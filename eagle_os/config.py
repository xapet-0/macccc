import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "eagle-os-dev")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URI", "sqlite:///eagle_os.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLACK_HOLE_INITIAL_DAYS = int(os.environ.get("BLACK_HOLE_INITIAL_DAYS", 100))
    HEATMAP_THRESHOLDS = {
        "active": int(os.environ.get("HEATMAP_ACTIVE_THRESHOLD", 3600)),
        "burning": int(os.environ.get("HEATMAP_BURNING_THRESHOLD", 18000)),
    }
    AUTO_CREATE_TABLES = os.environ.get("AUTO_CREATE_TABLES", "true").lower() == "true"


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
