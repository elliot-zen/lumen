from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api/src"))
sys.path.insert(0, str(ROOT / "packages/domain/src"))
sys.path.insert(0, str(ROOT / "packages/notes-platform/src"))

import uvicorn


def main() -> None:
    uvicorn.run(
        "lumen_api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
