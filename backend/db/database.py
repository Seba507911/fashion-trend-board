"""DB 연결 및 초기화 모듈."""
import aiosqlite
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "ftib.db"

DDL = """
CREATE TABLE IF NOT EXISTS brands (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    name_kr     TEXT,
    brand_type  TEXT NOT NULL CHECK(brand_type IN ('own', 'competitor')),
    logo_url    TEXT,
    website_url TEXT,
    crawl_config TEXT,
    is_active   INTEGER DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seasons (
    id          TEXT PRIMARY KEY,
    year        INTEGER NOT NULL,
    season_code TEXT NOT NULL CHECK(season_code IN ('SS', 'FW', 'RS', 'PF', 'CR')),
    label       TEXT,
    start_date  DATE,
    end_date    DATE,
    is_current  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    name_kr     TEXT NOT NULL,
    parent_id   TEXT REFERENCES categories(id),
    sort_order  INTEGER DEFAULT 0,
    icon        TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id              TEXT PRIMARY KEY,
    brand_id        TEXT NOT NULL REFERENCES brands(id),
    season_id       TEXT REFERENCES seasons(id),
    category_id     TEXT REFERENCES categories(id),
    product_name    TEXT NOT NULL,
    product_name_kr TEXT,
    price           REAL,
    sale_price      REAL,
    currency        TEXT DEFAULT 'KRW',
    colors          TEXT,
    materials       TEXT,
    image_urls      TEXT,
    thumbnail_url   TEXT,
    product_url     TEXT,
    style_tags      TEXT,
    sizes           TEXT,
    fit_info        TEXT,
    description     TEXT,
    is_active       INTEGER DEFAULT 1,
    crawled_at      DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    signal_type     TEXT NOT NULL,
    signal_value    REAL NOT NULL,
    signal_date     DATE NOT NULL,
    metadata        TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    score_type      TEXT NOT NULL,
    score_value     REAL NOT NULL,
    score_date      DATE NOT NULL,
    season_id       TEXT REFERENCES seasons(id),
    components      TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    season_id       TEXT NOT NULL REFERENCES seasons(id),
    prediction_text TEXT NOT NULL,
    predicted_score REAL,
    actual_score    REAL,
    accuracy_note   TEXT,
    confidence      TEXT CHECK(confidence IN ('high', 'medium', 'low')),
    predicted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_at     DATETIME
);

CREATE TABLE IF NOT EXISTS runway_looks (
    id              TEXT PRIMARY KEY,
    designer        TEXT NOT NULL,
    designer_slug   TEXT NOT NULL,
    season          TEXT NOT NULL,
    season_label    TEXT,
    city            TEXT,
    look_number     INTEGER,
    image_url       TEXT NOT NULL,
    thumbnail_url   TEXT,
    source_url      TEXT,
    collection_type TEXT DEFAULT 'woman',
    tags            TEXT,
    crawled_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_runway_designer ON runway_looks(designer_slug);
CREATE INDEX IF NOT EXISTS idx_runway_season ON runway_looks(season);
CREATE INDEX IF NOT EXISTS idx_runway_designer_season ON runway_looks(designer_slug, season);

CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_products_season ON products(season_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_brand_season ON products(brand_id, season_id);
CREATE INDEX IF NOT EXISTS idx_products_brand_category ON products(brand_id, category_id);
CREATE INDEX IF NOT EXISTS idx_signals_target ON signals(target_type, target_id, signal_date);
CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date);
CREATE INDEX IF NOT EXISTS idx_scores_target ON scores(target_type, target_id, score_date);
CREATE INDEX IF NOT EXISTS idx_scores_season ON scores(season_id, score_type);
CREATE INDEX IF NOT EXISTS idx_predictions_season ON predictions(season_id);
"""

SEED_DATA = """
INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('asics', 'ASICS', '아식스', 'competitor', 'https://www.asics.com/kr/ko-kr/'),
('newbalance', 'New Balance', '뉴발란스', 'competitor', 'https://www.newbalance.co.kr/'),
('marithe', 'Marithe Francois Girbaud', '마리떼 프랑소와 저버', 'competitor', 'https://www.marithe.com/'),
('alo', 'ALO Yoga', '알로 요가', 'competitor', 'https://www.aloyoga.co.kr/');

INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('prada', 'Prada', '프라다', 'reference', 'https://www.prada.com/'),
('gucci', 'Gucci', '구찌', 'reference', 'https://www.gucci.com/'),
('lemaire', 'Lemaire', '르메르', 'reference', 'https://www.lemaire.fr/');

INSERT OR IGNORE INTO seasons (id, year, season_code, label, is_current) VALUES
('2025SS', 2025, 'SS', '2025 Spring/Summer', 0),
('2025FW', 2025, 'FW', '2025 Fall/Winter', 0),
('2026SS', 2026, 'SS', '2026 Spring/Summer', 1);

INSERT OR IGNORE INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('apparel', 'Apparel', '의류', NULL, 1),
('accessories', 'Accessories', '용품', NULL, 2),
('footwear', 'Footwear', '신발', NULL, 3),
('outer', 'Outer', '아우터', 'apparel', 1),
('top', 'Top', '상의', 'apparel', 2),
('bottom', 'Bottom', '하의', 'apparel', 3),
('dress', 'Dress', '원피스', 'apparel', 4),
('set', 'Set-up', '셋업', 'apparel', 5),
('bag', 'Bag', '가방', 'accessories', 1),
('hat', 'Hat/Cap', '모자', 'accessories', 2),
('scarf', 'Scarf/Muffler', '스카프/머플러', 'accessories', 3),
('etc_acc', 'Others', '기타용품', 'accessories', 4),
('sneakers', 'Sneakers', '스니커즈', 'footwear', 1),
('boots', 'Boots', '부츠', 'footwear', 2),
('sandals', 'Sandals', '샌들', 'footwear', 3),
('loafers', 'Loafers/Flats', '로퍼/플랫', 'footwear', 4);
"""


def init_db_sync():
    """동기 방식으로 DB 초기화 (스크립트용)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(DDL)
    conn.executescript(SEED_DATA)
    conn.commit()
    conn.close()
    return DB_PATH


async def get_db() -> aiosqlite.Connection:
    """FastAPI 의존성 주입용 DB 커넥션."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
