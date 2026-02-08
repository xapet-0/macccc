from __future__ import annotations

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from eagle_os.app.extensions import db
from eagle_os.app.models.academic import Project, UserProject
from eagle_os.app.modules.projects import projects_bp
from eagle_os.app.utils import FT_get_default_user


def _project_unlocked(project: Project, user_id: int) -> bool:
    for parent in project.parent_projects:
        record = UserProject.query.filter_by(user_id=user_id, project_id=parent.id).first()
        if not record or record.status != "validated":
            return False
    return True


@projects_bp.route("/project/<slug>")
def project_detail(slug: str):
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    project = Project.query.filter_by(slug=slug).first_or_404()
    if not _project_unlocked(project, user.id):
        abort(403, description="System Alert: Access denied. Project locked.")
    return render_template("dashboard/project_detail.html", project=project, user=user)


@projects_bp.route("/subscribe/<slug>", methods=["POST"])
def subscribe(slug: str):
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    project = Project.query.filter_by(slug=slug).first_or_404()
    if not _project_unlocked(project, user.id):
        abort(403, description="System Alert: Prerequisites not validated.")

    record = UserProject.query.filter_by(user_id=user.id, project_id=project.id).first()
    if not record:
        record = UserProject(user_id=user.id, project_id=project.id, status="subscribed")
        db.session.add(record)
        db.session.commit()

    flash("System Alert: Subscription confirmed.", "success")
    return redirect(url_for("projects.project_detail", slug=slug))


@projects_bp.route("/submit/<slug>", methods=["POST"])
def submit(slug: str):
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    project = Project.query.filter_by(slug=slug).first_or_404()
    record = UserProject.query.filter_by(user_id=user.id, project_id=project.id).first()
    if not record or record.status not in {"subscribed", "failed"}:
        abort(403, description="System Alert: Submission not allowed.")

    submission = request.files.get("submission")
    if not submission:
        abort(400, description="System Alert: Submission file missing.")

    record.status = "waiting_correction"
    db.session.commit()

    flash("Submission Received. Awaiting system evaluation.", "info")
    return redirect(url_for("projects.project_detail", slug=slug))
