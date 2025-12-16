from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import logging

app = Flask(__name__)
CORS(app)  # Permet les appels depuis Vue localhost:5173

# Configure logging pour voir les requêtes dans la console
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze_filetage():
    try:
        logger.info("Requête POST reçue sur /api/analyze depuis %s (Content-Type: %s)", request.remote_addr, request.content_type)

        # Essaye JSON {"image_base64": "..."} d'abord
        data = request.get_json(silent=True)
        img_bytes = None

        if data and 'image_base64' in data:
            img_base64 = data['image_base64']
            logger.info("image_base64 reçue, longueur=%d", len(img_base64))
            # Supporte dataURI "data:image/...;base64,..." ou base64 pur
            payload = img_base64.split(',')[1] if ',' in img_base64 else img_base64
            img_bytes = base64.b64decode(payload)

        # Sinon accepte un upload multipart form-data avec le champ 'image'
        elif 'image' in request.files:
            file = request.files['image']
            file_bytes = file.read()
            logger.info("Fichier uploadé reçu: %s (taille=%d bytes)", file.filename, len(file_bytes))
            img_bytes = file_bytes

        else:
            logger.info("Aucune image trouvée dans la requête. keys json/form: %s / %s", 
                        list(data.keys()) if data else None, list(request.form.keys()))
            return jsonify({"success": False, "error": "No image provided"}), 400

        if not img_bytes:
            logger.error("Aucune donnée image décodable (bytes vides)")
            return jsonify({"success": False, "error": "Failed to decode image"}), 500

        # On ne dépend plus de NumPy/OpenCV/Pillow ici — on se contente d'enregistrer la taille des bytes
        logger.info("Image reçue (bytes=%d)", len(img_bytes))

        # TODO: TON ALGO FILETAGE (contours, Hough circles)
        # Pour l'instant : mock
        diametre = 10.2
        pas = 1.5
        filetage = "M10x1.5"

        logger.info("Analyse mock terminée -> diametre=%s, pas=%s, filetage=%s", diametre, pas, filetage)

        return jsonify({
            "success": True,
            "diametre": diametre,
            "pas": pas,
            "filetage": filetage
        })
    except Exception as e:
        logger.exception("Erreur lors de l'analyse")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health():
    return {"status": "OK"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
