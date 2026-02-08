from __future__ import annotations

from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.academic import Project
from app.models.system import Notification
from app.models.user import User
from app.modules.admin import admin_bp


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403, description="System Alert: Admin access required.")
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/quests/new", methods=["GET", "POST"])
@login_required
@admin_required
def quests_new():
    if request.method == "POST":
        name = request.form.get("name", "")
        slug = request.form.get("slug", "")
        tier = request.form.get("tier", type=int, default=0)
        project = Project(name=name, slug=slug, tier=tier)
        db.session.add(project)
        db.session.commit()
        flash("System Alert: Project created.", "success")
        return redirect(url_for("admin.quests_new"))
    return render_template("admin/control_panel.html")


@admin_bp.route("/system/broadcast", methods=["POST"])
@login_required
@admin_required
def broadcast():
    message = request.form.get("message", "")
    title = request.form.get("title", "System Broadcast")
    if not message:
        abort(400, description="System Alert: Message required.")

    notifications = [
        Notification(user_id=user.id, title=title, message=message, type="system_command")
        for user in User.query.all()
    ]
    db.session.add_all(notifications)
    db.session.commit()
    flash("System Alert: Broadcast sent.", "success")
    return redirect(url_for("admin.users"))
