from extensions import db


class Skill(db.Model):
    """Technical and aptitude skills evaluated by the diagnostic system."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # 'Web Development', 'Core CS', 'Data & AI', 'Aptitude'
    description = db.Column(db.Text, nullable=True)

    # Relationships
    questions = db.relationship('AssessmentQuestion', backref='skill', lazy='dynamic')
    role_requirements = db.relationship('RoleSkillRequirement', backref='skill', lazy='dynamic')
    assessment_results = db.relationship('AssessmentResult', backref='skill', lazy='dynamic')
    plan_tasks = db.relationship('ImprovementPlanTask', backref='skill', lazy='dynamic')

    def __repr__(self):
        return f"<Skill {self.name} [{self.category}]>"

