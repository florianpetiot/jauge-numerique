Outil de Mesure de Filetage (Computer Vision)
Présentation

Cet outil est une application interactive de vision par ordinateur permettant de mesurer des objets filetés (ex. vis) à partir d’une image unique.
Il combine calibration d’échelle, sélection de régions d’intérêt (ROI) et ajustement manuel d’un modèle sinusoïdal afin d’estimer des dimensions physiques telles que le diamètre, le pas de filetage et le nombre de filets, en s’appuyant sur OpenCV.

Le fonctionnement est volontairement semi-automatique : les traitements automatiques sont utilisés lorsqu’ils sont robustes, et l’interaction utilisateur intervient lorsque la vision pure devient ambiguë (alignement des filets).

Workflow global

Chargement d’une image contenant :

un objet de référence de dimensions connues (pièce)

l’objet fileté à mesurer

Sélection manuelle par l’utilisateur :

ROI 1 : objet de référence (calibration)

ROI 2 : objet fileté

Calibration automatique de l’échelle pixel → millimètre

Superposition interactive d’une jauge sinusoïdale sur l’objet

Ajustement manuel de la jauge par l’utilisateur

Calcul et affichage des mesures physiques finales

Pipeline de traitement d’image et de données utilisateur

Sélection des ROI

L’utilisateur trace deux rectangles sur une image redimensionnée

Les coordonnées sont reconverties vers la résolution originale

Calibration (Pixel → mm)

Conversion en niveaux de gris

Réduction du bruit par filtre médian

Détection de contours circulaires par transformée de Hough

Calcul du ratio millimètre par pixel à partir du diamètre réel connu

Préparation de l’objet à mesurer

Zoom d’affichage pour améliorer la précision visuelle

Conservation de l’échelle réelle pour les calculs finaux

Interaction utilisateur

Déplacement et redimensionnement de la jauge à la souris

Ajustement clavier de la fréquence, amplitude, phase et rotation

Validation explicite par l’utilisateur

Calculs finaux

Conversion des mesures pixel vers l’échelle réelle

Calcul du diamètre, de la longueur analysée et du pas de filetage

Techniques de contouring et de vision utilisées

Filtre médian pour la réduction du bruit tout en préservant les bords

Transformée de Hough pour les cercles :

Détection robuste de l’objet de calibration

Tolérance aux contours incomplets et aux variations d’éclairage

Ajustement sinusoïdal manuel :

Évite les erreurs des méthodes automatiques sur textures complexes

L’alignement visuel humain garantit une meilleure fiabilité

Superposition avec canal alpha :

Affichage non destructif

Séparation claire entre image source et couche de mesure

Structure des fichiers et rôles
main.py

Point d’entrée de l’application.
Gère l’ensemble du pipeline :

saisie utilisateur

chargement de l’image

sélection des ROI

calibration

interaction de mesure

calculs finaux et affichage des résultats

config.py

Fichier de configuration centralisé :

constantes physiques (diamètre réel de référence)

paramètres d’affichage

couleurs

chemin de l’image par défaut

Permet d’ajuster le comportement sans modifier la logique.

roi_selector.py

Gestion de la sélection interactive des zones d’intérêt :

affichage redimensionné pour l’ergonomie

gestion des événements souris

conversion des coordonnées écran vers l’image originale

Retourne les crops haute résolution.

calibrator.py

Responsable de la calibration métrique :

détection de l’objet de référence

calcul du ratio mm/pixel

validation de la calibration

Implémente la détection de cercles via OpenCV.

gauge.py

Implémente la jauge de mesure interactive :

rectangle de sélection

modèle sinusoïdal représentant le filetage

gestion souris (déplacement / redimensionnement)

gestion clavier (fréquence, amplitude, phase, rotation)

rendu avec transparence (alpha blending)

Expose les métriques en pixels nécessaires aux calculs finaux.