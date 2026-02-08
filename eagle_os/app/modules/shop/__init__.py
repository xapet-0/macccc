from flask import Blueprint

shop_bp = Blueprint("shop", __name__, url_prefix="/shop")

from app.modules.shop import routes  # noqa: E402,F401
