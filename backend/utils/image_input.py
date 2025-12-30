import base64
import logging

from flask import Request
from werkzeug.exceptions import BadRequest
from models.inputs import CameraInput

logger = logging.getLogger(__name__)


def extract_image_bytes(req: CameraInput) -> bytes:
    """Extrait une image depuis l'objet CameraInput validé.

    Supporte uniquement le format JSON avec image_base64 (base64 pur ou data URI).

    Lève BadRequest si l'image est invalide.
    """
    img_base64 = req.image_base64
    if not isinstance(img_base64, str) or not img_base64.strip():
        raise BadRequest("image_base64 must be a non-empty string")

    logger.info("image_base64 reçue, longueur=%d", len(img_base64))
    payload = img_base64.split(",", 1)[1] if "," in img_base64 else img_base64
    try:
        image_bytes = base64.b64decode(payload, validate=False)
    except Exception as exc:  # noqa: BLE001
        raise BadRequest("Invalid base64 payload") from exc

    if not image_bytes:
        raise BadRequest("Failed to decode image")
    return image_bytes
