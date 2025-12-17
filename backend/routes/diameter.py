from flask import Blueprint, Response, jsonify, request
import logging

from werkzeug.exceptions import BadRequest

diameter_bp = Blueprint("diameter", __name__)
logger = logging.getLogger(__name__)


@diameter_bp.post("/api/diameter")
def calculate_diameter() -> Response:
    logger.info(
        "Requête POST reçue sur /api/diameter depuis %s (Content-Type: %s)",
        request.remote_addr,
        request.content_type,
    )

    # Afficher en log le JSON reçu
    data = request.get_json(silent=True)
    logger.info("Données reçues (json): %s", data)

    if not isinstance(data, dict):
        logger.info("Body brut (texte): %s", request.get_data(as_text=True))
        raise BadRequest("Expected JSON body")

    transform = data.get("transform")
    if not isinstance(transform, dict):
        raise BadRequest("Missing 'transform' object")

    # Côté frontend tu envoies 'scale' (c'est le zoom)
    zoom = transform.get("scale")
    logger.info("Zoom (transform.scale) reçu: %s", zoom)


    # Pour l'instant, on retourne une réponse fictive
    result = {
        "diameter": 42.0,  # Valeur fictive
        "unit": "mm"
    }
    logger.info("Calcul du diamètre terminé -> diameter=%s %s", result["diameter"], result["unit"])

    return jsonify({"success": True, **result})