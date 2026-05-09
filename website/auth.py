import hmac
import logging
import random
import re
import threading
import resend

from datetime import datetime, timedelta
from flask import current_app
from email_validator import EmailNotValidError, validate_email
from flask import (Blueprint, flash, jsonify, redirect, render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from . import limiter
from .models import User
from .sync_google_sheets import add_user_to_google_sheet

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

resend.api_key = os.environ.get(
    "RESEND_API_KEY"
)

OTP_EXPIRY_MINUTES = 15

# VALIDATION HELPERS
def validate_email_format(email):
    try:
        validate_email(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit"
    return True, None


def validate_name(name):
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 50:
        return False, "Name must not exceed 50 characters"
    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        return False, "Name contains invalid characters"
    return True, None


def _generate_otp(user):
    """Set a fresh OTP on *user* and flush to the session (caller commits)."""
    otp_value = random.randint(100000, 999999)
    user.otp_secret = str(otp_value)
    user.otp_created_at = datetime.utcnow()
    return otp_value


def _otp_expired(user):
    """Return True if the stored OTP is older than OTP_EXPIRY_MINUTES."""
    if not user.otp_created_at:
        return True
    return datetime.utcnow() - user.otp_created_at > timedelta(minutes=OTP_EXPIRY_MINUTES)


def _otp_matches(user, candidate):
    """Constant-time OTP comparison to prevent timing attacks."""
    if not user.otp_secret:
        return False
    return hmac.compare_digest(user.otp_secret, candidate)


def send_otp_email(email, otp):

    try:

        params = {
            "from": "Notes App <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your Notes App Verification Code",
            "html": f"""
            <h2>Your Verification Code</h2>

            <p>Your OTP is:</p>

            <h1>{otp}</h1>

            <p>
                This code expires in
                {OTP_EXPIRY_MINUTES} minutes.
            </p>
            """
        }

        resend.Emails.send(params)

        logger.info(
            f"OTP email sent to {email}"
        )

        return True

    except Exception as e:

        logger.error(
            f"Failed to send OTP email: {e}"
        )

        return False
    
def send_otp_email_async(app, email, otp):

    with app.app_context():

        send_otp_email(email, otp)


def add_user_to_sheet_async(app, user):

    with app.app_context():

        add_user_to_google_sheet(user)

# AUTH ROUTES
@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            if not email or not password:
                flash('Email and password are required', category='error')
                return render_template("login.html", user=current_user)

            user = User.query.filter_by(email=email).first()

            if not user:
                logger.warning(f"Login attempt with unknown email: {email}")
                flash('Invalid email or password', category='error')
                return render_template("login.html", user=current_user)

            if not user.is_verified:
                logger.info(f"Login attempt with unverified account: {email}")
                otp_value = _generate_otp(user)
                db.session.commit()
                if send_otp_email(user.email, otp_value):
                    flash('Verification code sent to your email', 'info')
                    return redirect(url_for('auth.verify', email=user.email))
                flash('Failed to send verification email. Please try again.', 'error')
                return render_template("login.html", user=current_user)

            if not check_password_hash(user.password, password):
                logger.warning(f"Failed login for: {email}")
                flash('Invalid email or password', category='error')
                return render_template("login.html", user=current_user)

            login_user(user, remember=True)
            logger.info(f"User logged in: {email}")
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.home'))

        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/verify/<email>', methods=['GET', 'POST'])
def verify(email):
    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('User not found', category='error')
            return redirect(url_for('auth.login'))

        if user.is_verified:
            flash('Email already verified. Please log in.', category='info')
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            user_otp = request.form.get('otp', '').strip()

            if not user_otp:
                flash('Please enter the verification code', category='error')
                return render_template('verify.html', email=email, user=current_user)

            # BUG FIX: check expiry before comparing
            if _otp_expired(user):
                flash(
                    f'Verification code has expired. '
                    f'Please request a new one.',
                    'error',
                )
                return render_template('verify.html', email=email, user=current_user)

            # BUG FIX: constant-time comparison prevents timing attacks
            if _otp_matches(user, user_otp):
                user.is_verified = True
                user.otp_secret = None
                user.otp_created_at = None
                db.session.commit()
                logger.info(f"Email verified for: {email}")
                flash('Email verified successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))

            logger.warning(f"Invalid OTP attempt for: {email}")
            flash('Invalid verification code. Please try again.', 'error')

        return render_template('verify.html', email=email, user=current_user)

    except Exception as e:
        logger.error(f"Verification error: {e}")
        flash('An error occurred during verification. Please try again.', category='error')
        return redirect(url_for('auth.login'))


@auth.route('/resend_otp/<email>', methods=['POST'])
@limiter.limit("2 per minute")
def resend_otp(email):
    """
    BUG FIX: new endpoint — the old verify.html had a resendCode() JS function
    that only showed a toast but never contacted the server.  This route actually
    generates a fresh OTP and sends the email.
    """
    try:
        user = User.query.filter_by(email=email).first()

        if not user or user.is_verified:
            return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

        otp_value = _generate_otp(user)
        db.session.commit()

        if send_otp_email(user.email, otp_value):
            logger.info(f"OTP resent to {email}")
            return jsonify({'status': 'success', 'message': 'Verification code resent to your email'})

        return jsonify({'status': 'error', 'message': 'Failed to send email. Please try again.'}), 500

    except Exception as e:
        logger.error(f"Resend OTP error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500


@auth.route('/logout')
@login_required
def logout():
    logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            first_name = request.form.get('firstName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            password1 = request.form.get('password1', '')
            password2 = request.form.get('password2', '')

            is_valid, error_msg = validate_email_format(email)
            if not is_valid:
                flash(f'Invalid email: {error_msg}', category='error')
                return render_template("signup.html", user=current_user)

            if User.query.filter_by(email=email).first():
                logger.warning(f"Signup with existing email: {email}")
                flash('Email already registered', category='error')
                return render_template("signup.html", user=current_user)

            is_valid, error_msg = validate_name(first_name)
            if not is_valid:
                flash(f'Invalid first name: {error_msg}', category='error')
                return render_template("signup.html", user=current_user)

            is_valid, error_msg = validate_name(last_name)
            if not is_valid:
                flash(f'Invalid last name: {error_msg}', category='error')
                return render_template("signup.html", user=current_user)

            if password1 != password2:
                flash('Passwords do not match', category='error')
                return render_template("signup.html", user=current_user)

            is_valid, error_msg = validate_password_strength(password1)
            if not is_valid:
                flash(error_msg, category='error')
                return render_template("signup.html", user=current_user)

            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                otp_secret=None,
                otp_created_at=None,
                is_verified=False,
                password=generate_password_hash(password1, method='pbkdf2:sha256:260000'),
            )
            db.session.add(new_user)
            db.session.flush()

            otp_value = _generate_otp(new_user)
            db.session.commit()

            logger.info(f"New user registered: {email}")

            try:
                app = current_app._get_current_object()
                threading.Thread(
                    target=add_user_to_sheet_async,
                    args=(app, new_user),
                    daemon=True
                ).start()

            except Exception as e:

                logger.warning(
                    f"Google Sheets sync failed during signup: {e}"
                )

            try:
                app = current_app._get_current_object()
                threading.Thread(
                    target=send_otp_email_async,
                    args=(app, new_user.email, otp_value),
                    daemon=True
                ).start()
            except Exception as e:

                logger.warning(
                    f"Email sending failed: {e}"
                )

            flash(
                'Verification code sent to your email.',
                'info'
            )

            return redirect(
                url_for(
                    'auth.verify',
                    email=new_user.email
                )
            )

        except Exception as e:
            logger.error(f"Signup error: {e}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', category='error')

    return render_template("signup.html", user=current_user)


@auth.route('/forgot_password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()

            if not email:
                flash('Please enter your email', category='error')
                return render_template("forgot_password.html", user=current_user)

            user = User.query.filter_by(email=email).first()

            if not user:
                logger.info(f"Password reset for unknown email: {email}")
                # Generic message prevents email enumeration
                flash('If an account exists, a verification code will be sent', 'info')
                return render_template("forgot_password.html", user=current_user)

            otp_value = _generate_otp(user)
            db.session.commit()

            if send_otp_email(user.email, otp_value):
                logger.info(f"Password reset code sent to: {email}")
                flash('Verification code sent to your email', 'info')
                return redirect(url_for('auth.reset_password', email=user.email))

            flash('Failed to send verification email. Please try again.', 'error')

        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            flash('An error occurred. Please try again.', category='error')

    return render_template("forgot_password.html", user=current_user)


@auth.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('User not found', category='error')
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            user_otp = request.form.get('otp', '').strip()
            new_password1 = request.form.get('password1', '')
            new_password2 = request.form.get('password2', '')

            # BUG FIX: check expiry before comparing
            if _otp_expired(user):
                flash('Verification code has expired. Please request a new one.', 'error')
                return redirect(url_for('auth.forgot_password'))

            if not _otp_matches(user, user_otp):
                logger.warning(f"Invalid OTP during password reset for: {email}")
                flash('Invalid verification code. Please try again.', 'error')
                return render_template('reset_password.html', email=email, user=current_user)

            if new_password1 != new_password2:
                flash('Passwords do not match', category='error')
                return render_template('reset_password.html', email=email, user=current_user)

            is_valid, error_msg = validate_password_strength(new_password1)
            if not is_valid:
                flash(error_msg, category='error')
                return render_template('reset_password.html', email=email, user=current_user)

            user.password = generate_password_hash(new_password1, method='pbkdf2:sha256:260000')
            user.otp_secret = None
            user.otp_created_at = None
            db.session.commit()

            logger.info(f"Password reset for: {email}")
            flash('Password reset successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        return render_template('reset_password.html', email=email, user=current_user)

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        flash('An error occurred during password reset. Please try again.', category='error')
        return redirect(url_for('auth.login'))
