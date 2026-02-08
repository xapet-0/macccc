from __future__ import annotations

from app.extensions import db


project_skills = db.Table(
    "project_skills",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id"), primary_key=True),
)

project_dependencies = db.Table(
    "project_dependencies",
    db.Column("parent_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
    db.Column("child_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
)


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    pdf_url = db.Column(db.String(255))

    tier = db.Column(db.Integer, nullable=False, default=0)
    xp_reward = db.Column(db.Integer, nullable=False, default=0)
    estimated_hours = db.Column(db.Integer, nullable=False, default=0)

    x_coord = db.Column(db.Integer, nullable=False, default=0)
    y_coord = db.Column(db.Integer, nullable=False, default=0)

    parent_projects = db.relationship(
        "Project",
        secondary=project_dependencies,
        primaryjoin=id == project_dependencies.c.child_id,
        secondaryjoin=id == project_dependencies.c.parent_id,
        backref="child_projects",
    )

    skills = db.relationship("Skill", secondary=project_skills, backref="projects")


class UserProject(db.Model):
    __tablename__ = "user_projects"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), primary_key=True)

    status = db.Column(db.String(30), nullable=False, default="subscribed")
    final_mark = db.Column(db.Integer)
    validated_at = db.Column(db.DateTime)
    retries = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("User", back_populates="projects")
    project = db.relationship("Project", backref="user_projects")
