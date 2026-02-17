from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all route blueprints on the Flask app."""
    from .analyze import analyze_bp
    from .health import health_bp
    from .diameter import diameter_bp
    from .findThreading import threading_bp

    app.register_blueprint(analyze_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(diameter_bp)
    app.register_blueprint(threading_bp)