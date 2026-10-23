import pytest
from app import create_app
from extensions import db
from models.user import User
from models.role import JobRole, RoleSkillRequirement
from models.skill import Skill
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

        # Seed sample user
        user = User(
            full_name="Alex Vance",
            email="alex@college.edu",
            register_number="2026CSE042",
            role="student",
            course="B.E. Computer Science and Engineering",
            college="Engineering College",
            graduation_year=2027
        )
        user.set_password("alex123")
        db.session.add(user)

        # Seed sample skills
        s1 = Skill(name="HTML & CSS", category="Web Development", description="Semantic HTML")
        s2 = Skill(name="Data Structures", category="Core CS", description="Trees & Graphs")
        db.session.add_all([s1, s2])
        db.session.commit()

        # Seed sample role
        role = JobRole(
            title="Software Developer",
            category="Software Developer",
            description="Build scalable software.",
            avg_package="8 - 14 LPA",
            demand_level="Very High"
        )
        db.session.add(role)
        db.session.flush()

        req = RoleSkillRequirement(
            role_id=role.id,
            skill_id=s2.id,
            required_level=4.5,
            importance_weight=1.5
        )
        db.session.add(req)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_dashboard_unauthorized_redirects(client):
    """Test that visiting dashboard without logging in redirects to login."""
    response = client.get('/dashboard/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_dashboard_authenticated_renders(client):
    """Test dashboard renders metrics and student details for authenticated user."""
    # Login
    client.post('/auth/login', data={
        'identifier': 'alex@college.edu',
        'password': 'alex123'
    }, follow_redirects=True)

    response = client.get('/dashboard/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Personalized greeting
    assert "Welcome back, Alex Vance" in html
    assert "2026CSE042" in html

    # 4 Metric cards
    assert "Assessments Taken" in html
    assert "Skill Gaps Identified" in html
    assert "Improvement Tasks" in html
    assert "Job Roles Available" in html

    # Career Journey
    assert "Campus Placement Journey" in html
    assert "Diagnostic Assessment" in html
    assert "Skill Gap Discovery" in html


def test_job_roles_catalogue_renders(client):
    """Test job roles list and category filtering view."""
    # Login
    client.post('/auth/login', data={
        'identifier': 'alex@college.edu',
        'password': 'alex123'
    }, follow_redirects=True)

    response = client.get('/roles/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    assert "Job Roles &amp; Skill Benchmarks" in html or "Job Roles & Skill Benchmarks" in html
    assert "Software Developer" in html
    assert "Very High Demand" in html
    assert "Data Structures" in html


def test_job_role_detail_comparison(client):
    """Test individual role skill comparison page."""
    # Login
    client.post('/auth/login', data={
        'identifier': 'alex@college.edu',
        'password': 'alex123'
    }, follow_redirects=True)

    response = client.get('/roles/1')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    assert "Software Developer" in html
    assert "Benchmark Skill Comparison" in html
    assert "Data Structures" in html
    assert "4.5" in html  # Required level

