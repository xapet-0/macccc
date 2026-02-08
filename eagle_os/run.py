import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from eagle_os.app import create_app  # noqa: E402

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
