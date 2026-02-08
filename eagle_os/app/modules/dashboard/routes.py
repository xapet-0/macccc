from __future__ import annotations

from flask import render_template
from flask_login import login_required, current_user

from app.models.user import Coalition
from app.utils import check_black_hole, calculate_heatmap
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
    return render_template(
        "dashboard/index.html",
        user=current_user,
        coalition=coalition,
        heatmap_data=heatmap_data,
    )
