from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from eagle_os.app.extensions import db
from eagle_os.app.modules.battle import battle_bp
from eagle_os.app.utils import FT_get_default_user


@battle_bp.route("/sudden-quest", methods=["GET", "POST"])
def sudden_quest():
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    if request.method == "POST":
        accepted = request.form.get("accept") == "yes"
        if not accepted:
            abort(403, description="System Alert: Acceptance required.")

        window_start = datetime.now(timezone.utc)
        user.mana = max(0, user.mana - 5)
        user.last_sudden_quest = window_start
        db.session.commit()
        flash("System Alert: Sudden Quest activated. Complete within 5 minutes.", "warning")
        return redirect(url_for("dashboard.index"))

    return render_template("dashboard/sudden_quest.html")


@battle_bp.route("/sudden-quest/verify", methods=["POST"])
def sudden_quest_verify():
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    timestamp = user.last_sudden_quest
    if not timestamp:
        abort(400, description="System Alert: No active quest.")

    if datetime.now(timezone.utc) - timestamp > timedelta(minutes=5):
        user.hp = max(0, user.hp - 10)
        db.session.commit()
        abort(403, description="System Alert: Verification timeout. Penalty applied.")

    proof = request.files.get("proof")
    if not proof:
        abort(400, description="System Alert: Proof required.")

    user.wallet += 10
    db.session.commit()
    flash("System Alert: Sudden Quest verified.", "success")
    return redirect(url_for("dashboard.index"))
