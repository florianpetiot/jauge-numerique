import cv2
import numpy as np
import math

class ThreadGauge:
    def __init__(self, w_img, h_img, initial_n_sinus=10.0):
        # État de la jauge
        self.x1, self.y1 = 100, 100
        self.x2, self.y2 = 400, 180
        self.angle = 0
        
        # Paramètres Sinus
        self.n_sinus = initial_n_sinus
        self.amplitude = 4.0
        self.phase = 0.0
        
        # État Souris
        self.mode = "idle"
        self.active_border = None
        self.offset = (0, 0)
        self.edge_thickness = 10
        
        # Dimensions image cible
        self.w_img = w_img
        self.h_img = h_img

    def _draw_sinus(self, img, x1, y1, x2):
        L = x2 - x1
        if L <= 0: return
        
        xs = np.arange(0, L+1, 1)
        # Calcul vectorisé pour performance (remplace la boucle for lente)
        angles = 2 * math.pi * (xs / L) * self.n_sinus + self.phase
        hs = self.amplitude * np.sin(angles)
        
        pxs = (x1 + xs).astype(int)
        pys = (y1 + hs).astype(int)
        
        # Filtrage des points hors limites
        mask = (pxs >= 0) & (pxs < img.shape[1]) & (pys >= 0) & (pys < img.shape[0])
        
        # On dessine point par point ou via polylines (ici point par point pour garder ton style)
        for x, y in zip(pxs[mask], pys[mask]):
            # Couleur (Blue, Green, Red, Alpha)
            img[y, x] = (255, 0, 0, 255) 

    def _detect_border(self, x, y):
        if abs(x - self.x1) < self.edge_thickness: return "left"
        if abs(x - self.x2) < self.edge_thickness: return "right"
        if abs(y - self.y1) < self.edge_thickness: return "top"
        if abs(y - self.y2) < self.edge_thickness: return "bottom"
        if self.x1 < x < self.x2 and self.y1 < y < self.y2: return "inside"
        return None

    def handle_mouse(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
            zone = self._detect_border(x, y)
            if zone == "inside":
                self.mode = "move"
                self.offset = (x - self.x1, y - self.y1)
            elif zone in ["left", "right", "top", "bottom"]:
                self.mode = "resize"
                self.active_border = zone

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mode == "move":
                dx = x - (self.x1 + self.offset[0])
                dy = y - (self.y1 + self.offset[1])
                self.x1 += dx; self.y1 += dy
                self.x2 += dx; self.y2 += dy
            elif self.mode == "resize":
                if self.active_border == "left": self.x1 = x
                if self.active_border == "right": self.x2 = x
                if self.active_border == "top": self.y1 = y
                if self.active_border == "bottom": self.y2 = y

        elif event == cv2.EVENT_LBUTTONUP:
            self.mode = "idle"
            self.active_border = None

    def handle_keys(self, k):
        # Rotation
        if k == ord("r"): self.angle = (self.angle + 1) % 360
        # Fréquence
        elif k == ord("j"): self.n_sinus = max(1, self.n_sinus - 0.5)
        elif k == ord("l"): self.n_sinus += 0.5
        # Amplitude
        elif k == ord("k"): self.amplitude = max(1.0, self.amplitude - 0.5)
        elif k == ord("i"): self.amplitude += 0.5
        # Phase
        elif k == ord("u"): self.phase -= 0.5
        elif k == ord("o"): self.phase += 0.5

    def draw_overlay(self, background_image):
        # Création overlay transparent
        overlay = np.zeros((self.h_img, self.w_img, 4), dtype=np.uint8)
        
        # Dessin Rectangle et Sinus
        cv2.rectangle(overlay, (int(self.x1), int(self.y1)), (int(self.x2), int(self.y2)), (0, 255, 255, 255), 2)
        self._draw_sinus(overlay, self.x1, self.y1, self.x2)
        self._draw_sinus(overlay, self.x1, self.y2, self.x2)

        # Rotation
        cx, cy = (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2
        M = cv2.getRotationMatrix2D((cx, cy), self.angle, 1.0)
        rotated = cv2.warpAffine(overlay, M, (self.w_img, self.h_img), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)

        # Fusion Alpha (superposition propre)
        frame = background_image.copy()
        alpha = rotated[:, :, 3] / 255.0
        for c in range(3):
            frame[:, :, c] = frame[:, :, c] * (1 - alpha) + rotated[:, :, c] * alpha
        
        return frame

    def get_pixel_metrics(self):
        w = abs(self.x2 - self.x1)
        h = abs(self.y2 - self.y1)
        return w, h, self.n_sinus