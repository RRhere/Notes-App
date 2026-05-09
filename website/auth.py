from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from email_validator import validate_email, EmailNotValidError
import random
import logging
import re
from .sync_google_sheets import sync_with_google_sheets

auth = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

# ============================================
# VALIDATION FUNCTIONS
# ============================================

def validate_email_format(email):
    """Validate email format using email_validator"""
    try:
        validate_email(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)

def validate_password_strength(password):
    """Validate password strength"""
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
    """Validate name length and characters"""
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 50:
        return False, "Name must not exceed 50 characters"
    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        return False, "Name contains invalid characters"
    return True, None

def send_otp_email(email, otp):
    """Send OTP email with error handling"""
    try:
        subject = 'Your Notes App Verification Code'
        body = f'''
Hello,

Your verification code is: {otp}

This code will expire in 15 minutes.

If you didn't request this code, please ignore this email.

Best regards,
Notes App Team
        '''
        msg = Message(subject, recipients=[email], body=body)
        mail.send(msg)
        logger.info(f"OTP email sent successfully to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False

# ============================================
# AUTH ROUTES
# ============================================

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Handle user login with rate limiting"""
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
                logger.warning(f"Login attempt with non-existent email: {email}")
                flash('Invalid email or password', category='error')
                return render_template("login.html", user=current_user)
            
            if not user.is_verified:
                logger.info(f"Login attempt with unverified account: {email}")
                flash('Please verify your email first', category='warning')
                otp_value = random.randint(100000, 999999)
                user.otp_secret = str(otp_value)
                db.session.commit()
                if send_otp_email(user.email, otp_value):
                    flash('Verification code sent to your email', 'info')
                    return redirect(url_for('auth.verify', email=user.email))
                else:
                    flash('Failed to send verification email. Please try again.', 'error')
                    return render_template("login.html", user=current_user)
            
            if not check_password_hash(user.password, password):
                logger.warning(f"Failed login attempt for user: {email}")
                flash('Invalid email or password', category='error')
                return render_template("login.html", user=current_user)
            
            login_user(user, remember=True)
            logger.info(f"User logged in successfully: {email}")
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.home'))
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', category='error')
            return render_template("login.html", user=current_user)
    
    return render_template("login.html", user=current_user)

@auth.route('/verify/<email>', methods=['GET', 'POST'])
def verify(email):
    """Handle email verification"""
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
            
            if user_otp == user.otp_secret:
                user.is_verified = True
                user.otp_secret = None
                db.session.commit()
                logger.info(f"Email verified for user: {email}")
                flash('Email verified successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                logger.warning(f"Invalid OTP attempt for user: {email}")
                flash('Invalid verification code. Please try again.', 'error')
        
        return render_template('verify.html', email=email, user=current_user)
    
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        flash('An error occurred during verification. Please try again.', category='error')
        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def signup():
    """Handle user signup with validation"""
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            first_name = request.form.get('firstName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            password1 = request.form.get('password1', '')
            password2 = request.form.get('password2', '')
            
            # Validate email
            is_valid, error_msg = validate_email_format(email)
            if not is_valid:
                flash(f'Invalid email: {error_msg}', category='error')
                return render_template("signup.html", user=current_user)
            
            # Check if email exists
            if User.query.filter_by(email=email).first():
                logger.warning(f"Signup attempt with existing email: {email}")
                flash('Email already registered', category='error')
                return render_template("signup.html", user=current_user)
            
            # Validate names
            is_valid, error_msg = validate_name(first_name)
            if not is_valid:
                flash(f'Invalid first name: {error_msg}', category='error')
                return render_template("signup.html", user=current_user)
            
            is_valid, error_msg = validate_name(last_name)
            if not is_valid:
                flash(f'Invalid last name: {error_msg}', category='error')
                return render_template("signup.html", user=current_user)
            
            # Validate passwords match
            if password1 != password2:
                flash('Passwords do not match', category='error')
                return render_template("signup.html", user=current_user)
            
            # Validate password strength
            is_valid, error_msg = validate_password_strength(password1)
            if not is_valid:
                flash(error_msg, category='error')
                return render_template("signup.html", user=current_user)
            
            # Create user
            otp_value = random.randint(100000, 999999)
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                otp_secret=str(otp_value),
                is_verified=False,
                password=generate_password_hash(password1, method='pbkdf2:sha256:6000')
            )
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"New user registered: {email}")
            
            # Try to sync with Google Sheets
            try:
                sync_with_google_sheets()
            except Exception as e:
                logger.warning(f"Google Sheets sync failed during signup: {str(e)}")
            
            # Send OTP email
            if send_otp_email(new_user.email, otp_value):
                flash('Verification code sent to your email. Please check your inbox.', 'info')
                return redirect(url_for('auth.verify', email=new_user.email))
            else:
                flash('Account created but verification email failed. Please try logging in.', 'warning')
                return redirect(url_for('auth.login'))
        
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', category='error')
            return render_template("signup.html", user=current_user)
    
    return render_template("signup.html", user=current_user)

@auth.route('/forgot_password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Handle password reset request"""
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
                logger.info(f"Password reset request for non-existent email: {email}")
                flash('If an account exists, a verification code will be sent', 'info')
                return render_template("forgot_password.html", user=current_user)
            
            otp_value = random.randint(100000, 999999)
            user.otp_secret = str(otp_value)
            db.session.commit()
            
            if send_otp_email(user.email, otp_value):
                logger.info(f"Password reset code sent to: {email}")
                flash('Verification code sent to your email', 'info')
                return redirect(url_for('auth.reset_password', email=user.email))
            else:
                flash('Failed to send verification email. Please try again.', 'error')
                return render_template("forgot_password.html", user=current_user)
        
        except Exception as e:
            logger.error(f"Forgot password error: {str(e)}")
            flash('An error occurred. Please try again.', category='error')
            return render_template("forgot_password.html", user=current_user)
    
    return render_template("forgot_password.html", user=current_user)

@auth.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    """Handle password reset"""
    try:
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('User not found', category='error')
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            user_otp = request.form.get('otp', '').strip()
            new_password1 = request.form.get('password1', '')
            new_password2 = request.form.get('password2', '')
            
            if user_otp != user.otp_secret:
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
            
            user.password = generate_password_hash(new_password1, method='pbkdf2:sha256:6000')
            user.otp_secret = None
            db.session.commit()
            
            logger.info(f"Password reset successfully for: {email}")
            flash('Password reset successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        
        return render_template('reset_password.html', email=email, user=current_user)
    
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        flash('An error occurred during password reset. Please try again.', category='error')
        return redirect(url_for('auth.login'))