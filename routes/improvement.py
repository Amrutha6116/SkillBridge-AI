from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from extensions import db
from models.user import User
from models.skill import Skill
from models.role import JobRole, RoleSkillRequirement
from models.assessment import AssessmentAttempt, AssessmentResult
from models.improvement import ImprovementPlan, ImprovementPlanTask
from services.ai_service import AIService
from routes.auth import login_required


def get_utc_now():
    return datetime.now(timezone.utc)


improvement_bp = Blueprint('improvement', __name__, url_prefix='/improvement')


@improvement_bp.route('/')
@login_required
def index():
    """Screen 8: Personalized Improvement Plan / AI Suggestions."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    # Fetch student's plans (ordered by latest first)
    plans = ImprovementPlan.query.filter_by(user_id=user_id)\
        .order_by(ImprovementPlan.created_at.desc()).all()

    active_plan = plans[0] if plans else None
    plan_tasks = []
    completed_count = 0
    total_tasks = 0
    progress_percentage = 0

    if active_plan:
        plan_tasks = ImprovementPlanTask.query.filter_by(plan_id=active_plan.id).all()
        total_tasks = len(plan_tasks)
        completed_count = sum(1 for t in plan_tasks if t.status == 'completed')
        if total_tasks > 0:
            progress_percentage = round((completed_count / total_tasks) * 100)

    # Check if external AI service is configured
    ai_service = AIService()
    is_ai_connected = ai_service.is_ai_connected()

    return render_template(
        'improvement/index.html',
        active_page='improvement',
        user=user,
        plans=plans,
        active_plan=active_plan,
        tasks=plan_tasks,
        completed_count=completed_count,
        total_tasks=total_tasks,
        progress_percentage=progress_percentage,
        is_ai_connected=is_ai_connected
    )


@improvement_bp.route('/generate/<int:attempt_id>', methods=['POST', 'GET'])
@login_required
def generate_from_attempt(attempt_id):
    """Generate or retrieve a personalized AI learning plan based on an assessment attempt."""
    user_id = session.get('user_id')
    attempt = db.session.get(AssessmentAttempt, attempt_id)

    if not attempt or attempt.user_id != user_id:
        abort(404)

    user = db.session.get(User, user_id)

    # Check if a plan already exists for this attempt
    existing_plan = ImprovementPlan.query.filter_by(attempt_id=attempt.id, user_id=user_id).first()
    if existing_plan:
        flash('Displaying your existing learning roadmap generated for this assessment.', 'info')
        return redirect(url_for('improvement.index'))

    # Gather gaps and strengths from attempt results
    results = AssessmentResult.query.filter_by(attempt_id=attempt.id).all()
    role = db.session.get(JobRole, attempt.role_id) if attempt.role_id else None
    role_title = role.title if role else "Software Engineering"

    # Get benchmarks
    role_benchmarks = {}
    if role:
        role_reqs = RoleSkillRequirement.query.filter_by(role_id=role.id).all()
        role_benchmarks = {r.skill_id: r.required_level for r in role_reqs}

    skill_gaps = []
    strengths = []

    for r in results:
        skill = r.skill
        s_name = skill.name if skill else "Core Skill"
        req_lvl = role_benchmarks.get(r.skill_id, 3.5)
        gap = max(0.0, round(req_lvl - r.proficiency_level, 1))

        if gap > 0:
            skill_gaps.append({
                'skill_id': r.skill_id,
                'skill_name': s_name,
                'current_level': r.proficiency_level,
                'required_level': req_lvl,
                'gap': gap
            })
        else:
            strengths.append({
                'skill_id': r.skill_id,
                'skill_name': s_name,
                'current_level': r.proficiency_level
            })

    # Sort skill gaps by highest gap descending
    skill_gaps.sort(key=lambda x: x['gap'], reverse=True)

    # Generate plan using AI Service
    ai_service = AIService()
    generated = ai_service.generate_plan(
        student_name=user.full_name,
        target_role_title=role_title,
        skill_gaps=skill_gaps,
        strengths=strengths
    )

    # Persist ImprovementPlan record
    new_plan = ImprovementPlan(
        user_id=user.id,
        attempt_id=attempt.id,
        target_role_id=role.id if role else None,
        title=generated.get('title', f"{role_title} Placement Readiness Plan"),
        summary=generated.get('summary', 'Targeted learning plan to close skill deficits.'),
        generated_by=generated.get('generated_by', 'fallback'),
        created_at=get_utc_now()
    )
    db.session.add(new_plan)
    db.session.flush()

    # Create mapping of skill name to skill object
    skills_map = {s.name.lower(): s for s in Skill.query.all()}
    first_skill = Skill.query.first()

    # Persist tasks
    for t in generated.get('tasks', []):
        t_skill_name = t.get('skill_name', '').lower()
        matched_skill = skills_map.get(t_skill_name, first_skill)

        task = ImprovementPlanTask(
            plan_id=new_plan.id,
            skill_id=matched_skill.id if matched_skill else 1,
            title=t.get('title', 'Practice Milestone'),
            description=t.get('description', 'Complete practice tasks to build technical mastery.'),
            priority=t.get('priority', 'Medium'),
            current_level=t.get('current_level', 1.0),
            target_level=t.get('target_level', 4.0),
            estimated_duration=t.get('estimated_duration', '1 week'),
            status='not_started'
        )
        db.session.add(task)

    db.session.commit()
    flash('Personalized learning roadmap generated successfully!', 'success')
    return redirect(url_for('improvement.index'))


@improvement_bp.route('/task/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(task_id):
    """Update improvement task status via Fetch API."""
    user_id = session.get('user_id')
    task = db.session.get(ImprovementPlanTask, task_id)

    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    # Ensure task belongs to a plan owned by the logged-in student
    plan = db.session.get(ImprovementPlan, task.plan_id)
    if not plan or plan.user_id != user_id:
        return jsonify({'error': 'Unauthorized task update.'}), 403

    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()

    if new_status not in ['not_started', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status.'}), 400

    task.status = new_status
    if new_status == 'completed':
        task.completed_at = get_utc_now()
    else:
        task.completed_at = None

    db.session.commit()

    # Calculate updated plan progress
    all_tasks = ImprovementPlanTask.query.filter_by(plan_id=plan.id).all()
    completed_count = sum(1 for t in all_tasks if t.status == 'completed')
    total_tasks = len(all_tasks)
    percentage = round((completed_count / total_tasks) * 100) if total_tasks > 0 else 0

    return jsonify({
        'success': True,
        'task_id': task.id,
        'status': task.status,
        'completed_count': completed_count,
        'total_tasks': total_tasks,
        'progress_percentage': percentage
    })
