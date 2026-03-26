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
('alo', 'ALO Yoga', '알로 요가', 'competitor', 'https://www.aloyoga.co.kr/'),
('coor', 'Coor', '쿠어', 'competitor', 'https://coor.kr/'),
('blankroom', 'Blankroom', '블랭크룸', 'competitor', 'https://blankroom.co.kr/'),
('youth', 'Youth', '유스', 'competitor', 'https://youth-lab.kr/'),
('northface', 'The North Face Korea', '노스페이스코리아', 'competitor', 'https://www.thenorthfacekorea.co.kr/'),
('descente', 'Descente Korea', '데상트코리아', 'competitor', 'https://dk-on.com/DESCENTE'),
('nike', 'Nike', '나이키', 'competitor', 'https://www.nike.com/kr'),
('kolonsport', 'Kolon Sport', '코오롱스포츠', 'competitor', 'https://www.kolonsport.com');

INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('prada', 'Prada', '프라다', 'reference', 'https://www.prada.com/'),
('gucci', 'Gucci', '구찌', 'reference', 'https://www.gucci.com/'),
('lemaire', 'Lemaire', '르메르', 'reference', 'https://www.lemaire.fr/');

INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('zara', 'ZARA', '자라', 'competitor', 'https://www.zara.com/kr/'),
('cos', 'COS', '코스', 'competitor', 'https://www.cos.com/kr/'),
('hm', 'H&M', '에이치앤엠', 'competitor', 'https://www2.hm.com/ko_kr/'),
('on_running', 'On Running', '온러닝', 'competitor', 'https://www.on.com/ko-kr/'),
('hoka', 'HOKA', '호카', 'competitor', 'https://www.hoka.com/ko/kr/'),
('lululemon', 'Lululemon', '룰루레몬', 'competitor', 'https://www.lululemon.co.kr/'),
('k2', 'K2', '케이투', 'competitor', 'https://www.k2.co.kr/'),
('blackyak', 'Black Yak', '블랙야크', 'competitor', 'https://www.blackyak.com/'),
('fila', 'FILA Korea', '필라코리아', 'competitor', 'https://www.fila.co.kr/'),
('ralph_lauren', 'Ralph Lauren', '랄프로렌', 'competitor', 'https://www.ralphlauren.co.kr/'),
('mardi', 'Mardi Mercredi', '마르디 메크르디', 'competitor', 'https://www.mardimercredi.com/'),
('stussy', 'Stüssy', '스투시', 'competitor', 'https://www.stussy.com/'),
('maison_kitsune', 'Maison Kitsuné', '메종키츠네', 'competitor', 'https://www.maisonkitsune.com/'),
('dunst', 'DUNST', '던스트', 'competitor', 'https://dunst.co.kr/'),
('jacquemus', 'Jacquemus', '자크뮈스', 'competitor', 'https://www.jacquemus.com/'),
('ami', 'Ami Paris', '아미파리스', 'competitor', 'https://www.amiparis.com/'),
('emis', 'EMIS', '이미스', 'competitor', 'https://emis.kr/'),
('thisisneverthat', 'thisisneverthat', '디스이즈네버댓', 'competitor', 'https://www.thisisneverthat.com/'),
('acne_studios', 'Acne Studios', '아크네스튜디오', 'competitor', 'https://www.acnestudios.com/kr/'),
('wooyoungmi', 'WOOYOUNGMI', '우영미', 'competitor', 'https://www.wooyoungmi.com/'),
('ader_error', 'ADER error', '아더에러', 'competitor', 'https://www.adererror.com/'),
('salomon', 'Salomon', '살로몬', 'competitor', 'https://www.salomon.com/ko-kr/'),
('carhartt_wip', 'Carhartt WIP', '칼하트WIP', 'competitor', 'https://www.carhartt-wip.com/'),
('amomento', 'AMOMENTO', '아모멘토', 'competitor', 'https://www.amfrfr.com/'),
('recto', 'RECTO', '렉토', 'competitor', 'https://rfrfrfr.com/');

INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('uniqlo', 'UNIQLO', '유니클로', 'competitor', 'https://www.uniqlo.com/kr/ko/'),
('newera', 'New Era', '뉴에라', 'competitor', 'https://www.neweracap.co.kr/'),
('kangol', 'Kangol', '캉골', 'competitor', 'https://kangol.kr/'),
('snowpeak', 'Snow Peak', '스노우피크', 'competitor', 'https://www.snowpeak.co.kr/'),
('nanamica', 'nanamica', '나나미카', 'competitor', 'https://www.nanamica.com/'),
('captain_sunshine', 'CAPTAIN SUNSHINE', '캡틴선샤인', 'competitor', 'https://captain-sunshine.com/'),
('comoli', 'COMOLI', '코모리', 'competitor', 'https://www.comoli.jp/'),
('danton', 'DANTON', '단톤', 'competitor', 'https://www.danton-japan.com/'),
('auralee', 'AURALEE', '오라리', 'competitor', 'https://www.auralee.jp/'),
('apresse', 'A.PRESSE', '아프레쎄', 'competitor', 'https://apresse.jp/'),
('visvim', 'visvim', '비즈빔', 'competitor', 'https://www.visvim.tv/'),
('kapital', 'KAPITAL', '캐피탈', 'competitor', 'https://www.kapital.jp/');

INSERT OR IGNORE INTO brands (id, name, name_kr, brand_type, website_url) VALUES
('bode', 'BODE', '보데', 'competitor', 'https://www.bodenewyork.com/'),
('skims', 'SKIMS', '스킴스', 'competitor', 'https://skims.com/'),
('supreme', 'Supreme', '슈프림', 'competitor', 'https://www.supremenewyork.com/'),
('rrl', 'RRL', 'RRL', 'competitor', 'https://www.ralphlauren.co.kr/ko/rrl/10060'),
('palace', 'Palace', '팰리스', 'competitor', 'https://www.palaceskateboards.com/'),
('goldwin', 'Goldwin', '골드윈', 'competitor', 'https://www.goldwin.co.jp/'),
('covernat', 'COVERNAT', '커버낫', 'competitor', 'https://covernat.net/');

INSERT OR IGNORE INTO seasons (id, year, season_code, label, is_current) VALUES
('2025SS', 2025, 'SS', '2025 Spring/Summer', 0),
('2025FW', 2025, 'FW', '2025 Fall/Winter', 0),
('2026SS', 2026, 'SS', '2026 Spring/Summer', 1);

-- 대분류
INSERT OR IGNORE INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('wear', 'Wear', '의류', NULL, 1),
('accessory', 'Accessory', '용품', NULL, 2);

-- 의류 중분류
INSERT OR IGNORE INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('outer', 'Outer', '아우터', 'wear', 1),
('inner', 'Inner', '상의', 'wear', 2),
('bottom', 'Bottom', '하의', 'wear', 3),
('wear_etc', 'Wear Etc', '기타의류', 'wear', 4);

-- 용품 중분류
INSERT OR IGNORE INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('headwear', 'Headwear', '모자', 'accessory', 1),
('bag', 'Bag', '가방', 'accessory', 2),
('shoes', 'Shoes', '신발', 'accessory', 3),
('acc_etc', 'Acc Etc', '기타용품', 'accessory', 4);

-- Legacy aliases (keep for backward compat)
INSERT OR IGNORE INTO categories (id, name, name_kr, parent_id, sort_order) VALUES
('top', 'Top', '상의', 'wear', 2),
('dress', 'Dress', '원피스/드레스', 'wear', 4),
('accessories', 'Accessories', '기타용품', 'accessory', 4);
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
