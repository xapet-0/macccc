from __future__ import annotations

from datetime import datetime, timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.battle import battle_bp


@battle_bp.route("/sudden-quest", methods=["GET", "POST"])
@login_required
def sudden_quest():
    if request.method == "POST":
        accepted = request.form.get("accept") == "yes"
        if not accepted:
            abort(403, description="System Alert: Acceptance required.")

        window_start = datetime.utcnow()
        current_user.mana = max(0, current_user.mana - 5)
        current_user.last_sudden_quest = window_start  # type: ignore[attr-defined]
        db.session.commit()
        flash("System Alert: Sudden Quest activated. Complete within 5 minutes.", "warning")
        return redirect(url_for("dashboard.index"))

    return render_template("dashboard/sudden_quest.html")


@battle_bp.route("/sudden-quest/verify", methods=["POST"])
@login_required
def sudden_quest_verify():
    timestamp = getattr(current_user, "last_sudden_quest", None)
    if not timestamp:
        abort(400, description="System Alert: No active quest.")

    if datetime.utcnow() - timestamp > timedelta(minutes=5):
        current_user.hp = max(0, current_user.hp - 10)
        db.session.commit()
        abort(403, description="System Alert: Verification timeout. Penalty applied.")

    proof = request.files.get("proof")
    if not proof:
        abort(400, description="System Alert: Proof required.")

    current_user.wallet += 10
    db.session.commit()
    flash("System Alert: Sudden Quest verified.", "success")
    return redirect(url_for("dashboard.index"))
