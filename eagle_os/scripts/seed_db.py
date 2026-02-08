from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.academic import Project, Skill  # noqa: E402
from app.models.user import Coalition, User  # noqa: E402


def seed() -> None:
    config_name = os.environ.get("FLASK_ENV", "development")
    app = create_app(config_name)
    with app.app_context():
        db.create_all()

        coalition = Coalition(name="Aquila", color="#00eaff", icon_url="", score=0)
        db.session.add(coalition)

        user = User(
            username="neo",
            email="neo@eagle.os",
            password_hash="dev",
            is_admin=True,
            black_hole_date=datetime.utcnow() + timedelta(days=100),
            coalition=coalition,
        )
        db.session.add(user)

        skill = Skill(name="Algorithms", slug="algorithms")
        db.session.add(skill)

        libft = Project(
            name="Libft",
            slug="libft",
            description="Core C library foundation",
            tier=0,
            xp_reward=200,
            estimated_hours=40,
            skills_points={"algo": 10, "sysadmin": 4},
            x_coord=120,
            y_coord=200,
        )
        get_next_line = Project(
            name="Get Next Line",
            slug="get_next_line",
            description="Buffered reader",
            tier=1,
            xp_reward=300,
            estimated_hours=50,
            skills_points={"algo": 6, "web": 2},
            x_coord=280,
            y_coord=220,
        )
        get_next_line.parent_projects.append(libft)
        libft.skills.append(skill)
        get_next_line.skills.append(skill)

        db.session.add_all([libft, get_next_line])
        db.session.commit()


if __name__ == "__main__":
    seed()
