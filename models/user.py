from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


def get_utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    """User model representing Students and Placement Administrators."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    register_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    
    # Profile & Academic Details
    course = db.Column(db.String(120), default='B.E. Computer Science and Engineering')
    college = db.Column(db.String(150), default='School of Engineering & Technology')
    graduation_year = db.Column(db.Integer, default=2027)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    attempts = db.relationship('AssessmentAttempt', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    improvement_plans = db.relationship('ImprovementPlan', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and store the password securely with PBKDF2:SHA256."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify the password against the stored cryptographic hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user has administrator privileges."""
        return self.role == 'admin'

    def to_dict(self):
        """Serialize safe public user profile dictionary."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'register_number': self.register_number,
            'role': self.role,
            'course': self.course,
            'college': self.college,
            'graduation_year': self.graduation_year,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.register_number} ({self.role}) - {self.email}>"
