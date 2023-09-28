from flask import Flask
from flask import request
from flask import make_response

from player import Player
import os
from monitoring import Monitoring

app = Flask("Connect4")
m = Monitoring()


@app.route("/connect/", methods=['POST'])
def connect():
    request_json = request.json
    password = request_json.get('password')
    if password == "0":
        m.request_called("connect", True)
        return {"message": Player.create_player()}, 200
    else:
        m.request_called("connect", False)
        return {"error": "Access denied: incorrect password"}, 401

@app.route("/get_existing_models/", methods=['POST'])
def get_existing_models():
    request_json = request.json
    player_key = request_json.get('player_key')
    if not Player.does_exist(player_key):
        m.request_called("get_existing_models", False)
        return {"error": "Invalid player key"}

    m.request_called("get_existing_models", True)
    return {"message" : [os.path.basename(d) for d in os.listdir("../models") if os.path.isdir(os.path.join("../models", d))]}, 200

@app.route("/create_model/", methods=["POST"])
def create_model():
    request_json = request.json
    print(request_json)
    size = request.json.get('size')
    #agent = DQN(size, size[1], )


@app.route("/pick_model", methods=['POST'])
def pick_model():
    request_json = request.json
    player_key = request_json.get('player_key')
    model_name = request_json.get('model_name')
    board = Player.set_model(player_key, model_name)
    if board == None:
        m.request_called("pick_model", False)
        return {"error": "Invalid player key"}, 401
    m.picked_model(model_name)
    m.request_called("pick_model", True)
    return {"message": board}, 200

@app.route("/play_model", methods=['POST'])
def play_model():
    request_json = request.json
    player_key = request_json.get('player_key')
    res = Player.play_model(player_key)
    if res == None:
        m.request_called("play_model", False)
        return {"error": "Invalid player key"}, 401
    m.request_called("play_model", True)
    return {"message": res}, 200

@app.route("/play_player", methods=['POST'])
def play_player():
    request_json = request.json
    player_key = request_json.get('player_key')
    action = request_json.get('action')
    res = Player.play_player(player_key, action)
    if res == None:
        m.request_called("play_player", False)
        return {"error": "Invalid player key"}, 401
    m.request_called("play_player", True)
    return {"message": res}, 200

@app.route("/get_server_info", methods=['POST'])
def get_server_info():
    request_json = request.json
    admin_password = request_json.get('admin_password')
    if not admin_password == "admin":
        m.request_called("get_server_info", False)
        return {"error": "Invalid admin password"}, 401
    m.request_called("get_server_info", True)
    return {
        "players_amount": len(Player.PLAYERS),
        "picked_models": m.get_picked_models(),
        "requests_amount": m.get_total_requests_info(),
        "requests_timeline": m.get_timeline_date()
    }, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)