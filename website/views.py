from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Note, User
import json
from sqlalchemy.sql import exists


views=Blueprint('views',__name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note_title = request.form['title']
        note_content = request.form['content']

        if note_title.strip() and note_content.strip():
            new_note = Note(title=note_title, content=note_content, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Note added!", category='success')

        #return redirect(url_for('views.home'))

    notes = Note.query.filter(Note.user_id==current_user.id).all()
    return render_template('home.html', notes=notes, user=current_user)

@views.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted!", category='success')
    notes = Note.query.filter(Note.user_id==current_user.id).all()
    return render_template('home.html', notes=notes, user=current_user)