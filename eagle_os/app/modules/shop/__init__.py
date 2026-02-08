from flask import Blueprint

shop_bp = Blueprint("shop", __name__, url_prefix="/shop")

from eagle_os.app.modules.shop import routes  # noqa: E402,F401
