from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import logging
from datetime import datetime

views = Blueprint("views", __name__)
logger = logging.getLogger(__name__)

# ============================================
# VIEWS ROUTES
# ============================================

@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    """Handle home page with note creation"""
    try:
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            
            # Validate inputs
            if not title:
                flash("Please enter a note title", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())
            
            if len(title) > 200:
                flash("Title must not exceed 200 characters", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())
            
            if len(content) > 10000:
                flash("Note content must not exceed 10,000 characters", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())
            
            # Create new note
            try:
                new_note = Note(
                    title=title,
                    content=content,
                    user_id=current_user.id
                )
                db.session.add(new_note)
                db.session.commit()
                
                logger.info(f"Note created by user {current_user.id}: {new_note.id}")
                flash("Note created successfully!", category="success")
                
                # Return JSON for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'status': 'success',
                        'message': 'Note created successfully!',
                        'note': {
                            'id': new_note.id,
                            'title': new_note.title,
                            'content': new_note.content,
                            'created': new_note.created.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    })
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating note for user {current_user.id}: {str(e)}")
                flash("Failed to create note. Please try again.", category="error")
                return render_template("home.html", user=current_user, notes=get_user_notes())
        
        notes = get_user_notes()
        return render_template("home.html", user=current_user, notes=notes)
    
    except Exception as e:
        logger.error(f"Error loading home page for user {current_user.id}: {str(e)}")
        flash("An error occurred. Please try again.", category="error")
        return render_template("home.html", user=current_user, notes=[])

@views.route("/delete/<int:note_id>", methods=["POST"])
@login_required
def delete(note_id):
    """Handle note deletion"""
    try:
        note = Note.query.get(note_id)
        
        # Verify note exists and belongs to current user
        if not note:
            logger.warning(f"Delete attempt for non-existent note {note_id} by user {current_user.id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Note not found'
                }), 404
            flash("Note not found", category="error")
            return redirect(url_for("views.home"))
        
        if note.user_id != current_user.id:
            logger.warning(f"Unauthorized delete attempt for note {note_id} by user {current_user.id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Unauthorized'
                }), 403
            flash("Unauthorized action", category="error")
            return redirect(url_for("views.home"))
        
        # Delete note
        try:
            db.session.delete(note)
            db.session.commit()
            logger.info(f"Note {note_id} deleted by user {current_user.id}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'success',
                    'message': 'Note deleted successfully'
                })
            
            flash("Note deleted successfully", category="success")
            return redirect(url_for("views.home"))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting note {note_id}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to delete note'
                }), 500
            flash("Failed to delete note. Please try again.", category="error")
            return redirect(url_for("views.home"))
    
    except Exception as e:
        logger.error(f"Unexpected error during delete: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'error',
                'message': 'An error occurred'
            }), 500
        flash("An error occurred. Please try again.", category="error")
        return redirect(url_for("views.home"))

@views.route("/api/notes", methods=["GET"])
@login_required
def get_notes_api():
    """Get user's notes as JSON (for AJAX requests)"""
    try:
        notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created.desc()).all()
        
        return jsonify({
            'status': 'success',
            'notes': [{
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created': note.created.strftime('%Y-%m-%d %H:%M:%S')
            } for note in notes]
        })
    
    except Exception as e:
        logger.error(f"Error fetching notes for user {current_user.id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch notes'
        }), 500

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_notes():
    """Get all notes for current user"""
    try:
        return Note.query.filter_by(user_id=current_user.id).order_by(Note.created.desc()).all()
    except Exception as e:
        logger.error(f"Error fetching notes for user {current_user.id}: {str(e)}")
        return []