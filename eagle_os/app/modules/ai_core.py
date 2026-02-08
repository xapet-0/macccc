from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Dict, List

import os

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None

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
        return {
            "peak_performance_day": peak_label,
            "weakness": weakness,
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
        if failing_count >= 2:
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


class AICodeReviewer:
    def __init__(self) -> None:
        self._api_key = os.environ.get("OPENAI_API_KEY")
        self._client = OpenAI(api_key=self._api_key) if OpenAI and self._api_key else None

    def review_code(self, file_content: str, language: str) -> Dict[str, object]:
        if not self._client:
            return self._mock_review(file_content, language)

        system_prompt = (
            "You are a strict code reviewer for a computer science school. "
            "Analyze for bugs, memory leaks, and style violations. Grade from 0 to 100."
        )
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Language: {language}\n"
                        f"Code:\n{file_content}\n"
                        "Return JSON with keys: grade (int), feedback (str), bugs (list of strings)."
                    ),
                },
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return self._safe_parse(content)

    def _mock_review(self, file_content: str, language: str) -> Dict[str, object]:
        del file_content, language
        return {
            "grade": 70,
            "feedback": "Mock review: Provide code for full analysis.",
            "bugs": [],
        }

    def _safe_parse(self, content: str) -> Dict[str, object]:
        try:
            import json

            parsed = json.loads(content)
            return {
                "grade": int(parsed.get("grade", 0)),
                "feedback": str(parsed.get("feedback", "")),
                "bugs": list(parsed.get("bugs", [])),
            }
        except Exception:
            return {
                "grade": 0,
                "feedback": "Failed to parse model response.",
                "bugs": ["Invalid JSON response"],
            }
