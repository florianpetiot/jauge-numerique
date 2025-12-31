from flask import Blueprint, Response, jsonify, request
import logging

from werkzeug.exceptions import BadRequest
from models.validation import validate_body
from models.inputs import DiameterInput

diameter_bp = Blueprint("diameter", __name__)
logger = logging.getLogger(__name__)


@diameter_bp.post("/api/diameter")
@validate_body(DiameterInput)
def calculate_diameter(body: DiameterInput) -> Response:
    logger.info(
        "Requête POST reçue sur /api/diameter depuis %s (Content-Type: %s)",
        request.remote_addr,
        request.content_type,
    )

    # Afficher en log le JSON reçu
    logger.info("Données reçues (json): %s", body)

    transform = body.transform

    # Accéder aux propriétés via l'objet modèle (pas comme un dict)
    zoom = transform.scale
    logger.info("Zoom (transform.scale) reçu: %s", zoom)

    # Pour l'instant, on retourne une réponse fictive
    result = {
        "diameter": 42.0,  # Valeur fictive
        "unit": "mm"
    }
    logger.info("Calcul du diamètre terminé -> diameter=%s %s", result["diameter"], result["unit"])

    return jsonify({"success": True, **result})