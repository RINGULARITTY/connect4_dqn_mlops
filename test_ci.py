from config import Config, BoardConfig, ModelConfig, ModelLayerConfig, AgentConfig, RewardsConfig, TrainConfig
import jsonpickle
from datetime import datetime
from typing import List
from model_layers import LAYER_TYPES
import random
from connect4 import Connect4
import numpy as np
import pytest
import tensorflow as tf

class Environment:
    instance: "TestsEnvironment" = None
    
    def __init__(self):       
        self.config: Config = None
        self.connect4: Connect4 = None

class Test01Config:
    def test_00_init(self):
        Environment.instance = Environment()

    def test_01_config_load(self):
        with open("./config.json", 'r') as f:
            Environment.instance.config = jsonpickle.decode(f.read())

    def test_02_config_correct(self):
        config: Config = Environment.instance.config
        assert isinstance(config, Config)
        
        board_config: BoardConfig = config.board_config
        assert isinstance(board_config, BoardConfig)
        assert board_config.width > 0
        assert board_config.height > 0
        
        model_config: ModelConfig = config.model_config
        assert isinstance(model_config, ModelConfig)
        creation_date = datetime.strptime(model_config.creation_date, "%Y%d%m")
        edit_date = datetime.strptime(model_config.edit_date, "%Y%d%m")
        assert creation_date <= edit_date <= datetime.now()

        assert model_config.optimizer.lower() in [
            "sgd",
            "rmsprop",
            "adam",
            "adamw",
            "adadelta",
            "adagrad",
            "adamax",
            "adafactor",
            "nadam",
            "ftrl"
        ]
        assert model_config.loss.lower() in [
            "kld",
            "mae",
            "mape",
            "mse",
            "msle",
            "binary_crossentropy",
            "binary_focal_crossentropy",
            "categorical_crossentropy",
            "categorical_focal_crossentropy",
            "categorical_hinge",
            "cosine_similarity",
            "hinge",
            "huber",
            "kl_divergence",
            "kullback_leibler_divergence",
            "log_cosh",
            "logcosh",
            "poisson",
            "squared_hinge"
        ]
        
        model_layers_config: List[ModelLayerConfig] = model_config.layers
        assert len(model_layers_config) > 0
        for l in model_layers_config:
            assert isinstance(l, ModelLayerConfig)
            assert l.type.lower() in LAYER_TYPES

            params: dict = l.params
            if "units" in params:
                assert params["units"] > 0
            if "activation" in params:
                assert params["activation"].lower() in ["relu", "softmax", "leakyrelu", "prelu", "elu", "tresholded"]
        
        agent_config: AgentConfig = config.agent_config
        assert isinstance(agent_config, AgentConfig)
        assert isinstance(agent_config.rewards_config, RewardsConfig)
        
        train_config: TrainConfig = config.train_config
        assert isinstance(train_config, TrainConfig)
        assert train_config.epsilon >= train_config.epsilon_min
        assert train_config.batch_size > 0

class Test02Seed:
    def test_03_set_seed(self):
        config: Config = Environment.instance.config
        tf.random.set_seed(config.seed)
        random.seed(config.seed)

class Test03Connect4:
    def test_04_create_connect4(self):
        config: Config = Environment.instance.config
        Environment.instance.connect4 = Connect4(config.agent_config.rewards_config, config.board_config.width, config.board_config.height)
        c4 = Environment.instance.connect4
        c4.reset()
        assert np.all(c4.board == np.zeros((config.board_config.height, config.board_config.width), dtype=np.int8))
        assert c4.step(-1, -1)[1:] == (config.agent_config.rewards_config.forbidden_move, True)
        assert c4.step(config.board_config.width, -1)[1:] == (config.agent_config.rewards_config.forbidden_move, True)
    
    def test_05_connect4_game_1(self):
        '''Only 1 player filling first column
        '''
        config: Config = Environment.instance.config
        c4 = Environment.instance.connect4
        c4.reset()
        
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and reward == 0 and done == False
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and board[1, 0] == -1 and reward == config.agent_config.rewards_config.two_row and done == False
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and board[1, 0] == -1 and board[2, 0] == -1 and reward == config.agent_config.rewards_config.tree_row and done == False
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and board[1, 0] == -1 and board[2, 0] == -1 and board[3, 0] == -1 and reward == config.agent_config.rewards_config.win and done