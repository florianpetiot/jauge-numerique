from flask import Blueprint, Response, jsonify, request
import logging

from models.validation import validate_body
from models.inputs import ThreadingInput

threading_bp = Blueprint("threading", __name__)
logger = logging.getLogger(__name__)

# class ThreadingInput(BaseModel):
    # number_of_threads: int
    # width_of_thread: float

@threading_bp.post("/api/threading")
@validate_body(ThreadingInput)
def calculate_threading(body: ThreadingInput) -> Response:
    logger.info(
        "Requête POST reçue sur /api/threading depuis %s (Content-Type: %s)",
        request.remote_addr,
        request.content_type,
    )

    # Afficher en log le JSON reçu
    logger.info("Données reçues (json): %s", body)

    number_of_threads = body.number_of_threads
    width_of_thread = body.width_of_thread

    logger.info("Nombre de filets reçu: %s", number_of_threads)
    logger.info("Largeur du filet reçu: %s", width_of_thread)

    # Pour l'instant, on retourne une réponse fictive
    result = {
        "real_pitch": 1.5,  # Valeur fictive
    }
    logger.info("Calcul du pas réel terminé -> real_pitch=%s", result["real_pitch"])
    
    return jsonify({"success": True, **result})