import flask
from flask import Flask
from flask import request
from flask import make_response
import tensorflow as tf
import numpy as np

from config import RewardsConfig
import jsonpickle
from connect4 import Connect4
import os

app = Flask("Connect4")

global game

with open("../config/config.json", 'r') as f:
    rewards_config: RewardsConfig = jsonpickle.decode(f.read()).agent_config.rewards_config

game = Connect4(rewards_config)

@app.predict("/predict", methods=['POST'])
def predict():
    q_values = current_model.predict(game.board.reshape(1, *game.board.shape))
    action = np.argmax(q_values)
    try:
        board,_,_ = game.step(action, -1)
        return {"board": board}, 200
    except Exception as e:
        return {"error": f"Erreur lors du calcul du coup IA : {str(e)}"}, 418

@app.route("/play", methods=['POST']) # Play a round
def play():
    column = request.json.get('column')
    player = request.json.get('player')
    try:
        board,_,_ = game.step(column, 1)
        return {"board": board}, 200
    except Exception as e:
        return {"error": f"Erreur lors du calcul du coup : {str(e)}"}, 418

@app.route('/available_models', methods=['GET']) # Get all available models
def available_models():
    all_files = os.listdir('models')
    model_names = [f for f in all_files if os.path.isdir(os.path.join('models', f))]
    return {"available_models": model_names}, 200

@app.route('/select_model', methods=['POST']) # Choose one of the available models
def select_model():
    global current_model
    model_name = request.json.get('model_name')

    model_path = os.path.join('models', model_name)
    if os.path.exists(model_path):
        try:
            current_model = tf.keras.models.load_model(model_path)
            return {"message": f"Modele {model_name} sélectionne avec succes!"}, 200
        except Exception as e:
            return {"error": f"Erreur lors du chargement du modele : {str(e)}"}, 500
    else:
        return {"error": "Nom de modele invalide ou modèle non trouve"}, 400

@app.route("/connect", methods=['POST']) # Ask for connection
def connect():
    password = request.json.get('password')
    if password == "Mlops2024GameAccess":
        return {"message": "Access granted"}, 200
    else:
        return {"error": "Access denied: incorrect password"}, 401

if __name__ == "__main__":
    app.run(debug=True)