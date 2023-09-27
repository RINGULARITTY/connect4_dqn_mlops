import flask
from flask import Flask
from flask import request
from flask import make_response

from config import RewardsConfig
import jsonpickle
import game.connect4 as c4
import os

app = Flask("Connect 4")

global game

with open("../../config/config.json", 'r') as f:
    rewards_config: RewardsConfig = jsonpickle.decode(f.read()).agent_config.rewards_config

game = c4.Connect4(rewards_config)

@app.route("/play/", methods=['POST']) # Play a round
def play():
    column = request.json.get('column')
    player = request.json.get('player')
    board,_,_ = game.step(column, player)
    return {"board": board}

@app.route('/available_models', methods=['GET']) # Get all available models
def available_models():
    all_files = os.listdir('models')
    model_names = [f for f in all_files if os.path.isdir(os.path.join('models', f))]
    return {"available_models": model_names}

@app.route('/select_model', methods=['POST']) # Choose one of the available models
def select_model():
    global current_model
    model_name = request.json.get('model_name')

    model_path = os.path.join('models', model_name)
    if os.path.exists(model_path):
        try:
            current_model = tf.keras.models.load_model(model_path)
            return {"message": f"Modele {model_name} sélectionne avec succes!"}
        except Exception as e:
            return {"error": f"Erreur lors du chargement du modele : {str(e)}"}, 500
    else:
        return {"error": "Nom de modele invalide ou modèle non trouve"}, 400

if __name__ == "__main__":
    app.run(debug=True)