from flask import Flask, request, jsonify
import tensorflow as tf

app = Flask(__name__)

current_model = None

import os

@app.route('/available_models', methods=['GET'])
def available_models():
    all_files = os.listdir('models')
    model_names = [f for f in all_files if os.path.isdir(os.path.join('models', f))]
    return jsonify({"available_models": model_names})



@app.route('/select_model', methods=['POST'])
def select_model():
    global current_model
    model_name = request.json.get('model_name')

    # Vérifier si le modèle existe dans le dossier "models"
    model_path = os.path.join('models', model_name)
    if os.path.exists(model_path):
        try:
            current_model = tf.keras.models.load_model(model_path)
            return jsonify({"message": f"Modele {model_name} sélectionne avec succes!"})
        except Exception as e:
            return jsonify({"error": f"Erreur lors du chargement du modele : {str(e)}"}), 500
    else:
        return jsonify({"error": "Nom de modele invalide ou modèle non trouve"}), 400

if __name__ == "__main__":
    app.run(debug=True)
