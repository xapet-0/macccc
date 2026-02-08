from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from flask import jsonify
from flask_login import login_required, current_user

from app.models.academic import Project, UserProject
from app.models.gamification import DailyLog
from app.modules.dashboard import api_bp


def _user_project_map(user_id: int) -> Dict[int, UserProject]:
    records = UserProject.query.filter_by(user_id=user_id).all()
    return {record.project_id: record for record in records}


def _has_validated_parents(project: Project, user_map: Dict[int, UserProject]) -> bool:
    for parent in project.parent_projects:
        record = user_map.get(parent.id)
        if not record or record.status != "validated":
            return False
    return True


@api_bp.route("/api/neural-data", methods=["GET"])
@login_required
def neural_data():
    projects = Project.query.all()
    user_map = _user_project_map(current_user.id)

    today_log = DailyLog.query.filter_by(user_id=current_user.id, date=date.today()).first()
    active_seconds = today_log.active_seconds if today_log else 0

    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    for project in projects:
        user_project = user_map.get(project.id)
        if user_project and user_project.status == "validated":
            status = "completed"
        elif user_project and user_project.status == "subscribed":
            status = "burning" if active_seconds > 18000 else "available"
        else:
            status = "available" if _has_validated_parents(project, user_map) else "locked"

        nodes.append(
            {
                "id": project.id,
                "name": project.name,
                "tier": project.tier,
                "status": status,
                "type": "main",
            }
        )

        for parent in project.parent_projects:
            links.append({"source": parent.id, "target": project.id, "strength": 1})

    return jsonify({"nodes": nodes, "links": links})
