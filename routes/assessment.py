from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from extensions import db
from models.user import User
from models.skill import Skill
from models.role import JobRole, RoleSkillRequirement
from models.assessment import AssessmentQuestion, AssessmentAttempt, AssessmentResponse, AssessmentResult
from routes.auth import login_required


def get_utc_now():
    return datetime.now(timezone.utc)


assessment_bp = Blueprint('assessment', __name__, url_prefix='/assessment')


@assessment_bp.route('/')
@login_required
def index():
    """Screen 5 Hub: Choose an assessment category or job-role targeted evaluation."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    roles = JobRole.query.all()
    skills = Skill.query.all()

    # Pre-calculate category question counts
    category_counts = {}
    for s in skills:
        count = AssessmentQuestion.query.filter_by(skill_id=s.id).count()
        category_counts[s.category] = category_counts.get(s.category, 0) + count

    total_questions = sum(category_counts.values())

    return render_template(
        'assessment/index.html',
        active_page='assessment',
        user=user,
        roles=roles,
        category_counts=category_counts,
        total_questions=total_questions
    )


@assessment_bp.route('/start', methods=['POST'])
@login_required
def start():
    """Initialize a new assessment attempt session."""
    user_id = session.get('user_id')
    assessment_type = request.form.get('assessment_type', 'Comprehensive Diagnostic').strip()
    role_id = request.form.get('role_id')

    target_role = None
    if role_id and role_id.isdigit():
        target_role = db.session.get(JobRole, int(role_id))

    # Determine attempt title / category
    if target_role:
        category_name = f"{target_role.title} Assessment"
    else:
        category_name = assessment_type

    # Create new attempt
    attempt = AssessmentAttempt(
        user_id=user_id,
        role_id=target_role.id if target_role else None,
        category=category_name,
        status='in_progress',
        started_at=get_utc_now()
    )
    db.session.add(attempt)
    db.session.commit()

    return redirect(url_for('assessment.take', attempt_id=attempt.id))


@assessment_bp.route('/take/<int:attempt_id>')
@login_required
def take(attempt_id):
    """Screen 5: Interactive Assessment Taker."""
    user_id = session.get('user_id')
    attempt = db.session.get(AssessmentAttempt, attempt_id)

    if not attempt or attempt.user_id != user_id:
        abort(404)

    # Prevent re-taking already submitted/completed attempts
    if attempt.status == 'completed':
        flash('This assessment has already been submitted and scored.', 'info')
        return redirect(url_for('assessment.results', attempt_id=attempt.id))

    # Select relevant questions for this attempt
    if attempt.role_id:
        # Questions mapped to the skills required for this job role
        role = db.session.get(JobRole, attempt.role_id)
        skill_ids = [req.skill_id for req in role.requirements]
        questions = AssessmentQuestion.query.filter(AssessmentQuestion.skill_id.in_(skill_ids)).all()
    elif attempt.category in ['Web Development', 'Core CS', 'Aptitude', 'Data & AI']:
        # Questions in this specific skill category
        skills = Skill.query.filter_by(category=attempt.category).all()
        skill_ids = [s.id for s in skills]
        questions = AssessmentQuestion.query.filter(AssessmentQuestion.skill_id.in_(skill_ids)).all()
    else:
        # Comprehensive evaluation: all questions
        questions = AssessmentQuestion.query.all()

    if not questions:
        flash('No diagnostic questions are configured for this category yet.', 'warning')
        return redirect(url_for('assessment.index'))

    # Strictly serialize without revealing correct_option to client DOM
    client_questions = [q.to_client_dict() for q in questions]

    return render_template(
        'assessment/take.html',
        active_page='assessment',
        attempt=attempt,
        questions=client_questions,
        total_questions=len(client_questions)
    )


@assessment_bp.route('/submit/<int:attempt_id>', methods=['POST'])
@login_required
def submit(attempt_id):
    """Secure server-side answer validation, scoring, and skill gap calculation."""
    user_id = session.get('user_id')
    attempt = db.session.get(AssessmentAttempt, attempt_id)

    if not attempt or attempt.user_id != user_id:
        return jsonify({'error': 'Unauthorized assessment attempt.'}), 403

    # Prevent duplicate submission
    if attempt.status == 'completed':
        return jsonify({
            'success': True,
            'message': 'Attempt was already submitted.',
            'redirect_url': url_for('assessment.results', attempt_id=attempt.id)
        })

    data = request.get_json() or {}
    submitted_responses = data.get('responses', {})  # { question_id: 'A'|'B'|'C'|'D' }

    # Fetch all questions answered
    question_ids = [int(qid) for qid in submitted_responses.keys() if str(qid).isdigit()]
    if not question_ids:
        return jsonify({'error': 'No responses submitted.'}), 400

    questions = AssessmentQuestion.query.filter(AssessmentQuestion.id.in_(question_ids)).all()
    questions_map = {q.id: q for q in questions}

    total_correct = 0
    total_questions = len(questions)

    # Track scores per skill: { skill_id: { 'correct': 0, 'total': 0 } }
    skill_stats = {}

    for qid_str, selected in submitted_responses.items():
        qid = int(qid_str)
        q = questions_map.get(qid)
        if not q:
            continue

        selected_clean = selected.strip().upper()
        is_correct = (selected_clean == q.correct_option.strip().upper())
        if is_correct:
            total_correct += 1

        # Record individual response in database
        resp = AssessmentResponse(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=selected_clean,
            is_correct=is_correct
        )
        db.session.add(resp)

        # Accumulate per-skill breakdown
        if q.skill_id not in skill_stats:
            skill_stats[q.skill_id] = {'correct': 0, 'total': 0}
        skill_stats[q.skill_id]['total'] += 1
        if is_correct:
            skill_stats[q.skill_id]['correct'] += 1

    # Calculate overall scores
    percentage = round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0.0

    # Role benchmark mapping for gap calculation
    role_benchmarks = {}
    if attempt.role_id:
        role_reqs = RoleSkillRequirement.query.filter_by(role_id=attempt.role_id).all()
        role_benchmarks = {r.skill_id: r.required_level for r in role_reqs}

    # Calculate and persist per-skill proficiency and gap
    for skill_id, stats in skill_stats.items():
        ratio = stats['correct'] / stats['total'] if stats['total'] > 0 else 0.0
        # Proficiency formula (1.0 to 5.0 scale)
        proficiency = round(1.0 + (ratio * 4.0), 1)

        # Gap calculation: max(0, required_level - proficiency)
        required_level = role_benchmarks.get(skill_id, 3.5)  # Default benchmark is 3.5 if no role specified
        gap = max(0.0, round(required_level - proficiency, 1))

        result = AssessmentResult(
            attempt_id=attempt.id,
            skill_id=skill_id,
            score=stats['correct'],
            max_score=stats['total'],
            proficiency_level=proficiency,
            gap_level=gap
        )
        db.session.add(result)

    # Finalize attempt status
    attempt.total_score = total_correct
    attempt.max_score = total_questions
    attempt.percentage = percentage
    attempt.status = 'completed'
    attempt.completed_at = get_utc_now()

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Assessment submitted and scored successfully.',
        'redirect_url': url_for('assessment.results', attempt_id=attempt.id)
    })


@assessment_bp.route('/results/<int:attempt_id>')
@login_required
def results(attempt_id):
    """Screen 6: Assessment Results and Skill Gap Analysis."""
    user_id = session.get('user_id')
    attempt = db.session.get(AssessmentAttempt, attempt_id)

    if not attempt or attempt.user_id != user_id:
        abort(404)

    # Fetch results associated with this attempt
    results_list = AssessmentResult.query.filter_by(attempt_id=attempt.id).all()
    
    # Target role requirements if applicable
    role_benchmarks = {}
    if attempt.role_id:
        role_reqs = RoleSkillRequirement.query.filter_by(role_id=attempt.role_id).all()
        role_benchmarks = {r.skill_id: r.required_level for r in role_reqs}

    enriched_results = []
    strengths = []
    gaps = []

    chart_labels = []
    chart_student_levels = []
    chart_required_levels = []

    for r in results_list:
        skill = r.skill
        skill_name = skill.name if skill else 'Technical Skill'
        category = skill.category if skill else 'General'

        req_level = role_benchmarks.get(r.skill_id, 3.5)
        # Consistent gap calculation
        gap = max(0.0, round(req_level - r.proficiency_level, 1))
        
        # Match percentage
        match_pct = min(100.0, round((r.proficiency_level / req_level) * 100, 1)) if req_level > 0 else 100.0

        item = {
            'skill_id': r.skill_id,
            'skill_name': skill_name,
            'category': category,
            'score': r.score,
            'max_score': r.max_score,
            'proficiency_level': r.proficiency_level,
            'required_level': req_level,
            'gap_level': gap,
            'match_pct': match_pct
        }
        enriched_results.append(item)

        chart_labels.append(skill_name)
        chart_student_levels.append(r.proficiency_level)
        chart_required_levels.append(req_level)

        if gap == 0.0 and r.proficiency_level >= 3.0:
            strengths.append(item)
        elif gap > 0.0:
            gaps.append(item)

    # Sort gaps by highest gap descending (highest priority for improvement)
    gaps.sort(key=lambda x: x['gap_level'], reverse=True)

    # Letter grade rating
    pct = attempt.percentage
    if pct >= 85:
        grade = 'A+ (Excellent)'
        grade_badge = 'badge-success'
    elif pct >= 70:
        grade = 'A (Placement Ready)'
        grade_badge = 'badge-success'
    elif pct >= 55:
        grade = 'B (Developing Competency)'
        grade_badge = 'badge-indigo'
    elif pct >= 40:
        grade = 'C (Foundational)'
        grade_badge = 'badge-warning'
    else:
        grade = 'Needs Remediation'
        grade_badge = 'badge-danger'

    return render_template(
        'assessment/results.html',
        active_page='assessment',
        attempt=attempt,
        results=enriched_results,
        strengths=strengths,
        gaps=gaps,
        grade=grade,
        grade_badge=grade_badge,
        chart_labels=chart_labels,
        chart_student_levels=chart_student_levels,
        chart_required_levels=chart_required_levels
    )
