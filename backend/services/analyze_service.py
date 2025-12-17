from __future__ import annotations


def analyze_filetage(image_bytes: bytes) -> dict:
    """Analyse l'image et retourne diametre/pas/filetage.

    Pour l'instant c'est un mock (à remplacer par OpenCV + ton algo).
    """
    # TODO: implémenter l'algo (contours, Hough circles, etc.)
    diametre = 10.2
    pas = 1.5
    filetage = "M10x1.5"

    return {"diametre": diametre, "pas": pas, "filetage": filetage}
