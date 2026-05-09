from . import db

from flask_login import UserMixin

from sqlalchemy.sql import func


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(150), unique=True)

    first_name = db.Column(db.String(150))

    last_name = db.Column(db.String(150))

    password = db.Column(db.String(300))

    otp_secret = db.Column(db.String(10))

    is_verified = db.Column(
        db.Boolean,
        default=False
    )


class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    content = db.Column(db.Text)

    created = db.Column(
        db.DateTime(timezone=True),
        default=func.now()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )