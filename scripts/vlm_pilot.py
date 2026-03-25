"""VLM 파일럿 — Claude Vision으로 런웨이 룩 이미지 라벨링.

runway_looks 이미지를 Claude Vision Sonnet으로 분석하여 vlm_labels 테이블에 저장.

Usage:
    # 테스트 (5장)
    python scripts/vlm_pilot.py --limit 5 --dry-run

    # 파일럿 실행 (100장)
    python scripts/vlm_pilot.py --limit 100

    # 특정 디자이너만
    python scripts/vlm_pilot.py --designer prada --limit 20

    # 특정 시즌만
    python scripts/vlm_pilot.py --season spring-summer-2026 --limit 50
"""
from __future__ import annotations

import argparse
import base64
import json
import sqlite3
import time
from io import BytesIO
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

DB_PATH = Path(__file__).parent.parent / "backend" / "db" / "ftib.db"

VLM_PROMPT = """Analyze this fashion runway look image and classify the following attributes.
Respond ONLY in JSON format. Do not include any other text.

{
  "items": [
    {
      "item": "<bag|shoe|jacket|pants|skirt|dress|top|accessory|coat|hat|scarf>",
      "shape": "<round|square|structured|unstructured|asymmetric|geometric|organic>",
      "size": "<mini|small|medium|large|oversized>",
      "color": "<primary color name in English>",
      "texture": "<matte|glossy|textured|quilted|woven|smooth|distressed|embossed>"
    }
  ],
  "overall_silhouette": "<oversized|slim|wide|fitted|relaxed|structured|draped>",
  "dominant_colors": ["<color1>", "<color2>"],
  "key_materials": ["<material1>", "<material2>"]
}

Rules:
- List ALL visible clothing items and accessories in the "items" array
- Use only the enum values provided for each field
- For color, use standard English color names (black, white, navy, burgundy, beige, etc.)
- For key_materials, identify from: leather, denim, sheer, knit, wool, silk, linen, cotton, nylon, polyester, suede, velvet, satin, mesh, lace, tweed, corduroy, fleece, fur, faux fur
- Be precise and consistent"""

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024


def init_vlm_table(conn: sqlite3.Connection):
    """vlm_labels 테이블 생성."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vlm_labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL DEFAULT 'runway',
            source_id TEXT NOT NULL,
            items TEXT,
            overall_silhouette TEXT,
            dominant_colors TEXT,
            key_materials TEXT,
            raw_response TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_type, source_id)
        )
    """)
    conn.commit()


def get_unlabeled_looks(
    conn: sqlite3.Connection,
    limit: int = 100,
    designers: list[str] | None = None,
    seasons: list[str] | None = None,
) -> list[dict]:
    """라벨링 안 된 룩 목록 조회."""
    query = """
        SELECT rl.id, rl.designer, rl.season, rl.look_number, rl.image_url
        FROM runway_looks rl
        LEFT JOIN vlm_labels vl ON vl.source_type = 'runway' AND vl.source_id = rl.id
        WHERE vl.id IS NULL
    """
    params = []
    if designers:
        placeholders = ",".join("?" for _ in designers)
        query += f" AND rl.designer_slug IN ({placeholders})"
        params.extend(designers)
    if seasons:
        placeholders = ",".join("?" for _ in seasons)
        query += f" AND rl.season IN ({placeholders})"
        params.extend(seasons)
    query += " ORDER BY rl.designer, rl.season, rl.look_number LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    return [
        {"id": r[0], "designer": r[1], "season": r[2], "look_number": r[3], "image_url": r[4]}
        for r in rows
    ]


def fetch_image_base64(url: str) -> tuple[str, str] | None:
    """이미지 URL에서 base64 인코딩된 데이터 반환."""
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        content_type = resp.headers.get("content-type", "image/jpeg")
        if "jpeg" in content_type or "jpg" in content_type:
            media_type = "image/jpeg"
        elif "png" in content_type:
            media_type = "image/png"
        elif "webp" in content_type:
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"
        b64 = base64.standard_b64encode(resp.content).decode("utf-8")
        return b64, media_type
    except Exception as e:
        print(f"    Image fetch error: {e}")
        return None


def analyze_image(client, image_b64: str, media_type: str) -> dict | None:
    """Claude Vision으로 이미지 분석."""
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": VLM_PROMPT,
                        },
                    ],
                }
            ],
        )
        raw = message.content[0].text
        # JSON 파싱 (```json ... ``` 블록 처리)
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return {"parsed": json.loads(text), "raw": raw}
    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        return {"parsed": None, "raw": raw}
    except Exception as e:
        print(f"    API error: {e}")
        return None


def save_label(conn: sqlite3.Connection, source_id: str, result: dict, model: str):
    """분석 결과를 DB에 저장."""
    parsed = result.get("parsed") or {}
    items_json = json.dumps(parsed.get("items", []), ensure_ascii=False)
    silhouette = parsed.get("overall_silhouette", "")
    colors_json = json.dumps(parsed.get("dominant_colors", []), ensure_ascii=False)
    materials_json = json.dumps(parsed.get("key_materials", []), ensure_ascii=False)

    conn.execute(
        """INSERT OR REPLACE INTO vlm_labels
           (source_type, source_id, items, overall_silhouette, dominant_colors, key_materials, raw_response, model_used)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ("runway", source_id, items_json, silhouette, colors_json, materials_json, result.get("raw", ""), model),
    )
    conn.commit()


def main():
    import anthropic

    parser = argparse.ArgumentParser(description="VLM Pilot — Claude Vision runway labeling")
    parser.add_argument("--limit", type=int, default=100, help="Number of looks to process")
    parser.add_argument("--designers", nargs="+", default=None, help="Filter by designer slugs")
    parser.add_argument("--seasons", nargs="+", default=None, help="Filter by seasons")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    init_vlm_table(conn)

    looks = get_unlabeled_looks(conn, args.limit, args.designers, args.seasons)
    print(f"Found {len(looks)} unlabeled looks to process")

    if not looks:
        print("Nothing to do.")
        return

    if args.dry_run:
        for i, look in enumerate(looks[:10], 1):
            print(f"  [{i}] {look['designer']} | {look['season']} | Look #{look['look_number']}")
            print(f"       {look['image_url'][:80]}...")
        if len(looks) > 10:
            print(f"  ... and {len(looks) - 10} more")
        print(f"\nEstimated cost: ~${len(looks) * 0.01:.2f} (rough estimate)")
        return

    client = anthropic.Anthropic()
    success = 0
    errors = 0

    for i, look in enumerate(looks, 1):
        label = f"[{i}/{len(looks)}] {look['designer']} | {look['season']} | Look #{look['look_number']}"
        print(f"{label}")

        # 이미지 다운로드
        img = fetch_image_base64(look["image_url"])
        if not img:
            print(f"  -> SKIP (image fetch failed)")
            errors += 1
            continue

        b64, media_type = img

        # Claude Vision 분석
        result = analyze_image(client, b64, media_type)
        if not result:
            print(f"  -> SKIP (API error)")
            errors += 1
            continue

        parsed = result.get("parsed")
        if parsed:
            items_count = len(parsed.get("items", []))
            silhouette = parsed.get("overall_silhouette", "?")
            colors = parsed.get("dominant_colors", [])
            print(f"  -> {items_count} items | {silhouette} | {', '.join(colors)}")
        else:
            print(f"  -> JSON parse failed, raw saved")

        save_label(conn, look["id"], result, MODEL)
        success += 1

        # Rate limit (Sonnet: ~50 RPM for vision)
        if i < len(looks):
            time.sleep(1.5)

    conn.close()
    print(f"\n=== Done: {success} success, {errors} errors ===")


if __name__ == "__main__":
    main()
