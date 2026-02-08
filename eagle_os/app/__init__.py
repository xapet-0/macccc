from __future__ import annotations

from flask import Flask

from eagle_os.config import CONFIG_MAP
from eagle_os.app.extensions import bcrypt, db, login_manager, migrate
from eagle_os.app.modules.admin import admin_bp
from eagle_os.app.modules.correction import correction_bp
from eagle_os.app.modules.dashboard import api_bp, dashboard_bp
from eagle_os.app.modules.projects import projects_bp
from eagle_os.app.modules.battle import battle_bp
from eagle_os.app.modules.shop import shop_bp


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    config_class = CONFIG_MAP.get(config_name, CONFIG_MAP["development"])
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    if app.config.get("AUTO_CREATE_TABLES"):
        with app.app_context():
            db.create_all()

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(correction_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(battle_bp)
    app.register_blueprint(shop_bp)

    return app
