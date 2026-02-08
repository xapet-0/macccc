from __future__ import annotations

from flask import render_template
from flask_login import login_required, current_user

from app.models.user import Coalition
from app.utils import check_black_hole, calculate_heatmap
from app.models.academic import Project, UserProject
from app.modules.dashboard import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    if check_black_hole(current_user):
        return render_template("dashboard/game_over.html")

    coalition = None
    if current_user.coalition_id:
        coalition = Coalition.query.get(current_user.coalition_id)

    heatmap_data = calculate_heatmap(current_user.id)
    skill_radar = build_skill_radar(current_user.id)
    return render_template(
        "dashboard/index.html",
        user=current_user,
        coalition=coalition,
        heatmap_data=heatmap_data,
        skill_radar=skill_radar,
    )


def build_skill_radar(user_id: int) -> dict[str, int]:
    totals = {"Algorithms": 0, "Graphics": 0, "SysAdmin": 0, "Web": 0}
    records = UserProject.query.filter_by(user_id=user_id, status="validated").all()
    project_ids = [record.project_id for record in records]
    if not project_ids:
        return totals

    projects = Project.query.filter(Project.id.in_(project_ids)).all()
    mapping = {
        "algo": "Algorithms",
        "graphics": "Graphics",
        "sysadmin": "SysAdmin",
        "web": "Web",
    }
    for project in projects:
        skills_points = project.skills_points or {}
        for key, value in skills_points.items():
            label = mapping.get(key, key)
            if label in totals:
                totals[label] += int(value)
    return totals
    )
