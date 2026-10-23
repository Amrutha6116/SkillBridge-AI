from flask import Blueprint, render_template, request, flash, redirect, url_for

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Screen 1: Landing Page."""
    return render_template('landing.html')


@main_bp.route('/about')
def about():
    """About section anchor or standalone redirect."""
    return redirect(url_for('main.index', _anchor='about'))


@main_bp.route('/features')
def features():
    """Features section anchor or standalone redirect."""
    return redirect(url_for('main.index', _anchor='features'))


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact section handling."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not message:
            flash('Please fill in all fields before submitting.', 'danger')
            return redirect(url_for('main.index', _anchor='contact'))
            
        flash('Thank you for reaching out! The placement coordinator has received your message.', 'success')
        return redirect(url_for('main.index', _anchor='contact'))
        
    return redirect(url_for('main.index', _anchor='contact'))

