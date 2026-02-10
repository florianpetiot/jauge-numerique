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


import cv2
import numpy as np


class Calibrator:
    def __init__(self, real_diameter_mm: float):
        self.real_diameter = real_diameter_mm
        self.mm_per_pixel = None

    def calibrate(self, image_piece: cv2.typing.MatLike) -> bool|float:
        gray = cv2.cvtColor(image_piece, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 7)
        
        h, w = gray.shape
        min_dim = min(h, w)
        #HoughCircles vote en faisant voter chaque pixel de contour pour tous les cercles possibles qu’il pourrait appartenir à.
        # Les cercles qui reçoivent suffisamment de votes (≥ param2) sont validés.
        circles = cv2.HoughCircles(
            #dp = (résolution image originale) / (résolution de l'accumulateur)
            blur, cv2.HOUGH_GRADIENT, dp=1.2,
            #dist minimale entre deux cercles votés 
            minDist=min_dim // 2,
            #param1 : détecte les contours plus il est haut plus on accepte que les bords net (canny) 
            #param2: décide s'il y a réellement un cercle parmi ces contours (le nombre minimum de votes nécessaires.)
            param1=80, param2=20,
            minRadius=int(min_dim * 0.25),
            maxRadius=int(min_dim * 0.45)
        )

        if circles is not None:
            # On prend le premier cercle trouvé
            r = circles[0][0][2]
            # Diamètre en pixels = 2 * rayon
            diameter_px = 2 * r
            self.mm_per_pixel = self.real_diameter / diameter_px
            print(f"[Calibration] Diamètre px={diameter_px:.1f} -> Ratio={self.mm_per_pixel:.5f} mm/px")
            return self.mm_per_pixel
        else:
            print("[Erreur] Aucune pièce détectée pour la calibration.")
            return False