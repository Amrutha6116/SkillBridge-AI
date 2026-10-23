from datetime import datetime, timezone
from extensions import db


def get_utc_now():
    return datetime.now(timezone.utc)


class ImprovementPlan(db.Model):
    """Personalized learning plan generated from assessment diagnostics and target role."""
    __tablename__ = 'improvement_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempts.id', ondelete='SET NULL'), nullable=True)
    target_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(160), nullable=False)
    generated_by = db.Column(db.String(30), default='fallback')  # 'ai' or 'fallback'
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    tasks = db.relationship('ImprovementPlanTask', backref='plan', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Plan {self.id} for User={self.user_id} Role={self.target_role_id} [{self.generated_by}]>"


class ImprovementPlanTask(db.Model):
    """Actionable learning task with status progression (not started / in progress / completed)."""
    __tablename__ = 'improvement_plan_tasks'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('improvement_plans.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium')  # 'High', 'Medium', 'Low'
    current_level = db.Column(db.Float, default=1.0)
    target_level = db.Column(db.Float, default=4.0)
    estimated_duration = db.Column(db.String(50), default='1-2 weeks')
    status = db.Column(db.String(20), default='not_started')  # 'not_started', 'in_progress', 'completed'
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Serialize task for Fetch API client updates."""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else 'General',
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'current_level': self.current_level,
            'target_level': self.target_level,
            'estimated_duration': self.estimated_duration,
            'status': self.status
        }

    def __repr__(self):
        return f"<PlanTask {self.id} [{self.priority}] {self.title} Status={self.status}>"
