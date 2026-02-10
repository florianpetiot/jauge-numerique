import logging

from flask import Blueprint, Response, jsonify, request

from services.analyze_service import Calibrator
from utils.constants import REAL_DIAMETER_MM
from utils.image_converter import convert_image_base64_to_cv2
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
    image_cv2 =  convert_image_base64_to_cv2(body.image_base64)
    logger.info("Image reçue (shape=%s)", image_cv2.shape)

    # result = find_scale(image_cv2, body.top_threading, body.bottom_threading,
    #                     body.diameter_piece, body.x_piece, body.y_piece)

    calib = Calibrator(REAL_DIAMETER_MM)
    mm_per_pixel = calib.calibrate(image_cv2)
    if not mm_per_pixel:
        logger.warning("[Analyse] Échec de la calibration : aucune pièce détectée")
        return jsonify({"success": False, "error": "Calibration failed: no piece detected"})

    logger.info(f"[Analyse] Résultat de la calibration: mm_per_pixel={mm_per_pixel:.5f}")
    return jsonify({"success": True, "mm_per_pixel": float(mm_per_pixel)})
