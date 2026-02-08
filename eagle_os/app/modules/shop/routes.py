from __future__ import annotations

from datetime import timedelta

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.gamification import ShopItem
from app.modules.shop import shop_bp


@shop_bp.route("/")
@login_required
def index():
    items = ShopItem.query.all()
    return render_template("shop/index.html", items=items)


@shop_bp.route("/buy/<int:item_id>", methods=["POST"])
@login_required
def buy(item_id: int):
    item = ShopItem.query.get_or_404(item_id)
    balance = current_user.currency_balance
    if balance < item.cost:
        abort(403, description="System Alert: Insufficient funds.")

    if item.effect_type == "buy_xp":
        abort(403, description="System Alert: This purchase is restricted.")

    current_user.currency_balance -= item.cost
    if item.effect_type == "freeze_blackhole" and current_user.black_hole_date:
        current_user.black_hole_date = current_user.black_hole_date + timedelta(days=5)

    db.session.commit()
    flash("System Alert: Purchase successful.", "success")
    return redirect(url_for("shop.index"))
