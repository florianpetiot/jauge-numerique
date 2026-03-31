from __future__ import annotations
import cv2

def crop_coin_region(
    image: cv2.typing.MatLike, x_center: float, y_center: float, diameter_px: float, padding: float = 0.25
):
    # Crop the area around the detected coin position to simplify circle detection
    if diameter_px <= 0:
        return image

    h, w = image.shape[:2]
    radius = diameter_px * (0.5 + padding)

    x0 = max(int(x_center - radius), 0)
    y0 = max(int(y_center - radius), 0)
    x1 = min(int(x_center + radius), w)
    y1 = min(int(y_center + radius), h)

    if x1 - x0 < 2 or y1 - y0 < 2:
        return image

    return image[y0:y1, x0:x1].copy()


class Calibrator:
    def __init__(self, real_diameter_mm: float):
        self.real_diameter = real_diameter_mm
        self.mm_per_pixel = None

    def calibrate(self, image_piece: cv2.typing.MatLike) -> tuple[bool, float] | tuple[float, float]:
        gray = cv2.cvtColor(image_piece, cv2.COLOR_BGR2GRAY)
        
        h, w = gray.shape
        min_dim = min(h, w)
        
        # Flou modéré pour effacer les petites rayures sans détruire les contours des petites pièces
        blur = cv2.medianBlur(gray, 5)
        
        # L'utilisateur place la pièce dans le repère. La pièce peut être éloignée (petite) ou proche.
        # Le crop garantit que la zone pertinente est au centre de l'image.
        circles = cv2.HoughCircles(
            blur, cv2.HOUGH_GRADIENT, dp=1.2,
            minDist=min_dim // 4,  
            param1=100,            # Sensibilité Canny plus stricte pour les bords réels (métal)
            param2=35,             # Plus exigeant sur la circularité pour éviter les faux positifs
            minRadius=int(min_dim * 0.10), # La pièce peut être très petite si la caméra est loin (10% du crop)
            maxRadius=int(min_dim * 0.60)  # La pièce peut déborder légèrement du repère d'origine
        )
        
        # Fallback : si la pièce est peu contrastée, on assouplit la détection
        if circles is None:
            circles = cv2.HoughCircles(
                blur, cv2.HOUGH_GRADIENT, dp=1.2,
                minDist=min_dim // 4,
                param1=80,
                param2=20, # Redevient très tolérant sur la forme
                minRadius=int(min_dim * 0.10),
                maxRadius=int(min_dim * 0.60)
            )

        if circles is not None:
             cx_expected = w / 2.0
             cy_expected = h / 2.0
             
             valid_circles = []
             # On filtre d'abord pour s'assurer que le cercle est à peu près au centre du crop
             # (puisque l'utilisateur a ciblé la pièce avec le repère central)
             for c in circles[0]:
                 x, y, r = c
                 dist = ((x - cx_expected) ** 2 + (y - cy_expected) ** 2) ** 0.5
                 # Tolérance : le centre du cercle ne doit pas être décalé de plus de 30% de l'image
                 if dist < min_dim * 0.30:
                     valid_circles.append(c)
             
             if not valid_circles:
                 # S'ils sont tous excentrés, on prend quand même le cercle le plus "net" trouvé par OpenCV
                 valid_circles = [circles[0][0]]

             # On trie les cercles valides par leur rayon (du plus grand au plus petit).
             # Pourquoi ? Souvent, la gravure de la face forme un cercle intérieur très "net" 
             # et OpenCV le préfère au vrai bord physique de la pièce.
             # Prendre le plus grand des bons cercles concentriques permet de cibler le bord extérieur.
             valid_circles.sort(key=lambda c: c[2], reverse=True)
             
             r = valid_circles[0][2]
             
             diameter_px = float(2 * r)
             self.mm_per_pixel = self.real_diameter / diameter_px
             print(f"[Calibration] Diamètre px={diameter_px:.1f} -> Ratio={self.mm_per_pixel:.5f} mm/px")
             return self.mm_per_pixel, diameter_px

        else:
            print("[Erreur] Aucune pièce détectée pour la calibration.")
            return False, 0.0