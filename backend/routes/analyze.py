import logging

from flask import Blueprint, Response, jsonify, request

from services.analyze_service import analyze_filetage
from utils.image_input import extract_image_bytes

analyze_bp = Blueprint("analyze", __name__)
logger = logging.getLogger(__name__)


@analyze_bp.post("/api/analyze")
def analyze() -> Response:
    logger.info(
        "Requête POST reçue sur /api/analyze depuis %s (Content-Type: %s)",
        request.remote_addr,
        request.content_type,
    )

    image_bytes = extract_image_bytes(request)
    logger.info("Image reçue (bytes=%d)", len(image_bytes))

    result = analyze_filetage(image_bytes)
    logger.info(
        "Analyse terminée -> diametre=%s, pas=%s, filetage=%s",
        result.get("diametre"),
        result.get("pas"),
        result.get("filetage"),
    )

    return jsonify({"success": True, **result})
