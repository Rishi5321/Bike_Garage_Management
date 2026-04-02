from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import db, mail
from app.models import User
import random
import string

auth = Blueprint('auth', __name__)


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp, username):
    try:
        msg = Message(
            subject = 'Your Bike Garage OTP Verification Code',
            recipients = [email]
        )
        msg.html = f"""
        <div style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:20px;">
            <div style="background:#2E4057;color:white;padding:20px;text-align:center;border-radius:8px 8px 0 0;">
                <h2 style="margin:0;">🔧 Bike Garage</h2>
                <p style="margin:5px 0 0;color:#cdd5e0;font-size:14px;">Account Verification</p>
            </div>
            <div style="background:#f8f9fa;padding:30px;border-radius:0 0 8px 8px;">
                <p style="font-size:16px;">Hello <strong>{username}</strong>,</p>
                <p>Your OTP verification code is:</p>
                <div style="background:white;border:2px dashed #2E4057;border-radius:8px;padding:20px;text-align:center;margin:20px 0;">
                    <h1 style="color:#2E4057;font-size:42px;letter-spacing:12px;margin:0;">{otp}</h1>
                </div>
                <p style="color:#6c757d;font-size:13px;">This OTP is valid for <strong>10 minutes</strong> only.</p>
                <p style="color:#6c757d;font-size:13px;">If you did not request this, please ignore this email.</p>
                <hr style="border:none;border-top:1px solid #dee2e6;">
                <p style="color:#adb5bd;font-size:12px;text-align:center;">
                    Bike Garage Management System
                </p>
            </div>
        </div>
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user     = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back! You are logged in.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')
        confirm  = request.form.get('confirm_password')

        if password != confirm:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register'))

        otp = generate_otp()

        session['otp']      = otp
        session['username'] = username
        session['email']    = email
        session['password'] = password

        sent = send_otp_email(email, otp, username)

        if sent:
            flash(f'OTP sent to {email}! Please check your inbox.', 'success')
            return redirect(url_for('auth.verify_otp'))
        else:
            flash('Failed to send OTP. Please check your email address.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        flash('Session expired. Please register again.', 'warning')
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if entered_otp == session.get('otp'):
            user = User(
                username = session.get('username'),
                email    = session.get('email')
            )
            user.set_password(session.get('password'))
            db.session.add(user)
            db.session.commit()

            session.pop('otp',      None)
            session.pop('username', None)
            session.pop('email',    None)
            session.pop('password', None)

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP! Please try again.', 'danger')

    return render_template('auth/verify_otp.html',
                           email=session.get('email'))


@auth.route('/resend-otp')
def resend_otp():
    if 'otp' not in session:
        flash('Session expired. Please register again.', 'warning')
        return redirect(url_for('auth.register'))

    otp  = generate_otp()
    session['otp'] = otp
    sent = send_otp_email(
        session.get('email'),
        otp,
        session.get('username')
    )

    if sent:
        flash('New OTP sent to your email!', 'success')
    else:
        flash('Failed to resend OTP. Please try again.', 'danger')

    return redirect(url_for('auth.verify_otp'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user  = User.query.filter_by(email=email).first()

        if user:
            otp            = generate_otp()
            session['reset_otp']   = otp
            session['reset_email'] = email
            sent = send_otp_email(email, otp, user.username)
            if sent:
                flash(f'OTP sent to {email}!', 'success')
                return redirect(url_for('auth.reset_verify_otp'))
            else:
                flash('Failed to send OTP. Try again.', 'danger')
        else:
            flash('No account found with this email!', 'danger')

    return render_template('auth/forgot_password.html')


@auth.route('/reset-verify-otp', methods=['GET', 'POST'])
def reset_verify_otp():
    if 'reset_otp' not in session:
        flash('Session expired. Please try again.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if entered_otp == session.get('reset_otp'):
            session['reset_verified'] = True
            flash('OTP verified! Set your new password.', 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('Invalid OTP! Please try again.', 'danger')

    return render_template('auth/reset_verify_otp.html',
                           email=session.get('reset_email'))


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('reset_verified'):
        flash('Please verify OTP first.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm  = request.form.get('confirm_password')

        if password != confirm:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.reset_password'))

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('auth.reset_password'))

        user = User.query.filter_by(
            email=session.get('reset_email')
        ).first()

        if user:
            user.set_password(password)
            db.session.commit()

            session.pop('reset_otp',      None)
            session.pop('reset_email',    None)
            session.pop('reset_verified', None)

            flash('Password updated successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Something went wrong. Please try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))

    return render_template('auth/reset_password.html')

@auth.route('/forgot-username', methods=['GET', 'POST'])
def forgot_username():
    if request.method == 'POST':
        email = request.form.get('email')
        user  = User.query.filter_by(email=email).first()

        if user:
            try:
                msg = Message(
                    subject    = 'Your Bike Garage Username',
                    recipients = [email]
                )
                msg.html = f"""
                <div style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:20px;">
                    <div style="background:#2E4057;color:white;padding:20px;text-align:center;border-radius:8px 8px 0 0;">
                        <h2 style="margin:0;">🔧 Bike Garage</h2>
                        <p style="margin:5px 0 0;color:#cdd5e0;font-size:14px;">Username Recovery</p>
                    </div>
                    <div style="background:#f8f9fa;padding:30px;border-radius:0 0 8px 8px;">
                        <p style="font-size:16px;">Hello,</p>
                        <p>Your username for Bike Garage is:</p>
                        <div style="background:white;border:2px dashed #2E4057;border-radius:8px;padding:20px;text-align:center;margin:20px 0;">
                            <h2 style="color:#2E4057;margin:0;letter-spacing:4px;">
                                {user.username}
                            </h2>
                        </div>
                        <p style="color:#6c757d;font-size:13px;">
                            You can now login with this username.
                        </p>
                        <p style="color:#6c757d;font-size:13px;">
                            If you did not request this, please ignore this email.
                        </p>
                        <hr style="border:none;border-top:1px solid #dee2e6;">
                        <p style="color:#adb5bd;font-size:12px;text-align:center;">
                            Bike Garage Management System
                        </p>
                    </div>
                </div>
                """
                mail.send(msg)
                flash('Your username has been sent to your email!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash('Failed to send email. Please try again.', 'danger')
        else:
            flash('No account found with this email!', 'danger')

    return render_template('auth/forgot_username.html')

# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_user, logout_user, login_required, current_user
# from app import db
# from app.models import User

# auth = Blueprint('auth', __name__)


# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard.index'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user     = User.query.filter_by(username=username).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash('Welcome back! You are logged in.', 'success')
#             return redirect(url_for('dashboard.index'))
#         else:
#             flash('Invalid username or password!', 'danger')

#     return render_template('auth/login.html')


# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email    = request.form.get('email')
#         password = request.form.get('password')
#         confirm  = request.form.get('confirm_password')

#         if password != confirm:
#             flash('Passwords do not match!', 'danger')
#             return redirect(url_for('auth.register'))

#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash('Username already exists!', 'danger')
#             return redirect(url_for('auth.register'))

#         existing_email = User.query.filter_by(email=email).first()
#         if existing_email:
#             flash('Email already registered!', 'danger')
#             return redirect(url_for('auth.register'))

#         user = User(username=username, email=email)
#         user.set_password(password)
#         db.session.add(user)
#         db.session.commit()
#         flash('Account created! Please login.', 'success')
#         return redirect(url_for('auth.login'))

#     return render_template('auth/register.html')


# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('auth.login'))