import cv2
import config
from roi_selector import ROISelector
from calibrator import Calibrator
from gauge import ThreadGauge

def main():
    # 1. Configuration initiale
    try:
        user_input = input("Nombre de sinusoïdes au départ (ex: 10, Entrée pour défaut) : ")
        n_sinus = float(user_input) if user_input.strip() else 10.0
    except ValueError:
        n_sinus = 10.0

    # 2. Chargement Image
    img = cv2.imread(config.DEFAULT_IMAGE_PATH)
    if img is None:
        print(f"ERREUR: Image introuvable à {config.DEFAULT_IMAGE_PATH}")
        return

    # 3. Sélection des Zones
    selector = ROISelector(img, config.MAX_W, config.MAX_H)
    img_piece, img_obj = selector.select()

    if img_piece is None or img_obj is None:
        print("Sélection annulée.")
        return

    # 4. Calibration
    calib = Calibrator(config.REAL_DIAMETER_MM)
    if not calib.calibrate(img_piece):
        return

    # 5. Préparation de l'objet à mesurer (Grossissement)
    # On agrandit l'objet pour mieux voir (Display Scale)
    obj_big = cv2.resize(img_obj, None, fx=config.DISPLAY_SCALE, fy=config.DISPLAY_SCALE)
    h_big, w_big = obj_big.shape[:2]

    # 6. Initialisation de la Jauge
    gauge = ThreadGauge(w_big, h_big, initial_n_sinus=n_sinus)

    # 7. Boucle principale
    window_name = "Mesure de Filetage"
    cv2.namedWindow(window_name)
    
    # Callback souris relié à la méthode de l'objet gauge
    def mouse_wrapper(event, x, y, flags, param):
        gauge.handle_mouse(event, x, y)
    
    cv2.setMouseCallback(window_name, mouse_wrapper)

    print("\nCommandes : SOURIS(Bouger/Redim), R(Rotation), J/L(Freq), K/I(Amp), U/O(Phase), V(Valider)")

    while True:
        # Dessin
        final_frame = gauge.draw_overlay(obj_big)
        
        # Info texte
        info = f"Sinus: {gauge.n_sinus:.1f} | Amp: {gauge.amplitude:.1f} | Angle: {gauge.angle}"
        cv2.putText(final_frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow(window_name, final_frame)

        # Gestion Clavier
        k = cv2.waitKey(20) & 0xFF
        if k == ord('v'): # Valider
            break
        elif k == 27: # Echap
            print("Annulation.")
            cv2.destroyAllWindows()
            return
        
        gauge.handle_keys(k)

    cv2.destroyAllWindows()

    # 8. Calculs Finaux
    w_px, h_px, n_sinus_final = gauge.get_pixel_metrics()
    
    # Attention aux échelles :
    # Les pixels de la jauge sont sur l'image zoomée par DISPLAY_SCALE.
    # On doit revenir aux pixels de l'image originale (img_obj), qui était à l'échelle 1:1 par rapport à img_piece (car découpée dedans).
    
    # 1. Ramener à l'échelle du crop (dé-zoomer l'affichage)
    width_crop = w_px / config.DISPLAY_SCALE
    height_crop = h_px / config.DISPLAY_SCALE
    
    # 2. Convertir en mm
    width_mm = width_crop * calib.mm_per_pixel
    diameter_mm = height_crop * calib.mm_per_pixel
    pitch_mm = width_mm / n_sinus_final if n_sinus_final > 0 else 0

    print("\n===== RÉSULTATS =====")
    print(f"Diamètre estimé : {diameter_mm:.2f} mm")
    print(f"Longueur zone   : {width_mm:.2f} mm")
    print(f"Nombre de filets: {n_sinus_final}")
    print(f"Pas (Pitch)     : {pitch_mm:.3f} mm")
    print("=====================\n")

if __name__ == "__main__":
    main()