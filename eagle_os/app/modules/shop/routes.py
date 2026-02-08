from __future__ import annotations

from datetime import timedelta

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user

from eagle_os.app.extensions import db
from eagle_os.app.models.gamification import ShopItem
from eagle_os.app.modules.shop import shop_bp
from eagle_os.app.utils import FT_get_default_user


@shop_bp.route("/")
def index():
    items = ShopItem.query.all()
    return render_template("shop/index.html", items=items)


@shop_bp.route("/buy/<int:item_id>", methods=["POST"])
def buy(item_id: int):
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    item = ShopItem.query.get_or_404(item_id)
    balance = user.currency_balance
    if balance < item.cost:
        abort(403, description="System Alert: Insufficient funds.")

    if item.effect_type == "buy_xp":
        abort(403, description="System Alert: This purchase is restricted.")

    user.currency_balance -= item.cost
    if item.effect_type == "freeze_blackhole" and user.black_hole_date:
        user.black_hole_date = user.black_hole_date + timedelta(days=5)

    db.session.commit()
    flash("System Alert: Purchase successful.", "success")
    return redirect(url_for("shop.index"))
