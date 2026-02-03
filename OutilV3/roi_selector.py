import cv2

class ROISelector:
    def __init__(self, image, max_w, max_h):
        self.original_image = image
        self.rectangles = []
        self.drawing = False
        self.ix, self.iy = -1, -1
        
        # Redimensionnement pour l'affichage (si l'image est trop grosse)
        h, w = image.shape[:2]
        self.scale = min(max_w / w, max_h / h, 1.0)
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        self.img_disp = cv2.resize(image, (new_w, new_h))
        self.clone = self.img_disp.copy()

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            temp = self.clone.copy()
            cv2.rectangle(temp, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Selection", temp)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            # On stocke les coordonnées affichées
            self.rectangles.append((self.ix, self.iy, x, y))
            cv2.rectangle(self.clone, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Selection", self.clone)

    def _get_crop_coords(self, rect):
        """Convertit les coords écran vers les coords image originale"""
        x1, y1, x2, y2 = rect
        xmin, xmax = sorted([x1, x2])
        ymin, ymax = sorted([y1, y2])
        return (int(xmin / self.scale), int(ymin / self.scale),
                int(xmax / self.scale), int(ymax / self.scale))

    def select(self):
        cv2.namedWindow("Selection")
        cv2.setMouseCallback("Selection", self._mouse_callback)
        
        print(">> Sélectionnez : 1. La Pièce (Calibration) -> 2. L'Objet (Vis)")
        
        while True:
            cv2.imshow("Selection", self.clone)
            key = cv2.waitKey(1)
            # Quitter si 'q' ou si on a 2 rectangles
            if key == ord("q") or len(self.rectangles) == 2:
                break
        
        cv2.destroyWindow("Selection")

        if len(self.rectangles) < 2:
            return None, None

        # Extraction des images haute résolution
        coords_piece = self._get_crop_coords(self.rectangles[0])
        coords_obj = self._get_crop_coords(self.rectangles[1])

        img_piece = self.original_image[coords_piece[1]:coords_piece[3], coords_piece[0]:coords_piece[2]]
        img_obj = self.original_image[coords_obj[1]:coords_obj[3], coords_obj[0]:coords_obj[2]]

        # On retourne aussi le facteur d'échelle global utilisé pour la sélection (info utile)
        return img_piece, img_obj