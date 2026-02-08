from __future__ import annotations

from flask import render_template
from flask_login import current_user

from eagle_os.app.models.academic import Project, UserProject
from eagle_os.app.models.user import Coalition
from eagle_os.app.modules.dashboard import dashboard_bp
from eagle_os.app.utils import FT_calculate_heatmap, FT_check_black_hole, FT_get_default_user


@dashboard_bp.route("/")
def index():
    user = current_user if current_user.is_authenticated else FT_get_default_user()
    if FT_check_black_hole(user):
        return render_template("dashboard/game_over.html")

    coalition = None
    if user.coalition_id:
        coalition = Coalition.query.get(user.coalition_id)

    heatmap_data = FT_calculate_heatmap(user.id)
    skill_radar = build_skill_radar(user.id)
    return render_template(
        "dashboard/index.html",
        user=user,
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
