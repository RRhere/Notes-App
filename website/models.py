from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    otp_secret = db.Column(db.String(10))
    otp_created_at = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    notes = db.relationship(
        'Note',
        backref='author',
        lazy=True,
        cascade='all, delete-orphan',
    )


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
