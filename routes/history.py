from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import db
from models.user import User
from models.assessment import AssessmentAttempt
from routes.auth import login_required

history_bp = Blueprint('history', __name__, url_prefix='/history')


@history_bp.route('/')
@login_required
def index():
    """Screen 9: Chronological Assessment History."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    # Strictly isolated query for the current student only
    attempts = AssessmentAttempt.query.filter_by(user_id=user_id)\
        .order_by(AssessmentAttempt.completed_at.desc()).all()

    completed_attempts = [a for a in attempts if a.status == 'completed']
    total_tests = len(completed_attempts)

    highest_score = max([a.percentage for a in completed_attempts], default=0.0)
    avg_score = round(sum([a.percentage for a in completed_attempts]) / total_tests, 1) if total_tests > 0 else 0.0

    return render_template(
        'history/index.html',
        active_page='history',
        user=user,
        attempts=attempts,
        total_tests=total_tests,
        highest_score=highest_score,
        avg_score=avg_score
    )
