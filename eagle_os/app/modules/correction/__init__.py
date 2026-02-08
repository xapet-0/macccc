from flask import Blueprint

correction_bp = Blueprint("correction", __name__)

from eagle_os.app.modules.correction import routes  # noqa: E402,F401
