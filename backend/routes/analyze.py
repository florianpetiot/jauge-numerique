import logging

from flask import Blueprint, Response, jsonify, request

from services.analyze_service import find_scale
from utils.image_input import extract_image_bytes
from models.inputs import CameraInput
from models.validation import validate_body

analyze_bp = Blueprint("analyze", __name__)
logger = logging.getLogger(__name__)


@analyze_bp.post("/api/analyze")
@validate_body(CameraInput)
def analyze(body: CameraInput) -> Response:
    logger.info(
        "Requête POST reçue sur /api/analyze depuis %s (Content-Type: %s)",
        request.remote_addr,
        request.content_type,
    )

    # Utilisez body au lieu de request pour extraire les données validées
    image_bytes = extract_image_bytes(body)
    logger.info("Image reçue (bytes=%d)", len(image_bytes))

    result = find_scale(image_bytes, body.top_threading, body.bottom_threading,
                        body.diameter_piece, body.x_piece, body.y_piece)
    logger.info(
        "Analyse terminée -> diametre=%s, pas=%s, filetage=%s",
        result.get("diametre"),
        result.get("pas"),
        result.get("filetage"),
    )

    return jsonify({"success": True, **result})
