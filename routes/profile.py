from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models.user import User
from routes.auth import login_required

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def index():
    """Screen 10: Profile and Settings."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    return render_template('profile/index.html', active_page='profile', user=user)


@profile_bp.route('/update', methods=['POST'])
@login_required
def update():
    """Update allowed student profile details."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    full_name = request.form.get('full_name', '').strip()
    course = request.form.get('course', '').strip()
    college = request.form.get('college', '').strip()
    grad_year_str = request.form.get('graduation_year', '').strip()

    if not full_name:
        flash('Full name cannot be empty.', 'danger')
        return redirect(url_for('profile.index'))

    user.full_name = full_name
    if course:
        user.course = course
    if college:
        user.college = college
    if grad_year_str and grad_year_str.isdigit():
        user.graduation_year = int(grad_year_str)

    db.session.commit()
    session['user_name'] = user.full_name

    flash('Profile details updated successfully.', 'success')
    return redirect(url_for('profile.index'))


@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change account password with verification."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required.', 'danger')
        return redirect(url_for('profile.index'))

    if not user.check_password(current_password):
        flash('Current password verification failed. Please try again.', 'danger')
        return redirect(url_for('profile.index'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'danger')
        return redirect(url_for('profile.index'))

    if new_password != confirm_password:
        flash('New password and confirmation do not match.', 'danger')
        return redirect(url_for('profile.index'))

    user.set_password(new_password)
    db.session.commit()

    flash('Your password has been changed securely.', 'success')
    return redirect(url_for('profile.index'))
