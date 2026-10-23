from extensions import db


class JobRole(db.Model):
    """Industry campus placement job roles with benchmark skill requirements."""
    __tablename__ = 'job_roles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # 'Software Developer', 'Frontend Developer', 'Web Developer', 'Data Analyst'
    description = db.Column(db.Text, nullable=False)
    min_experience = db.Column(db.String(50), default='Fresher / Campus Hire')
    avg_package = db.Column(db.String(50), default='6.5 - 12 LPA')
    demand_level = db.Column(db.String(30), default='High')  # 'Moderate', 'High', 'Very High'

    # Relationships
    requirements = db.relationship('RoleSkillRequirement', backref='job_role', lazy='joined', cascade='all, delete-orphan')
    attempts = db.relationship('AssessmentAttempt', backref='target_role', lazy='dynamic')
    improvement_plans = db.relationship('ImprovementPlan', backref='target_role', lazy='dynamic')

    def __repr__(self):
        return f"<JobRole {self.title} [{self.category}]>"


class RoleSkillRequirement(db.Model):
    """Specific skill proficiency requirements for each job role (scale 1.0 to 5.0)."""
    __tablename__ = 'role_skill_requirements'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    required_level = db.Column(db.Float, nullable=False, default=3.5)  # Proficiency scale: 1.0 - 5.0
    importance_weight = db.Column(db.Float, default=1.0)  # Relative weight in role readiness calculation

    # Uniqueness constraint to prevent duplicate requirements for the same role and skill
    __table_args__ = (
        db.UniqueConstraint('role_id', 'skill_id', name='uq_role_skill'),
    )

    def __repr__(self):
        return f"<Requirement Role={self.role_id} Skill={self.skill_id} Level={self.required_level}>"

