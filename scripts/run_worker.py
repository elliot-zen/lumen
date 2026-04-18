from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api/src"))
sys.path.insert(0, str(ROOT / "packages/domain/src"))
sys.path.insert(0, str(ROOT / "packages/notes-platform/src"))

from lumen_api.worker_main import run_worker_forever


if __name__ == "__main__":
    run_worker_forever()
