from model import Model
from connect4 import Connect4
from typing import List
import random
from config import RewardsConfig
import jsonpickle

class Player:
    PLAYERS: List["Player"] = []
    LAST_PLAYER_ID = 0
    
    def __init__(self):
        random.seed(Player.LAST_PLAYER_ID)
        Player.LAST_PLAYER_ID += 1

        self.key: str = str(random.getrandbits(128))
        self.model: Model = None
        self.game: Connect4 = None
    
    def setup(self, model_name):
        self.model = Model(f"../models/{model_name}")
        with open("../config/config.json", 'r') as f:
            rewards_config: RewardsConfig = jsonpickle.decode(f.read()).agent_config.rewards_config
        self.game = Connect4(rewards_config, self.model.input_shape[1], self.model.input_shape[0])
    
    def play_m(self) -> bool:
        action = self.model.predict(self.game)
        return self.game.step(action, -1)[2]
    
    def play_p(self, action) -> bool:
        return self.game.step(action, 1)[2]

    @classmethod
    def create_player(cls) -> str:
        p = Player()
        cls.PLAYERS.append(p)
        return p.key
    
    @classmethod
    def does_exist(cls, player_key) -> bool:
        return player_key in [p.key for p in cls.PLAYERS]
    
    @classmethod
    def set_model(cls, player_key, model_name):
        for p in cls.PLAYERS:
            if p.key == player_key:
                p.setup(model_name)
                return p.game.board.tolist()
        return None
    
    @classmethod
    def play_model(cls, player_key):
        for p in cls.PLAYERS:
            if p.key == player_key:
                res = p.play_m()
                return {"finished": res, "board": p.game.board.tolist()}
        return None
    
    @classmethod
    def play_player(cls, player_key, action):
        for p in cls.PLAYERS:
            if p.key == player_key:
                res = p.play_p(action)
                return {"finished": res, "board": p.game.board.tolist()}
        return None