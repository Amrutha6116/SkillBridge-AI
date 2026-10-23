import pytest
import json
from app import create_app
from extensions import db
from models.user import User
from models.skill import Skill
from models.role import JobRole, RoleSkillRequirement
from models.assessment import AssessmentQuestion, AssessmentAttempt, AssessmentResponse, AssessmentResult
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
        user = User(
            full_name="Alex Vance",
            email="student@college.edu",
            register_number="2026CSE042",
            role="student"
        )
        user.set_password("student123")
        db.session.add(user)

        # Seed skills
        s1 = Skill(name="HTML & CSS", category="Web Development", description="Web markup")
        s2 = Skill(name="JavaScript", category="Web Development", description="JS programming")
        db.session.add_all([s1, s2])
        db.session.flush()

        # Seed questions
        q1 = AssessmentQuestion(
            skill_id=s1.id,
            question_text="What does HTML stand for?",
            option_a="Hyper Text Markup Language",
            option_b="High Tech Multi Language",
            option_c="Hyperlink Text Mode Language",
            option_d="None of the above",
            correct_option="A",
            difficulty="Beginner"
        )
        q2 = AssessmentQuestion(
            skill_id=s2.id,
            question_text="Which keyword declares a block-scoped variable in ES6?",
            option_a="var",
            option_b="let",
            option_c="def",
            option_d="int",
            correct_option="B",
            difficulty="Beginner"
        )
        db.session.add_all([q1, q2])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_assessment_hub_renders(client):
    """Test that assessment hub renders category options."""
    client.post('/auth/login', data={'identifier': 'student@college.edu', 'password': 'student123'})
    response = client.get('/assessment/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Diagnostic Center" in html
    assert "Comprehensive Diagnostic" in html
    assert "Web Development" in html


def test_assessment_start_and_take(client, app):
    """Test initializing an assessment and loading the question taker."""
    client.post('/auth/login', data={'identifier': 'student@college.edu', 'password': 'student123'})
    
    # Start assessment
    res = client.post('/assessment/start', data={'assessment_type': 'Web Development'}, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Question text should be present, but correct answers must NOT be exposed
    assert "What does HTML stand for?" in html
    assert "Which keyword declares a block-scoped variable in ES6?" in html
    assert "correct_option" not in html


def test_assessment_submission_and_server_scoring(client, app):
    """Test submitting answers, calculating score on server, and checking result records."""
    client.post('/auth/login', data={'identifier': 'student@college.edu', 'password': 'student123'})
    
    # Start attempt
    client.post('/assessment/start', data={'assessment_type': 'Web Development'})
    with app.app_context():
        attempt = AssessmentAttempt.query.first()
        attempt_id = attempt.id
        q1 = AssessmentQuestion.query.filter_by(correct_option="A").first()
        q2 = AssessmentQuestion.query.filter_by(correct_option="B").first()
        q1_id = q1.id
        q2_id = q2.id

    # Submit 1 correct ('A') and 1 wrong ('A' instead of 'B')
    res = client.post(
        f'/assessment/submit/{attempt_id}',
        data=json.dumps({
            'responses': {
                str(q1_id): 'A',
                str(q2_id): 'A'
            }
        }),
        content_type='application/json'
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert f"/assessment/results/{attempt_id}" in data['redirect_url']

    # Verify database persistence & server scoring
    with app.app_context():
        updated_attempt = db.session.get(AssessmentAttempt, attempt_id)
        assert updated_attempt.status == 'completed'
        assert updated_attempt.total_score == 1
        assert updated_attempt.max_score == 2
        assert updated_attempt.percentage == 50.0

        # Check recorded responses
        responses = AssessmentResponse.query.filter_by(attempt_id=attempt_id).all()
        assert len(responses) == 2
        correct_flags = {r.question_id: r.is_correct for r in responses}
        assert correct_flags[q1_id] is True
        assert correct_flags[q2_id] is False

        # Check calculated results
        results = AssessmentResult.query.filter_by(attempt_id=attempt_id).all()
        assert len(results) == 2
