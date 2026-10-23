import pytest
from app import create_app
from extensions import db
from models.user import User
from models.skill import Skill
from models.assessment import AssessmentAttempt, AssessmentResult
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # Seed student
        user1 = User(
            full_name="Alex Vance",
            email="student@college.edu",
            register_number="2026CSE042",
            role="student"
        )
        user1.set_password("student123")

        user2 = User(
            full_name="Other Student",
            email="other@college.edu",
            register_number="2026CSE099",
            role="student"
        )
        user2.set_password("other123")
        db.session.add_all([user1, user2])
        db.session.flush()

        # Seed skills
        s1 = Skill(name="HTML5 & Modern CSS", category="Web Development", description="Web markup")
        s2 = Skill(name="Data Structures", category="Core CS", description="DSA")
        db.session.add_all([s1, s2])
        db.session.flush()

        # Seed attempt for user1
        attempt = AssessmentAttempt(
            user_id=user1.id,
            category="Comprehensive Diagnostic",
            total_score=8,
            max_score=10,
            percentage=80.0,
            status="completed"
        )
        db.session.add(attempt)
        db.session.flush()

        # Result 1: Strength (Level 4.5, Gap 0)
        res1 = AssessmentResult(
            attempt_id=attempt.id,
            skill_id=s1.id,
            score=4,
            max_score=4,
            proficiency_level=4.5,
            gap_level=0.0
        )
        # Result 2: Gap (Level 2.5, Gap 1.5 against 4.0 benchmark)
        res2 = AssessmentResult(
            attempt_id=attempt.id,
            skill_id=s2.id,
            score=2,
            max_score=4,
            proficiency_level=2.5,
            gap_level=1.5
        )
        db.session.add_all([res1, res2])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_results_screen_renders_for_owner(client):
    """Test that student can view their assessment results with charts and gaps."""
    client.post('/auth/login', data={'identifier': 'student@college.edu', 'password': 'student123'})
    
    response = client.get('/assessment/results/1')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Overall score & grade
    assert "Diagnostic Assessment Results" in html
    assert "80.0%" in html
    assert "8" in html
    assert "10" in html

    # Charts present
    assert 'id="barChart"' in html
    assert 'id="radarChart"' in html

    # Gaps and Strengths breakdown
    assert "Identified Skill Deficits" in html
    assert "Data Structures" in html
    assert "1.0 Level" in html or "&minus;1.0 Level" in html or "-1.0 Level" in html
    assert "Verified Strengths" in html
    assert "HTML5 &amp; Modern CSS" in html or "HTML5 & Modern CSS" in html

    # CTA to generate AI Improvement Plan
    assert "Generate AI Improvement Plan" in html


def test_results_privacy_isolation(client):
    """Test that student cannot view another student's assessment results."""
    # Log in as other student (user2)
    client.post('/auth/login', data={'identifier': 'other@college.edu', 'password': 'other123'})
    
    # Attempt 1 belongs to user1
    response = client.get('/assessment/results/1')
    assert response.status_code == 404
