import pytest
from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client


def test_landing_page_renders(client):
    """Test Screen 1: Landing Page renders successfully with HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # Check title and branding
    assert "SkillBridge" in html
    assert "AI" in html
    
    # Check required hero headline
    assert "Your Skills." in html
    assert "Our AI." in html
    assert "A Stronger Future." in html
    
    # Check 4 required feature highlights
    assert "Assess Your Skills" in html
    assert "Find Skill Gaps" in html
    assert "Get AI Suggestions" in html
    assert "Achieve Your Goals" in html
    
    # Check CTA buttons
    assert "Get Started" in html
    assert "Learn More" in html


def test_404_error_page(client):
    """Test 404 custom error handler."""
    response = client.get('/non-existent-page-path-123')
    assert response.status_code == 404
    assert b"Page Not Found" in response.data

