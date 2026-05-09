import logging

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from . import db
from .models import Note

views = Blueprint("views", __name__)
logger = logging.getLogger(__name__)


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_notes():
    """Return all notes for the current user, newest first."""
    try:
        return (
            Note.query
            .filter_by(user_id=current_user.id)
            .order_by(Note.created.desc())
            .all()
        )
    except Exception as e:
        logger.error(f"Error fetching notes for user {current_user.id}: {e}")
        return []


def _is_ajax():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


# ============================================
# VIEWS ROUTES
# ============================================

@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    try:
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()

            if not title:
                if _is_ajax():
                    return jsonify({'status': 'error', 'message': 'Please enter a note title'}), 400
                flash("Please enter a note title", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())

            if len(title) > 200:
                if _is_ajax():
                    return jsonify({'status': 'error', 'message': 'Title must not exceed 200 characters'}), 400
                flash("Title must not exceed 200 characters", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())

            if len(content) > 10000:
                if _is_ajax():
                    return jsonify({'status': 'error', 'message': 'Note content must not exceed 10,000 characters'}), 400
                flash("Note content must not exceed 10,000 characters", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())

            try:
                new_note = Note(title=title, content=content, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                logger.info(f"Note {new_note.id} created by user {current_user.id}")

                if _is_ajax():
                    return jsonify({
                        'status': 'success',
                        'message': 'Note created successfully!',
                        'note': {
                            'id': new_note.id,
                            'title': new_note.title,
                            'content': new_note.content,
                            'created': new_note.created.strftime('%Y-%m-%d %H:%M:%S'),
                        },
                    })

                # BUG FIX: POST → Redirect → GET so that browser refresh does
                # not resubmit the form and create a duplicate note.
                flash("Note created successfully!", category="success")
                return redirect(url_for('views.home'))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating note for user {current_user.id}: {e}")
                if _is_ajax():
                    return jsonify({'status': 'error', 'message': 'Failed to create note. Please try again.'}), 500
                flash("Failed to create note. Please try again.", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())

        notes = get_user_notes()
        return render_template("home.html", user=current_user, notes=notes)

    except Exception as e:
        logger.error(f"Error loading home page for user {current_user.id}: {e}")
        flash("An error occurred. Please try again.", category="error")
        return render_template("home.html", user=current_user, notes=[])


@views.route("/delete/<int:note_id>", methods=["POST"])
@login_required
def delete(note_id):
    try:
        # BUG FIX: db.session.get() replaces the deprecated Note.query.get()
        note = db.session.get(Note, note_id)

        if not note:
            logger.warning(f"Delete attempt for missing note {note_id} by user {current_user.id}")
            if _is_ajax():
                return jsonify({'status': 'error', 'message': 'Note not found'}), 404
            flash("Note not found", category="error")
            return redirect(url_for("views.home"))

        if note.user_id != current_user.id:
            logger.warning(f"Unauthorised delete of note {note_id} by user {current_user.id}")
            if _is_ajax():
                return jsonify({'status': 'error', 'message': 'Unauthorised'}), 403
            flash("Unauthorised action", category="error")
            return redirect(url_for("views.home"))

        try:
            db.session.delete(note)
            db.session.commit()
            logger.info(f"Note {note_id} deleted by user {current_user.id}")

            if _is_ajax():
                return jsonify({'status': 'success', 'message': 'Note deleted successfully'})

            flash("Note deleted successfully", category="success")
            return redirect(url_for("views.home"))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting note {note_id}: {e}")
            if _is_ajax():
                return jsonify({'status': 'error', 'message': 'Failed to delete note'}), 500
            flash("Failed to delete note. Please try again.", category="error")
            return redirect(url_for("views.home"))

    except Exception as e:
        logger.error(f"Unexpected error during delete: {e}")
        if _is_ajax():
            return jsonify({'status': 'error', 'message': 'An error occurred'}), 500
        flash("An error occurred. Please try again.", category="error")
        return redirect(url_for("views.home"))


@views.route("/api/notes", methods=["GET"])
@login_required
def get_notes_api():
    try:
        notes = (
            Note.query
            .filter_by(user_id=current_user.id)
            .order_by(Note.created.desc())
            .all()
        )
        return jsonify({
            'status': 'success',
            'notes': [{
                'id': n.id,
                'title': n.title,
                'content': n.content,
                'created': n.created.strftime('%Y-%m-%d %H:%M:%S'),
            } for n in notes],
        })
    except Exception as e:
        logger.error(f"Error fetching notes for user {current_user.id}: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch notes'}), 500
