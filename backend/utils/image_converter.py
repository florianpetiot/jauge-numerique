import base64
import logging
import cv2
import numpy as np
from flask import Request
from werkzeug.exceptions import BadRequest
from models.inputs import CameraInput

logger = logging.getLogger(__name__)


def convert_image_base64_to_cv2(image_base64: str) -> cv2.typing.MatLike:
    """Convertit une image encodée en base64 (data URI ou base64 pur) en format OpenCV (numpy array).

    Lève BadRequest si l'image est invalide.
    """
    
    if not isinstance(image_base64, str) or not image_base64.strip():
        raise BadRequest("image_base64 must be a non-empty string")

    logger.info("image_base64 reçue, longueur=%d", len(image_base64))
    payload = image_base64.split(",", 1)[1] if "," in image_base64 else image_base64
    try:
        image_bytes = base64.b64decode(payload)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image_cv2 = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image_cv2 is None:
            raise ValueError("cv2.imdecode returned None")
        return image_cv2
    except Exception as exc:  # noqa: BLE001
        raise BadRequest("Invalid base64 payload") from exc
