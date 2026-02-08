from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Dict, List

from app.models.academic import Project, UserProject
from app.models.gamification import DailyLog
from app.models.user import User
from app.utils import system_notify


class EagleAgent:
    def analyze_patterns(self, user_id: int) -> Dict[str, str]:
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        logs = (
            DailyLog.query.filter(
                DailyLog.user_id == user_id,
                DailyLog.date >= start_date,
            )
            .order_by(DailyLog.date.asc())
            .all()
        )

        peak_days: List[str] = [log.date.strftime("%A") for log in logs if log.active_seconds > 7200]
        peak_day = Counter(peak_days).most_common(1)
        peak_label = peak_day[0][0] if peak_day else "Unknown"

        failures = (
            UserProject.query.filter(
                UserProject.user_id == user_id,
                UserProject.status == "failed",
            )
            .count()
        )
        weakness = "Resilience" if failures == 0 else "Consistency"

        momentum = self._momentum_score(user_id)

        return {
            "peak_performance_day": peak_label,
            "weakness": weakness,
            "momentum": f\"{momentum:.2f}\",
        }

    def recommend_next_step(self, user_id: int) -> Dict[str, str]:
        user = User.query.get(user_id)
        if not user:
            return {"status": "offline", "message": "User not found"}

        available_projects = (
            Project.query.outerjoin(UserProject)
            .filter(
                (UserProject.user_id == user_id) | (UserProject.user_id.is_(None)),
            )
            .all()
        )

        failing_count = (
            UserProject.query.filter(
                UserProject.user_id == user_id,
                UserProject.status == "failed",
            )
            .count()
        )

        momentum = self._momentum_score(user_id)
        if failing_count >= 2 or momentum < 2.0:
            system_notify(user, "System Assist: Try a lower tier project to stabilize progress.", "warning")
            candidate = min(available_projects, key=lambda project: project.tier, default=None)
        else:
            candidate = min(available_projects, key=lambda project: project.tier, default=None)

        if not candidate:
            return {"status": "idle", "message": "No projects available"}

        return {
            "status": "recommended",
            "project": candidate.name,
            "slug": candidate.slug,
        }

    def _momentum_score(self, user_id: int) -> float:
        streak_days = (
            DailyLog.query.filter(DailyLog.user_id == user_id, DailyLog.status != "frozen")
            .count()
        )
        total_hours = (
            DailyLog.query.with_entities(DailyLog.active_seconds)
            .filter(DailyLog.user_id == user_id)
            .all()
        )
        total_seconds = sum(item[0] for item in total_hours)
        failures = (
            UserProject.query.filter(
                UserProject.user_id == user_id,
                UserProject.status == "failed",
            )
            .count()
        )
        fail_rate = failures / max(1, failures + 5)
        return (streak_days ** 1.2) * (1 + total_seconds / 3600) * (1 - fail_rate)
