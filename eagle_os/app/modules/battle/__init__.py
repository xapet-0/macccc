from flask import Blueprint

battle_bp = Blueprint("battle", __name__, url_prefix="/battle")

from eagle_os.app.modules.battle import battle_routes  # noqa: E402,F401
