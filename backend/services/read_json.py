import json
import logging
logger = logging.getLogger(__name__)

def find_match_json(mesured_diam_mm: float, tolerance_diam: float,
                        mesured_pas: float, tolerance_pas: float,dimension_filepath) -> list[dict]:
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

    with open(dimension_filepath, 'r') as file:
        dimensions = json.load(file)

    acceptable_diams = []
    for dimension in dimensions.keys():
        if abs(dimensions[dimension]['diam_mm'] - mesured_diam_mm) <= tolerance_diam:
            acceptable_diams.append(dimension)

    acceptables = []
    for dimension in acceptable_diams:
        pas = -1
        if dimensions[dimension]['unite'] == 'I':
            pas = 25.4/(dimensions[dimension]['pas'])
        else: 
            pas = dimensions[dimension]['pas']

        if abs(pas - mesured_pas) <= tolerance_pas:
            acceptables.append(dimension)
    return acceptables
