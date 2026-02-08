from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=1)
    xp = db.Column(db.Integer, nullable=False, default=0)
    hp = db.Column(db.Integer, nullable=False, default=100)
    mana = db.Column(db.Integer, nullable=False, default=100)
    rank = db.Column(db.String(10), nullable=False, default="E")
    wallet = db.Column(db.Integer, nullable=False, default=0)


class Quest(db.Model):
    __tablename__ = "quests"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    rank = db.Column(db.String(2), nullable=False, default="E")
    status = db.Column(db.String(20), nullable=False, default="LOCKED")
    xp_reward = db.Column(db.Integer, nullable=False, default=0)
    subject_file = db.Column(db.String(255))
    eval_script = db.Column(db.String(255))
    graph_x = db.Column(db.Integer, nullable=False, default=0)
    graph_y = db.Column(db.Integer, nullable=False, default=0)
    loot = db.relationship("Loot", backref="quest", uselist=False, cascade="all, delete-orphan")


class Loot(db.Model):
    __tablename__ = "loot"

    id = db.Column(db.Integer, primary_key=True)
    quest_id = db.Column(db.Integer, db.ForeignKey("quests.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255))
    is_locked = db.Column(db.Boolean, nullable=False, default=True)


class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, nullable=False, default=0)
    activity_type = db.Column(db.String(50), nullable=False)
