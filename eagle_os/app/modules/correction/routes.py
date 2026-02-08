from __future__ import annotations

import random
from datetime import datetime, timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.academic import Project, UserProject
from app.models.user import User
from app.utils import system_notify
from app.modules.correction import correction_bp


@correction_bp.route("/slots")
@login_required
def slots():
    return render_template("dashboard/correction_slots.html")


@correction_bp.route("/assign")
@login_required
def assign():
    waiting = UserProject.query.filter_by(status="waiting_correction").all()
    random.shuffle(waiting)
    for record in waiting:
        validator = UserProject.query.filter_by(
            user_id=current_user.id,
            project_id=record.project_id,
            status="validated",
        ).first()
        if validator:
            return redirect(
                url_for("correction.evaluate", id=record.project_id, user_id=record.user_id)
            )
    flash("System Alert: No eligible corrections available.", "info")
    return redirect(url_for("correction.slots"))


@correction_bp.route("/evaluate/<int:id>", methods=["GET", "POST"])
@login_required
def evaluate(id: int):
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        abort(400, description="System Alert: Missing user_id.")

    record = UserProject.query.filter_by(user_id=user_id, project_id=id).first_or_404()
    project = Project.query.get_or_404(id)
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        grade = request.form.get("grade", type=int)
        feedback = request.form.get("feedback", "")
        if grade is None:
            abort(400, description="System Alert: Grade required.")

        record.final_mark = grade
        record.validated_at = datetime.utcnow()

        if grade < 50:
            record.status = "failed"
            user.xp = max(0, user.xp - 50)
            system_notify(user, "System Alert: Project failed. XP deducted.", "danger")
        elif grade >= 80:
            record.status = "validated"
            user.xp += project.xp_reward
            if user.black_hole_date:
                user.black_hole_date = user.black_hole_date + timedelta(days=project.tier)
            system_notify(user, "New Path Opened", "success")
        else:
            record.status = "waiting_correction"

        db.session.commit()
        flash("System Alert: Evaluation stored.", "success")
        return redirect(url_for("correction.slots"))

    return render_template(
        "dashboard/evaluate.html",
        record=record,
        project=project,
        user=user,
    )
