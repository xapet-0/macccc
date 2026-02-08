from __future__ import annotations

from app.extensions import db


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
