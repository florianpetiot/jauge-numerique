import base64
import logging

from flask import Request
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)


def extract_image_bytes(req: Request) -> bytes:
    """Extrait une image depuis la requête.

    Supporte:
    - JSON: {"image_base64": "..."} (base64 pur ou data URI)
    - multipart/form-data: champ fichier "image"

    Lève BadRequest si aucune image valide n'est fournie.
    """
    data = req.get_json(silent=True)

    if data and isinstance(data, dict) and "image_base64" in data:
        img_base64 = data["image_base64"]
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

    if "image" in req.files:
        file = req.files["image"]
        file_bytes = file.read()
        logger.info(
            "Fichier uploadé reçu: %s (taille=%d bytes)",
            getattr(file, "filename", "<unknown>"),
            len(file_bytes),
        )

        if not file_bytes:
            raise BadRequest("Empty uploaded file")
        return file_bytes

    keys_json = list(data.keys()) if isinstance(data, dict) else None
    logger.info(
        "Aucune image trouvée dans la requête. keys json/form: %s / %s",
        keys_json,
        list(req.form.keys()),
    )
    raise BadRequest("No image provided")
