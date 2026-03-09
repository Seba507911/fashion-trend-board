"""DB 초기화 스크립트."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.database import init_db_sync

if __name__ == "__main__":
    db_path = init_db_sync()
    print(f"DB initialized at {db_path}")
