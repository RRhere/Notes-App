from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from .models import Note

from . import db

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])

@login_required
def home():

    if request.method == "POST":

        title = request.form.get("title")

        content = request.form.get("content")

        if len(title) < 1:

            flash("Title is too short", category="error")

        else:

            new_note = Note(
                title=title,
                content=content,
                user_id=current_user.id
            )

            db.session.add(new_note)

            db.session.commit()

            flash("Note added!", category="success")

    notes = Note.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "notes.html",
        user=current_user,
        notes=notes
    )


@views.route("/delete/<int:id>", methods=["POST"])

@login_required
def delete(id):

    note = Note.query.get(id)

    if note and note.user_id == current_user.id:

        db.session.delete(note)

        db.session.commit()

        flash("Note deleted", category="success")

    return redirect(url_for("views.home"))