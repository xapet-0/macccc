from __future__ import annotations

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.academic import Project, UserProject
from app.modules.projects import projects_bp


def _project_unlocked(project: Project) -> bool:
    for parent in project.parent_projects:
        record = UserProject.query.filter_by(user_id=current_user.id, project_id=parent.id).first()
        if not record or record.status != "validated":
            return False
    return True


@projects_bp.route("/project/<slug>")
@login_required
def project_detail(slug: str):
    project = Project.query.filter_by(slug=slug).first_or_404()
    if not _project_unlocked(project):
        abort(403, description="System Alert: Access denied. Project locked.")
    return render_template("dashboard/project_detail.html", project=project)


@projects_bp.route("/subscribe/<slug>", methods=["POST"])
@login_required
def subscribe(slug: str):
    project = Project.query.filter_by(slug=slug).first_or_404()
    if not _project_unlocked(project):
        abort(403, description="System Alert: Prerequisites not validated.")

    record = UserProject.query.filter_by(user_id=current_user.id, project_id=project.id).first()
    if not record:
        record = UserProject(user_id=current_user.id, project_id=project.id, status="subscribed")
        db.session.add(record)
        db.session.commit()

    flash("System Alert: Subscription confirmed.", "success")
    return redirect(url_for("projects.project_detail", slug=slug))


@projects_bp.route("/submit/<slug>", methods=["POST"])
@login_required
def submit(slug: str):
    project = Project.query.filter_by(slug=slug).first_or_404()
    record = UserProject.query.filter_by(user_id=current_user.id, project_id=project.id).first()
    if not record or record.status not in {"subscribed", "failed"}:
        abort(403, description="System Alert: Submission not allowed.")

    submission = request.files.get("submission")
    if not submission:
        abort(400, description="System Alert: Submission file missing.")

    record.status = "waiting_correction"
    db.session.commit()

    flash("Submission Received. Awaiting system evaluation.", "info")
    return redirect(url_for("projects.project_detail", slug=slug))
