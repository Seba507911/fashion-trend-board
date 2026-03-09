"""Vercel Serverless Function — FastAPI 래퍼."""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.api.main import app  # noqa: E402
