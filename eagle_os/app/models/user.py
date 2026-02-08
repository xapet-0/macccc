from __future__ import annotations

import math
from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class Coalition(db.Model):
    __tablename__ = "coalitions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    color = db.Column(db.String(7), nullable=False)
    icon_url = db.Column(db.String(255))
    score = db.Column(db.Integer, nullable=False, default=0)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    level = db.Column(db.Float, nullable=False, default=1.0)
    xp = db.Column(db.Integer, nullable=False, default=0)
    wallet = db.Column(db.Integer, nullable=False, default=0)
    correction_points = db.Column(db.Integer, nullable=False, default=5)

    hp = db.Column(db.Integer, nullable=False, default=100)
    mana = db.Column(db.Integer, nullable=False, default=100)
    black_hole_date = db.Column(db.DateTime)
    is_frozen = db.Column(db.Boolean, nullable=False, default=False)
    last_sudden_quest = db.Column(db.DateTime)

    coalition_id = db.Column(db.Integer, db.ForeignKey("coalitions.id"))
    coalition = db.relationship("Coalition", backref="members")

    projects = db.relationship("UserProject", back_populates="user", lazy="dynamic")
    logs = db.relationship("DailyLog", back_populates="user", lazy="dynamic")

    def calculate_level(self) -> float:
        return round(max(1.0, math.sqrt(self.xp) * 0.1), 2)

    def time_until_blackhole(self) -> int:
        if not self.black_hole_date:
            return 0
        delta = self.black_hole_date - datetime.utcnow()
        return max(0, delta.days)
