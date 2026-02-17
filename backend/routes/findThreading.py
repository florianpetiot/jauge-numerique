from flask import Blueprint, Response, jsonify, request
import logging

from models.validation import validate_body
from models.inputs import ThreadingInput
from services.find_match import find_match

threading_bp = Blueprint("findThreading", __name__)
logger = logging.getLogger(__name__)

# class ThreadingInput(BaseModel):
    # number_of_threads: int
    # width_of_thread: float

@threading_bp.post("/api/findThreading")
@validate_body(ThreadingInput)
def calculate_threading(body: ThreadingInput) -> Response:
    logger.info(
        "Requête POST reçue sur /api/findThreading depuis %s (Content-Type: %s)",
        request.remote_addr,
        request.content_type,
    )

    # Afficher en log le JSON reçu
    logger.info("Données reçues (json): %s", body)

    number_of_threads = body.diameter_mm
    step_mm = body.step_mm

    result = find_match(
        mesured_diam_mm=number_of_threads,
        tolerance_diam=0.1,
        mesured_pas=step_mm,
        tolerance_pas=0.1,
        dimension_filepath="data/Dimensions.json"
    )

    
    return jsonify({"success": True, "matches": result})