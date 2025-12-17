import logging

from flask import Flask, jsonify, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

try:
    # Exécution depuis la racine: `python -m backend.app`
    from backend.routes import register_blueprints
except ModuleNotFoundError:
    # Exécution depuis `backend/`: `python app.py`
    from routes import register_blueprints


def create_app() -> Flask:
    app = Flask(__name__)

    # Limite par défaut (à ajuster selon tes besoins)
    app.config.setdefault("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)  # 10 MB

    # CORS (permet les appels depuis le frontend)
    CORS(app)

    # Logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    # Routes
    register_blueprints(app)

    # Gestion d'erreurs centralisée (évite try/except dans chaque route)
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        response = make_response(jsonify({"success": False, "error": e.description}), e.code)
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        logger.exception("Erreur inattendue")
        if app.debug:
            response = make_response(jsonify({"success": False, "error": str(e)}), 500)
        else:
            response = make_response(jsonify({"success": False, "error": "Internal Server Error"}), 500)
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
