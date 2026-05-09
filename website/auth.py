from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
import random
from .sync_google_sheets import sync_with_google_sheets

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.is_verified:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password or email not verified, try again', category='error')
        elif user and not user.is_verified:
            flash('Email not verified, verify now', category='error')
            otp_value = random.randint(0, 999999)
            send_otp_email(user.email, otp_value)
            flash('An OTP has been sent to your email. Please enter it to verify your account', 'info')
            return redirect(url_for('auth.verify', email=user.email, otp_value=otp_value))
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/verify/<email>', methods=['GET', 'POST'])
def verify(email, otp_value):
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        user_otp = request.form.get('otp')

        if user_otp == user.otp_secret:
            user.is_verified = True
            db.session.commit()
            flash('Account verified successfully, You can now log in', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify.html', email=email, user=current_user)

def send_otp_email(email, otp):
    subject = 'OTP Verification'
    body = f'Your OTP for account verification is: {otp}'

    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2 or len(last_name) < 2:
            flash('First Name and Last Name must be greater than 2 letters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password must be greater than 7 characters', category='error')
        else:
            otp_value = random.randint(0, 999999)
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                otp_secret=str(otp_value),
                is_verified=False,
                password=generate_password_hash(
                    password1,
                    method='pbkdf2:sha256:6000'
                )
            )
            db.session.add(new_user)
            db.session.commit()

            try:
                sync_with_google_sheets()
            except Exception as e:
                print("Google Sheets Sync Failed:", e)

            send_otp_email(new_user.email, otp_value)

            flash(
                'An OTP has been sent to your email. Please enter it to verify your account.',
                'info'
            )

            return redirect(
                url_for(
                    'auth.verify',
                    email=new_user.email,
                    otp_value=otp_value
                )
            )

    return render_template("signup.html", user=current_user)

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            otp_value = random.randint(0, 999999)
            user.otp_secret = str(otp_value)
            db.session.commit()
            send_otp_email(user.email, otp_value)
            flash('An OTP has been sent to your email. Please enter it to reset your password.', 'info')
            return redirect(url_for('auth.reset_password', email=user.email, otp_value=otp_value))
        else:
            flash('Email does not exist', category='error')

    return render_template("forgot_password.html", user=current_user)

@auth.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email, otp_value):
    user = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        user_otp = request.form.get('otp')
        new_password1 = request.form.get('password1')
        new_password2 = request.form.get('password2')

        if user_otp == user.otp_secret:
            if new_password1 != new_password2:
                flash('Passwords do not match', category='error')
            elif len(new_password1) < 7:
                flash('Password must be greater than 7 characters', category='error')
            else:
                user.password = generate_password_hash(new_password1, method='pbkdf2:sha256:6000')
                user.otp_secret = None  # Clear the OTP secret
                db.session.commit()
                flash('Password has been reset successfully. You can now log in.', 'success')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('reset_password.html', email=email, user=current_user)