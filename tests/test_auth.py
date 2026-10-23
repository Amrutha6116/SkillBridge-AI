import pytest
from app import create_app
from extensions import db
from models.user import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'
    ADMIN_SECRET_KEY = 'test-admin-secret-2026'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_student_signup_success(client, app):
    """Test standard student registration with password hashing."""
    response = client.post('/auth/signup', data={
        'role': 'student',
        'full_name': 'Test Student',
        'email': 'newstudent@college.edu',
        'register_number': '2026CSE999',
        'password': 'securepassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='newstudent@college.edu').first()
        assert user is not None
        assert user.full_name == 'Test Student'
        assert user.role == 'student'
        assert user.password_hash != 'securepassword123'
        assert user.check_password('securepassword123') is True
        assert user.check_password('wrongpassword') is False


def test_signup_short_password_fails(client, app):
    """Test registration with password under 6 characters."""
    response = client.post('/auth/signup', data={
        'role': 'student',
        'full_name': 'Short Pass',
        'email': 'short@college.edu',
        'register_number': '2026CSE100',
        'password': '123'
    }, follow_redirects=True)
    
    assert b"Password must be at least 6 characters" in response.data
    with app.app_context():
        assert User.query.filter_by(email='short@college.edu').first() is None


def test_signup_duplicate_email_fails(client, app):
    """Test duplicate account prevention by email."""
    client.post('/auth/signup', data={
        'role': 'student',
        'full_name': 'First Student',
        'email': 'duplicate@college.edu',
        'register_number': 'REG001',
        'password': 'password123'
    })
    
    response = client.post('/auth/signup', data={
        'role': 'student',
        'full_name': 'Second Student',
        'email': 'duplicate@college.edu',
        'register_number': 'REG002',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert b"already registered" in response.data


def test_admin_signup_restricted(client, app):
    """Test that public admin creation requires institutional secret key."""
    # Fails without secret
    fail_res = client.post('/auth/signup', data={
        'role': 'admin',
        'full_name': 'Fake Admin',
        'email': 'fakeadmin@college.edu',
        'register_number': 'ADMIN999',
        'password': 'password123',
        'admin_secret': 'wrong-token'
    }, follow_redirects=True)
    assert b"Invalid Administrator Secret Token" in fail_res.data
    
    # Succeeds with correct secret
    success_res = client.post('/auth/signup', data={
        'role': 'admin',
        'full_name': 'Real Admin',
        'email': 'realadmin@college.edu',
        'register_number': 'ADMIN002',
        'password': 'password123',
        'admin_secret': 'test-admin-secret-2026'
    }, follow_redirects=True)
    assert b"Account created successfully" in success_res.data


def test_login_by_email_and_reg_no(client, app):
    """Test login with email and register number as identifiers."""
    with app.app_context():
        u = User(
            full_name="Alex Vance",
            email="alex@college.edu",
            register_number="2026CSE042",
            role="student"
        )
        u.set_password("alex1234")
        db.session.add(u)
        db.session.commit()

    # Login via Email
    res_email = client.post('/auth/login', data={
        'identifier': 'alex@college.edu',
        'password': 'alex1234'
    }, follow_redirects=True)
    assert b"Welcome back, Alex Vance" in res_email.data
    
    # Logout
    client.get('/auth/logout')

    # Login via Register Number
    res_reg = client.post('/auth/login', data={
        'identifier': '2026CSE042',
        'password': 'alex1234'
    }, follow_redirects=True)
    assert b"Welcome back, Alex Vance" in res_reg.data


def test_login_wrong_password_fails(client, app):
    """Test login rejection on incorrect password."""
    with app.app_context():
        u = User(full_name="Bob", email="bob@college.edu", register_number="BOB01")
        u.set_password("correctpass")
        db.session.add(u)
        db.session.commit()

    res = client.post('/auth/login', data={
        'identifier': 'bob@college.edu',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid email/register number or password" in res.data

