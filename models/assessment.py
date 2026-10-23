from datetime import datetime, timezone
from extensions import db


def get_utc_now():
    return datetime.now(timezone.utc)


class AssessmentQuestion(db.Model):
    """Multiple choice diagnostic question mapped to a specific skill."""
    __tablename__ = 'assessment_questions'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    difficulty = db.Column(db.String(20), default='Medium')  # 'Beginner', 'Medium', 'Advanced'
    explanation = db.Column(db.Text, nullable=True)

    # Relationships
    responses = db.relationship('AssessmentResponse', backref='question', lazy='dynamic')

    def to_client_dict(self):
        """Serialize question without revealing the correct option to the browser."""
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else 'General',
            'skill_category': self.skill.category if self.skill else 'General',
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'difficulty': self.difficulty
        }

    def __repr__(self):
        return f"<Question {self.id} (Skill={self.skill_id})>"


class AssessmentAttempt(db.Model):
    """An individual student's assessment session and calculated scores."""
    __tablename__ = 'assessment_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id', ondelete='SET NULL'), nullable=True)
    category = db.Column(db.String(80), nullable=False)  # e.g., 'Web Development', 'All Skills', 'Software Developer Assessment'
    total_score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='completed')  # 'in_progress', 'completed', 'abandoned'
    started_at = db.Column(db.DateTime, default=get_utc_now)
    completed_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    responses = db.relationship('AssessmentResponse', backref='attempt', lazy='select', cascade='all, delete-orphan')
    results = db.relationship('AssessmentResult', backref='attempt', lazy='select', cascade='all, delete-orphan')
    improvement_plans = db.relationship('ImprovementPlan', backref='attempt', lazy='dynamic')

    def __repr__(self):
        return f"<Attempt {self.id} User={self.user_id} Score={self.total_score}/{self.max_score} ({self.percentage}%)>"


class AssessmentResponse(db.Model):
    """Student's submitted answer for a specific question within an attempt."""
    __tablename__ = 'assessment_responses'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempts.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('assessment_questions.id', ondelete='CASCADE'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    is_correct = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question'),
    )

    def __repr__(self):
        return f"<Response Attempt={self.attempt_id} Q={self.question_id} Picked={self.selected_option} Valid={self.is_correct}>"


class AssessmentResult(db.Model):
    """Categorized skill proficiency and gap metrics calculated from an attempt."""
    __tablename__ = 'assessment_results'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempts.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=0)
    proficiency_level = db.Column(db.Float, default=1.0)  # Scale 1.0 - 5.0
    gap_level = db.Column(db.Float, default=0.0)  # max(0, required_level - proficiency_level)

    __table_args__ = (
        db.UniqueConstraint('attempt_id', 'skill_id', name='uq_attempt_skill'),
    )

    def __repr__(self):
        return f"<Result Attempt={self.attempt_id} Skill={self.skill_id} Level={self.proficiency_level}>"
