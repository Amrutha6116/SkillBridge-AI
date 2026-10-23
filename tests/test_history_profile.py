import pytest
from app import create_app
from extensions import db
from models.user import User
from models.assessment import AssessmentAttempt
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

        user1 = User(
            full_name="Alex Vance",
            email="alex@college.edu",
            register_number="2026CSE042",
            role="student",
            course="B.E. Computer Science",
            college="College of Engineering",
            graduation_year=2027
        )
        user1.set_password("alex123")

        user2 = User(
            full_name="Other Student",
            email="other@college.edu",
            register_number="2026CSE099",
            role="student"
        )
        user2.set_password("other123")
        db.session.add_all([user1, user2])
        db.session.flush()

        # Add attempt for user1
        att1 = AssessmentAttempt(
            user_id=user1.id,
            category="Web Development",
            total_score=8,
            max_score=10,
            percentage=80.0,
            status="completed"
        )
        # Add attempt for user2
        att2 = AssessmentAttempt(
            user_id=user2.id,
            category="Core CS",
            total_score=5,
            max_score=10,
            percentage=50.0,
            status="completed"
        )
        db.session.add_all([att1, att2])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_history_isolated_to_logged_in_user(client):
    """Test that history shows only the student's own attempts."""
    client.post('/auth/login', data={'identifier': 'alex@college.edu', 'password': 'alex123'})
    
    response = client.get('/history/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # User 1 has Web Development attempt
    assert "Web Development" in html
    assert "80.0%" in html

    # User 2's Core CS attempt should NOT appear for User 1
    assert "Core CS" not in html


def test_profile_view_and_update(client, app):
    """Test profile rendering and updating allowed details."""
    client.post('/auth/login', data={'identifier': 'alex@college.edu', 'password': 'alex123'})

    # View profile
    view_res = client.get('/profile/')
    assert view_res.status_code == 200
    html = view_res.data.decode('utf-8')
    assert "Alex Vance" in html
    assert "2026CSE042" in html

    # Update profile
    update_res = client.post('/profile/update', data={
        'full_name': 'Alexander Vance',
        'course': 'B.Tech CSE with AI Specialization',
        'college': 'Premier Institute of Tech',
        'graduation_year': '2028'
    }, follow_redirects=True)
    assert update_res.status_code == 200
    assert b"Profile details updated successfully" in update_res.data

    with app.app_context():
        u = db.session.get(User, 1)
        assert u.full_name == 'Alexander Vance'
        assert u.graduation_year == 2028


def test_password_change_success_and_failures(client, app):
    """Test password change validation, wrong password rejection, and successful update."""
    client.post('/auth/login', data={'identifier': 'alex@college.edu', 'password': 'alex123'})

    # Wrong current password
    fail_res1 = client.post('/profile/change-password', data={
        'current_password': 'wrongpass',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert b"Current password verification failed" in fail_res1.data

    # Mismatched confirmation
    fail_res2 = client.post('/profile/change-password', data={
        'current_password': 'alex123',
        'new_password': 'newpassword123',
        'confirm_password': 'mismatched123'
    }, follow_redirects=True)
    assert b"do not match" in fail_res2.data

    # Successful password change
    success_res = client.post('/profile/change-password', data={
        'current_password': 'alex123',
        'new_password': 'brandnewpass123',
        'confirm_password': 'brandnewpass123'
    }, follow_redirects=True)
    assert b"Your password has been changed securely" in success_res.data

    # Verify new password can be used to log in
    client.get('/auth/logout')
    login_new = client.post('/auth/login', data={
        'identifier': 'alex@college.edu',
        'password': 'brandnewpass123'
    }, follow_redirects=True)
    assert b"Welcome back, Alexander Vance" in login_new.data or b"Welcome back, Alex Vance" in login_new.data

