from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)
api_bp = Blueprint("graph_api", __name__)

from eagle_os.app.modules.dashboard import routes, api  # noqa: E402,F401
