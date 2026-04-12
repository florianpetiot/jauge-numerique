from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Any
import logging

load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL et/ou SUPABASE_KEY ne sont pas définis dans les variables d'environnement.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def _get_pitch_mm(match: dict) -> float:
    """Retourne le pas en mm, quel que soit le système (métrique ou impérial)."""
    if match.get('unite') == 'I':
        return round(25.4 / match['pas'], 3) if match['pas'] != 0 else 0
    return match['pas']


def _compute_score(match: dict, mesured_diam_mm: float, tolerance_diam: float,
                   mesured_pas: float, tolerance_pas: float) -> float:
    """Calcule un score de correspondance entre 0 et 100.

    100 = correspondance parfaite (valeurs identiques).
    0   = aux limites de la tolérance.
    """
    # Score diamètre
    diam_error = abs(match['diam_mm'] - mesured_diam_mm)
    diam_score = max(0.0, 1.0 - diam_error / tolerance_diam)

    # Score pas (convertir TPI → mm pour les impériaux)
    match_pitch_mm = _get_pitch_mm(match)
    pitch_error = abs(match_pitch_mm - mesured_pas)
    pitch_score = max(0.0, 1.0 - pitch_error / tolerance_pas)

    # Score combiné (moyenne)
    score = (diam_score + pitch_score) / 2.0
    return round(score * 100, 1)


def find_match_supabase(mesured_diam_mm: float, tolerance_diam: float,
                        mesured_pas: float, tolerance_pas: float) -> list[dict]:
    diam_min = mesured_diam_mm - tolerance_diam
    diam_max = mesured_diam_mm + tolerance_diam

    pas_min_metric = mesured_pas - tolerance_pas
    pas_max_metric = mesured_pas + tolerance_pas

    pas_min_imperial = 25.4 / (mesured_pas + tolerance_pas)
    pas_max_imperial = 25.4 / (mesured_pas - tolerance_pas)

    logger.info(
        "Recherche Supabase: diam [%.2f, %.2f], pas métrique [%.2f, %.2f], pas impérial [%.2f, %.2f]",
        diam_min, diam_max, pas_min_metric, pas_max_metric, pas_min_imperial, pas_max_imperial
    )

    response = supabase.table("normes") \
        .select("*") \
        .gte("diam_mm", diam_min) \
        .lte("diam_mm", diam_max) \
        .or_(
            f"and(unite.eq.m,pas.gte.{pas_min_metric},pas.lte.{pas_max_metric}),"
            f"and(unite.eq.I,pas.gte.{pas_min_imperial},pas.lte.{pas_max_imperial})"
        ) \
        .execute()

    logger.info("Supabase a retourné %d résultat(s)", len(response.data))

    # Calculer score + pitch_mm pour chaque résultat
    scored = []
    for match in response.data:
        score = _compute_score(match, mesured_diam_mm, tolerance_diam, mesured_pas, tolerance_pas)
        pitch_mm = _get_pitch_mm(match)
        scored.append({**match, 'score': score, 'pitch_mm': pitch_mm})

    # Trier par score décroissant
    scored.sort(key=lambda x: x['score'], reverse=True)
    logger.info("Scores: %s", [(r['nom'], r['score']) for r in scored])

    # Garder les 2 meilleurs
    top = scored[:2]

    # Filtrer : score < 60 → résultat non fiable
    top = [r for r in top if r['score'] >= 60]

    # Si le meilleur score >= 90% → suffisamment confiant, un seul résultat
    if top and top[0]['score'] >= 90:
        top = [top[0]]

    logger.info("Résultats finaux: %s", [(r['nom'], r['score']) for r in top])
    return top