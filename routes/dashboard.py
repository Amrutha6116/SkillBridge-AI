from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import db
from models.user import User
from models.assessment import AssessmentAttempt, AssessmentResult
from models.improvement import ImprovementPlan, ImprovementPlanTask
from models.role import JobRole
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Screen 4: Student Dashboard with live database metrics."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('auth.login'))

    # 1. Total assessments taken by this student
    attempts = AssessmentAttempt.query.filter_by(user_id=user.id)\
        .order_by(AssessmentAttempt.completed_at.desc()).all()
    assessments_count = len(attempts)

    # 2. Skill gaps identified from the student's latest assessment attempt
    latest_attempt = attempts[0] if attempts else None
    skill_gaps_count = 0
    latest_results = []
    if latest_attempt:
        latest_results = AssessmentResult.query.filter_by(attempt_id=latest_attempt.id).all()
        # A gap exists if required benchmark or deficit > 0
        skill_gaps_count = sum(1 for r in latest_results if (r.gap_level and r.gap_level > 0.0))

    # 3. Improvement tasks suggested / pending
    user_plans = ImprovementPlan.query.filter_by(user_id=user.id).all()
    plan_ids = [p.id for p in user_plans]
    improvement_tasks_count = 0
    completed_tasks_count = 0
    if plan_ids:
        all_tasks = ImprovementPlanTask.query.filter(ImprovementPlanTask.plan_id.in_(plan_ids)).all()
        improvement_tasks_count = sum(1 for t in all_tasks if t.status != 'completed')
        completed_tasks_count = sum(1 for t in all_tasks if t.status == 'completed')

    # 4. Job roles available & explored
    total_roles_count = JobRole.query.count()

    # Calculate student readiness tier
    avg_score = 0.0
    if attempts:
        avg_score = round(sum(a.percentage for a in attempts) / len(attempts), 1)

    readiness_status = "Initial Assessment Needed"
    if assessments_count > 0:
        if avg_score >= 80.0:
            readiness_status = "Placement Ready (Tier 1)"
        elif avg_score >= 60.0:
            readiness_status = "Competent (Tier 2 Ready)"
        else:
            readiness_status = "Needs Targeted Improvement"

    # Career Journey Step Statuses
    journey = {
        'step1': 'completed' if assessments_count > 0 else 'active',
        'step2': 'completed' if (assessments_count > 0 and skill_gaps_count is not None) else ('active' if assessments_count > 0 else ''),
        'step3': 'completed' if completed_tasks_count > 0 else ('active' if len(user_plans) > 0 else ''),
        'step4': 'completed' if avg_score >= 80.0 else ('active' if assessments_count >= 2 else '')
    }

    recent_attempts = attempts[:5]

    return render_template(
        'dashboard/index.html',
        active_page='dashboard',
        user=user,
        assessments_count=assessments_count,
        skill_gaps_count=skill_gaps_count,
        improvement_tasks_count=improvement_tasks_count,
        total_roles_count=total_roles_count,
        avg_score=avg_score,
        readiness_status=readiness_status,
        journey=journey,
        recent_attempts=recent_attempts,
        latest_attempt=latest_attempt
    )
