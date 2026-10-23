import os
from datetime import datetime

from flask import Flask, render_template
from config import Config
from extensions import db


def create_app(config_class=Config):
    """Application factory for SkillBridge AI."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.roles import roles_bp
    from routes.assessment import assessment_bp
    from routes.improvement import improvement_bp
    from routes.history import history_bp
    from routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(improvement_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(profile_bp)

    # Context processors for templates
    @app.context_processor
    def inject_global_data():
        return {
            "app_name": "SkillBridge AI",
            "current_year": datetime.now().year,
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    return app


# Development server entry point
if __name__ == "__main__":
    application = create_app()

    print("=" * 60)
    print("SkillBridge AI - Server Starting")
    print("Access locally at: http://127.0.0.1:5000")
    print("=" * 60)

    application.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )