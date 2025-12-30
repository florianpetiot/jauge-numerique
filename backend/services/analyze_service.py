from __future__ import annotations


def find_scale(image_bytes: bytes, top_threading: float, bottom_threading: float,
               diameter_piece: float, x_piece: float, y_piece: float) -> dict:
    """Analyse l'image et retourne diametre/pas/filetage.

    Pour l'instant c'est un mock (à remplacer par OpenCV + ton algo).
    """
    # TODO: implémenter l'algo (contours, Hough circles, etc.)
    diametre = 10.2
    pas = 1.5
    filetage = "M10x1.5"

    return {"diametre": diametre, "pas": pas, "filetage": filetage}
