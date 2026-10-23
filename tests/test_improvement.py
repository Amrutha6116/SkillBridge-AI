import pytest
import json
from app import create_app
from extensions import db
from models.user import User
from models.skill import Skill
from models.assessment import AssessmentAttempt, AssessmentResult
from models.improvement import ImprovementPlan, ImprovementPlanTask
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

        user = User(
            full_name="Alex Vance",
            email="student@college.edu",
            register_number="2026CSE042",
            role="student"
        )
        user.set_password("student123")
        db.session.add(user)

        s1 = Skill(name="Data Structures & Algorithms", category="Core CS", description="DSA")
        db.session.add(s1)
        db.session.flush()

        attempt = AssessmentAttempt(
            user_id=user.id,
            category="Comprehensive Diagnostic",
            total_score=5,
            max_score=10,
            percentage=50.0,
            status="completed"
        )
        db.session.add(attempt)
        db.session.flush()

        res = AssessmentResult(
            attempt_id=attempt.id,
            skill_id=s1.id,
            score=1,
            max_score=3,
            proficiency_level=2.3,
            gap_level=1.7
        )
        db.session.add(res)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_improvement_plan_generation_and_fallback(client, app):
    """Test generating a personalized learning plan using deterministic fallback."""
    client.post('/auth/login', data={'identifier': 'student@college.edu', 'password': 'student123'})

    # Generate plan from attempt
    res = client.post('/improvement/generate/1', follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Verify roadmap rendered
    assert "Personalized Learning Roadmap" in html
    assert "Deterministic Rules Engine" in html or "AI Engine" in html
    assert "Placement Advisory Disclaimer" in html
    assert "Roadmap Progress" in html

    # Verify database persistence
    with app.app_context():
        plan = ImprovementPlan.query.filter_by(user_id=1).first()
        assert plan is not None
        assert plan.attempt_id == 1
        tasks = ImprovementPlanTask.query.filter_by(plan_id=plan.id).all()
        assert len(tasks) > 0
        assert any("Data Structures" in t.title or "Data Structures" in t.description or "Data Structures" in t.skill.name for t in tasks)


def test_task_status_update_via_fetch_api(client, app):
    """Test toggling task status (not_started -> completed) via Fetch API endpoint."""
    client.post('/auth/login', data={'identifier': 'student@college.edu', 'password': 'student123'})
    client.post('/improvement/generate/1')

    with app.app_context():
        task = ImprovementPlanTask.query.first()
        task_id = task.id
        assert task.status == 'not_started'

    # Update status to completed
    res = client.post(
        f'/improvement/task/{task_id}/update-status',
        data=json.dumps({'status': 'completed'}),
        content_type='application/json'
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['status'] == 'completed'
    assert data['completed_count'] == 1

    # Verify database persistence
    with app.app_context():
        updated_task = db.session.get(ImprovementPlanTask, task_id)
        assert updated_task.status == 'completed'
        assert updated_task.completed_at is not None

