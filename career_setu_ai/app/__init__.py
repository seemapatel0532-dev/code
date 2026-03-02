import os
from flask import Flask, render_template
from flask_login import login_required, current_user

from app.config import Config
from app.extensions import db, login_manager, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # ✅ import models for migrations
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.job_description import JobDescription
    from app.models.bulk_ranking import BulkRankingRun              # Phase 6
    from app.models.resume_profile import ResumeProfile, ResumeProfileVersion  # Phase 7

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.resume_routes import resume_bp
    from app.routes.scoring_routes import scoring_bp
    from app.routes.job_routes import jds_bp
    from app.routes.match_routes import match_bp
    from app.routes.ranker_routes import ranker_bp                 # Phase 6
    from app.routes.builder_routes import builder_bp               # Phase 7
    from app.routes.assistant_routes import assistant_bp            # Phase 8

    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(scoring_bp)
    app.register_blueprint(jds_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(ranker_bp)
    app.register_blueprint(builder_bp)
    app.register_blueprint(assistant_bp)

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return render_template("dashboard.html", page_title="Dashboard")
        return render_template("auth/login.html", page_title="Login")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        resume_count = Resume.query.filter_by(user_id=current_user.id).count()
        jd_count = JobDescription.query.filter_by(user_id=current_user.id).count()
        return render_template(
            "dashboard.html",
            page_title="Dashboard",
            resume_count=resume_count,
            jd_count=jd_count,
        )

    return app