from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from extensions import db
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to protect authenticated routes against unauthorized guest access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this placement module.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to protect administrator-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in with administrator credentials.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Access restricted to Placement Administrators only.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Screen 2: Sign Up Page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        role = request.form.get('role', 'student').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        register_number = request.form.get('register_number', '').strip().upper()
        password = request.form.get('password', '')
        admin_secret = request.form.get('admin_secret', '').strip()

        # Input Validations
        if not full_name or not email or not register_number or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/signup.html', form_data=request.form)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/signup.html', form_data=request.form)

        if '@' not in email or '.' not in email:
            flash('Please enter a valid academic or professional email address.', 'danger')
            return render_template('auth/signup.html', form_data=request.form)

        # Safe Administrator Provisioning Check
        if role == 'admin':
            expected_secret = current_app.config.get('ADMIN_SECRET_KEY', 'skillbridge-admin-secret-2026')
            if admin_secret != expected_secret:
                flash('Invalid Administrator Secret Token. Public admin creation is restricted.', 'danger')
                return render_template('auth/signup.html', form_data=request.form)
        else:
            role = 'student'

        # Duplicate Account Checks
        if User.query.filter_by(email=email).first():
            flash('An account with this email address is already registered. Please log in.', 'warning')
            return render_template('auth/signup.html', form_data=request.form)

        if User.query.filter_by(register_number=register_number).first():
            flash('An account with this Register Number / ID is already registered.', 'warning')
            return render_template('auth/signup.html', form_data=request.form)

        # Create and persist new user
        new_user = User(
            full_name=full_name,
            email=email,
            register_number=register_number,
            role=role,
            course='B.E. Computer Science and Engineering' if role == 'student' else 'Placement Advisory Cell',
            college='School of Engineering and Technology',
            graduation_year=2027 if role == 'student' else 2020
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'Account created successfully for {full_name}! Please sign in.', 'success')
            return redirect(url_for('auth.login', identifier=email))
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred while saving your profile. Please try again.', 'danger')
            return render_template('auth/signup.html', form_data=request.form)

    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Screen 3: Login Page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    identifier = request.args.get('identifier', '')

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'true'

        if not identifier or not password:
            flash('Please enter both your identifier and password.', 'danger')
            return render_template('auth/login.html', identifier=identifier)

        # Check by email or register number
        user = User.query.filter(
            (User.email == identifier.lower()) | (User.register_number == identifier.upper())
        ).first()

        if not user or not user.check_password(password):
            flash('Invalid email/register number or password. Please verify and try again.', 'danger')
            return render_template('auth/login.html', identifier=identifier)

        # Secure Session Establishment
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.full_name
        session['user_role'] = user.role
        session['user_email'] = user.email
        session['user_reg'] = user.register_number

        if remember_me:
            session.permanent = True

        flash(f'Welcome back, {user.full_name}!', 'success')
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html', identifier=identifier)


@auth_bp.route('/logout')
def logout():
    """Logout current user session safely."""
    user_name = session.get('user_name', 'Student')
    session.clear()
    flash(f'Goodbye {user_name}! You have been securely logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Safe placeholder / guidance for password recovery."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            flash(
                f"Password recovery requested for {email}. In this academic demonstration system, please contact your administrator or update your password via Profile Settings.",
                'info'
            )
        else:
            flash("If an account exists with that email address, reset guidance will be provided.", 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')
