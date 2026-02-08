from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict

from flask import flash

from app.extensions import db
from app.models.gamification import DailyLog
from app.models.system import Notification
from app.models.user import User


def check_black_hole(user: User) -> bool:
    if user.black_hole_date and datetime.utcnow() > user.black_hole_date:
        user.is_frozen = True
        db.session.commit()
        return True
    return False


def calculate_heatmap(user_id: int) -> Dict[str, str]:
    today = date.today()
    start_date = today - timedelta(days=364)
    logs = (
        DailyLog.query.filter(
            DailyLog.user_id == user_id,
            DailyLog.date >= start_date,
        )
        .order_by(DailyLog.date.asc())
        .all()
    )
    log_map = {log.date: log.status for log in logs}
    output: Dict[str, str] = {}
    for offset in range(365):
        current_day = start_date + timedelta(days=offset)
        output[current_day.isoformat()] = log_map.get(current_day, "frozen")
    return output


def system_notify(user: User, message: str, type: str = "info") -> Notification:
    notification = Notification(user_id=user.id, title="System Alert", message=message, type=type)
    db.session.add(notification)
    db.session.commit()
    flash(message, type)
    return notification
