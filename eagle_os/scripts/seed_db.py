from __future__ import annotations

import os
from datetime import datetime, timedelta

from flask import Flask

from app.extensions import db
from app.models.academic import Project, Skill
from app.models.user import Coalition, User


def create_seed_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///eagle_os.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def seed():
    app = create_seed_app()
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
