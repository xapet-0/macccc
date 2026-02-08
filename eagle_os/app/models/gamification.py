from __future__ import annotations

from app.extensions import db


user_achievements = db.Table(
    "user_achievements",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("achievement_id", db.Integer, db.ForeignKey("achievements.id"), primary_key=True),
)


class DailyLog(db.Model):
    __tablename__ = "daily_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    active_seconds = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="frozen")

    user = db.relationship("User", back_populates="logs")


class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_consumed = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", backref="inventory")


class ShopItem(db.Model):
    __tablename__ = "shop_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Integer, nullable=False, default=0)
    effect_type = db.Column(db.String(30), nullable=False)
    icon_url = db.Column(db.String(255))


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    xp_bonus = db.Column(db.Integer, nullable=False, default=0)
    icon = db.Column(db.String(255))

    users = db.relationship("User", secondary=user_achievements, back_populates="achievements")
