import json
import logging
logger = logging.getLogger(__name__)

def _get_pitch_mm(match: dict) -> float:
    """Retourne le pas en mm, quel que soit le système (métrique ou impérial)."""
    if match.get('unite') == 'I':
        return round(25.4 / match['pas'], 3) if match['pas'] != 0 else 0
    return match['pas']

def _compute_score(match: dict, mesured_diam_mm: float, tolerance_diam: float,
                   mesured_pas: float, tolerance_pas: float) -> float:
    """Calcule un score de correspondance entre 0 et 100."""
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

def find_match_json(mesured_diam_mm: float, tolerance_diam: float,
                        mesured_pas: float, tolerance_pas: float,dimension_filepath) -> list[dict]:
    diam_min = mesured_diam_mm - tolerance_diam
    diam_max = mesured_diam_mm + tolerance_diam

    pas_min_metric = mesured_pas - tolerance_pas
    pas_max_metric = mesured_pas + tolerance_pas

    pas_min_imperial = 25.4 / (mesured_pas + tolerance_pas) if (mesured_pas + tolerance_pas) != 0 else 0
    pas_max_imperial = 25.4 / (mesured_pas - tolerance_pas) if (mesured_pas - tolerance_pas) != 0 else float('inf')

    logger.info(
        "Recherche JSON: diam [%.2f, %.2f], pas métrique [%.2f, %.2f], pas impérial [%.2f, %.2f]",
        diam_min, diam_max, pas_min_metric, pas_max_metric, pas_min_imperial, pas_max_imperial
    )

    with open(dimension_filepath, 'r') as file:
        dimensions = json.load(file)

    acceptable_matches = []
    for dimension, valeurs in dimensions.items():
        match_dict = {"nom": dimension, **valeurs}
        
        diam = match_dict['diam_mm']
        pas_mm = _get_pitch_mm(match_dict)
        
        # Filtrage initial sur les diamètres et les pas (convertis en millimètres)
        if diam_min <= diam <= diam_max and pas_min_metric <= pas_mm <= pas_max_metric:
            acceptable_matches.append(match_dict)

    scored = []
    for match in acceptable_matches:
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
