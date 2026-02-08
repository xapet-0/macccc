# Shadow OS Architecture

## Overview
Shadow OS is a modular Flask application structured as a package-first monolith. It uses Blueprints to partition domain logic and SQLAlchemy models to define the domain schema.

## Core Layers
- **App Factory:** `eagle_os/app/__init__.py` creates the Flask app, wires extensions, and registers blueprints.
- **Extensions:** `eagle_os/app/extensions.py` holds shared instances of SQLAlchemy, Migrate, LoginManager, and Bcrypt.
- **Models:** `eagle_os/app/models/` contains all domain entities (users, projects, gamification, system notifications).
- **Modules:** `eagle_os/app/modules/` holds blueprints grouped by domain (dashboard, projects, correction, shop, admin, battle).
- **UI Layer:** `eagle_os/app/templates/` and `eagle_os/app/static/` provide the HUD, radar chart, and neural graph visuals.

## Request Flow
1. **App Factory** initializes extensions and loads configuration.
2. **Blueprint Routes** handle requests and assemble data.
3. **Models** represent persistent state and relationships.
4. **Templates/JS** render the UI and visualizations.

## Naming Convention
All newly added helper functions in the infrastructure layer use the `FT_` prefix to make shared utilities explicit and searchable.

## Directory Map
```
/eagle_os
  /app
    __init__.py
    extensions.py
    utils.py
    /models
    /modules
    /static
    /templates
  config.py
  run.py
  scripts/
```

## Default User Policy
Authentication is disabled by default. A fallback codename user (`المحارب المجهول` / "Solo Leveling") is created on demand so the system can boot without login friction.
