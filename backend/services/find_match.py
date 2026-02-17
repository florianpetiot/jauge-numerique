import json
from utils.metric_conversion import TPI_to_pas, pas_to_TPI

def find_match(mesured_diam_mm: float, tolerance_diam: float, mesured_pas: float, tolerance_pas: float, dimension_filepath: str) -> list[str]:
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
            pas = TPI_to_pas(dimensions[dimension]['pas'])
        else: 
            pas = dimensions[dimension]['pas']

        if abs(pas - mesured_pas) <= tolerance_pas:
            acceptables.append(dimension)

    for acceptable in acceptables:
        print(acceptable, dimensions[acceptable])

    return acceptables

# find_match(13.2,0.1,1.24,0.1,"data/Dimensions.json")