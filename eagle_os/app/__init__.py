from __future__ import annotations

from flask import Flask

from eagle_os.config import CONFIG_MAP
from app.extensions import bcrypt, db, login_manager, migrate
from app.modules.admin import admin_bp
from app.modules.correction import correction_bp
from app.modules.dashboard import api_bp, dashboard_bp
from app.modules.projects import projects_bp
from app.modules.battle import battle_bp
from app.modules.shop import shop_bp


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    config_class = CONFIG_MAP.get(config_name, CONFIG_MAP["development"])
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(correction_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(battle_bp)
    app.register_blueprint(shop_bp)

    login_manager.login_view = "auth.login"

    return app
