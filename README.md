# Eagle OS (Gamified LMS)

## Overview
Eagle OS is a gamified learning management system inspired by 42 School and Solo Leveling, built as a modular Flask application with a cyberpunk HUD, a neural graph, and structured gamification layers.

## Repository Layout
- `eagle_os/` — source of truth for the Flask app, blueprints, models, and templates.
- `templates/` — legacy prototype templates kept for reference.

## Technical Documentation Tooling
### Line Count Snapshot
The current Python code footprint (excluding virtual environments and uploads) is:
- **Python files:** 24
- **Python lines:** 854

To regenerate this snapshot locally, run:
```bash
python - <<'PY'
from pathlib import Path
root = Path('.')
paths = [p for p in root.rglob('*.py') if 'venv' not in p.parts and 'uploads' not in p.parts]
lines = 0
for p in paths:
    try:
        lines += sum(1 for _ in p.open())
    except Exception:
        pass
print('python_files', len(paths))
print('python_lines', lines)
PY
```

## Current Known Issues
- **No Docker setup yet.** Containerization and deployment scripts are not present.
- **Missing dependency manifest.** A unified `requirements.txt` for `eagle_os/` has not been generated.
- **Legacy prototype folder.** `templates/` remains from the older prototype and should be cleaned once parity is confirmed.

## How to Run (Development)
1. Create a virtual environment and install dependencies.
2. Initialize the database:
   ```bash
   python eagle_os/scripts/seed_db.py
   ```
3. Start the app:
   ```bash
   python eagle_os/run.py
   ```
4. Visit the dashboard at `http://localhost:5000/`.

## How to Run the Shop
1. Ensure you have `ShopItem` records seeded (manual insertion or admin tooling).
2. Visit `http://localhost:5000/shop` to browse and buy items.
