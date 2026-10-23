from flask import Blueprint, render_template, session, abort
from extensions import db
from models.user import User
from models.role import JobRole
from models.assessment import AssessmentAttempt, AssessmentResult
from routes.auth import login_required

roles_bp = Blueprint('roles', __name__, url_prefix='/roles')


def get_student_proficiencies(user_id):
    """Retrieve student's latest measured skill proficiencies from database."""
    if not user_id:
        return {}
        
    latest_attempt = AssessmentAttempt.query.filter_by(user_id=user_id, status='completed')\
        .order_by(AssessmentAttempt.completed_at.desc()).first()
        
    if not latest_attempt:
        return {}

    results = AssessmentResult.query.filter_by(attempt_id=latest_attempt.id).all()
    return {r.skill_id: r.proficiency_level for r in results}


@roles_bp.route('/')
@login_required
def index():
    """Screen 7: Job Roles Catalogue and Skill Comparison."""
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    roles = JobRole.query.all()
    proficiencies = get_student_proficiencies(user_id)
    has_assessed = len(proficiencies) > 0

    enriched_roles = []
    for r in roles:
        req_comparisons = []
        total_weighted_match = 0.0
        total_weight = 0.0

        for req in r.requirements:
            student_level = proficiencies.get(req.skill_id, 0.0)
            gap = max(0.0, round(req.required_level - student_level, 1))
            match_pct = min(100.0, round((student_level / req.required_level) * 100, 1)) if req.required_level > 0 else 100.0

            weight = req.importance_weight or 1.0
            total_weighted_match += (match_pct * weight)
            total_weight += weight

            req_comparisons.append({
                'skill_id': req.skill_id,
                'skill_name': req.skill.name if req.skill else 'General Skill',
                'skill_category': req.skill.category if req.skill else 'Tech',
                'required_level': req.required_level,
                'student_level': student_level,
                'gap': gap,
                'match_pct': match_pct
            })

        overall_readiness = round(total_weighted_match / total_weight, 1) if total_weight > 0 else 0.0

        enriched_roles.append({
            'role': r,
            'requirements': req_comparisons,
            'overall_readiness': overall_readiness,
            'critical_gaps_count': sum(1 for c in req_comparisons if c['gap'] > 0.8)
        })

    # Categories for filter pills
    categories = ['All', 'Software Developer', 'Frontend Developer', 'Web Developer', 'Data Analyst']

    return render_template(
        'roles/index.html',
        active_page='roles',
        roles=enriched_roles,
        categories=categories,
        has_assessed=has_assessed
    )


@roles_bp.route('/<int:role_id>')
@login_required
def detail(role_id):
    """Detailed role specification and granular skill difference comparison."""
    role = db.session.get(JobRole, role_id)
    if not role:
        abort(404)

    user_id = session.get('user_id')
    proficiencies = get_student_proficiencies(user_id)
    has_assessed = len(proficiencies) > 0

    comparisons = []
    total_weighted_match = 0.0
    total_weight = 0.0

    for req in role.requirements:
        student_level = proficiencies.get(req.skill_id, 0.0)
        gap = max(0.0, round(req.required_level - student_level, 1))
        match_pct = min(100.0, round((student_level / req.required_level) * 100, 1)) if req.required_level > 0 else 100.0

        weight = req.importance_weight or 1.0
        total_weighted_match += (match_pct * weight)
        total_weight += weight

        comparisons.append({
            'skill_id': req.skill_id,
            'skill_name': req.skill.name if req.skill else 'General Skill',
            'skill_category': req.skill.category if req.skill else 'Tech',
            'required_level': req.required_level,
            'student_level': student_level,
            'gap': gap,
            'match_pct': match_pct
        })

    overall_readiness = round(total_weighted_match / total_weight, 1) if total_weight > 0 else 0.0

    return render_template(
        'roles/detail.html',
        active_page='roles',
        role=role,
        comparisons=comparisons,
        overall_readiness=overall_readiness,
        has_assessed=has_assessed
    )
