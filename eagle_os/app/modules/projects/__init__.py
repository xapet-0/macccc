from flask import Blueprint

projects_bp = Blueprint("projects", __name__)

from eagle_os.app.modules.projects import routes  # noqa: E402,F401
