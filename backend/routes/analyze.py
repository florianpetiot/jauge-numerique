import logging

from flask import Blueprint, Response, jsonify, request

from services.analyze_service import Calibrator, crop_coin_region
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
    image_cv2 = convert_image_base64_to_cv2(body.image_base64)
    logger.info("Image reçue (shape=%s)", image_cv2.shape)

    # Focus the calibration on the coin area provided by the client overlay
    cropped = crop_coin_region(image_cv2, body.x_piece, body.y_piece, body.diameter_piece)
    logger.info("Zone recadrée pour la pièce (shape=%s)", cropped.shape)

    calib = Calibrator(REAL_DIAMETER_MM)
    mm_per_pixel, detected_diam_px = calib.calibrate(cropped)
    if not mm_per_pixel:
        logger.warning("[Analyse] Échec de la calibration : aucune pièce détectée")
        return jsonify({"success": False, "error": "Calibration failed: no piece detected"})

    logger.info(
        "[Analyse] Calibration: detected_diam_px=%.1f  overlay_diam_px=%.1f  mm_per_pixel=%.5f",
        detected_diam_px, body.diameter_piece, mm_per_pixel,
    )
    return jsonify({
        "success": True,
        "mm_per_pixel": float(mm_per_pixel),
        "detected_diameter_px": detected_diam_px,
    })
