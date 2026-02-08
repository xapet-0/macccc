from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from eagle_os.app.extensions import db
from eagle_os.app.models.academic import Project, UserProject
from eagle_os.app.models.user import User
from eagle_os.app.utils import FT_system_notify
from eagle_os.app.modules.correction import correction_bp
from eagle_os.app.utils import FT_get_default_user


@correction_bp.route("/slots")
def slots():
    return render_template("dashboard/correction_slots.html")


@correction_bp.route("/assign")
def assign():
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    waiting = UserProject.query.filter_by(status="waiting_correction").all()
    random.shuffle(waiting)
    for record in waiting:
        validator = UserProject.query.filter_by(
            user_id=user.id,
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
def evaluate(id: int):
    user = current_user if current_user.is_authenticated else FT_get_default_user()
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
        record.validated_at = datetime.now(timezone.utc)

        if grade < 50:
            record.status = "failed"
            user.xp = max(0, user.xp - 50)
            FT_system_notify(user, "System Alert: Project failed. XP deducted.", "danger")
        elif grade >= 80:
            record.status = "validated"
            user.xp += project.xp_reward
            if user.black_hole_date:
                user.black_hole_date = user.black_hole_date + timedelta(days=project.tier)
            FT_system_notify(user, "New Path Opened", "success")
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
