from config import Config, BoardConfig, ModelConfig, ModelLayerConfig, AgentConfig, RewardsConfig, TrainConfig
import jsonpickle
from datetime import datetime
from typing import List
from model_layers import LAYER_TYPES
import random
from connect4 import Connect4
import numpy as np
from model import DQN
import tensorflow as tf

class Environment:
    instance: "Environment" = None
    
    def __init__(self):       
        self.config: Config = None
        self.connect4: Connect4 = None
        self.model: DQN = None

class Test_01_Config:
    def test_00_init(self):
        Environment.instance = Environment()

    def test_01_config_load(self):
        with open("../config/config.json", 'r') as f:
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
        creation_date = datetime.strptime(model_config.creation_date, "%Y%m%d")
        edit_date = datetime.strptime(model_config.edit_date, "%Y%m%d")
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

class Test_02_Seed:
    def test_03_set_seed(self):
        config: Config = Environment.instance.config
        tf.random.set_seed(config.seed)
        random.seed(config.seed)
        np.random.seed(config.seed)

class Test_03_Connect4:
    def test_04_create_connect4(self):
        config: Config = Environment.instance.config
        Environment.instance.connect4 = Connect4(config.agent_config.rewards_config, config.board_config.width, config.board_config.height)
        c4 = Environment.instance.connect4
        c4.reset()
        assert np.all(c4.board == np.zeros((config.board_config.height, config.board_config.width), dtype=np.int8))
        assert c4.step(-1, -1)[1:] == (config.agent_config.rewards_config.forbidden_move, True)
        c4.reset()
        assert c4.step(config.board_config.width, -1)[1:] == (config.agent_config.rewards_config.forbidden_move, True)
    
    def test_05_connect4_game_1(self):
        '''Only 1 player filling first column
        '''
        config: Config = Environment.instance.config
        c4: Connect4 = Environment.instance.connect4
        c4.reset()
        
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and reward == 0 and done == False
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and board[1, 0] == -1 and reward == config.agent_config.rewards_config.two_row and done == False
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and board[1, 0] == -1 and board[2, 0] == -1 and reward == config.agent_config.rewards_config.tree_row and done == False
        board, reward, done = c4.step(0, -1)
        assert board[0, 0] == -1 and board[1, 0] == -1 and board[2, 0] == -1 and board[3, 0] == -1 and reward == config.agent_config.rewards_config.win and done

class Test_04_Model:
    def test_06_create_model(self):
        config: Config = Environment.instance.config
        c4: Connect4 = Environment.instance.connect4
        
        Environment.instance.model = DQN(c4.board.shape, config.board_config.width, config.model_config)
        
    def test_07_play_model(self):
        c4: Connect4 = Environment.instance.connect4
        model: DQN = Environment.instance.model
        c4.reset()
        
        done = False
        rewards_p, rewards_m = 0, 0
        while not done:
            q_values = model.model.predict(c4.board.reshape(1, *c4.board.shape), verbose=0)
            action = np.argmax(q_values)
            _, rewards, done = c4.step(action, -1)
            rewards_p += rewards
            
            q_values = model.target_model.predict(c4.board.reshape(1, *c4.board.shape), verbose=0)
            action = np.argmax(q_values)
            _, rewards, done = c4.step(action, 1)
            rewards_m += rewards
        
        print()
        print(f"Rewards P: {rewards_p}, Rewards M: {rewards_m}")
        c4.display()
        
        assert abs(np.count_nonzero(c4.board == -1) - np.count_nonzero(c4.board == 1)) <= 1
    
class Test_04_Train:
    def test_08_train_model(self):
        train_config: TrainConfig = Environment.instance.config.train_config
        c4: Connect4 = Environment.instance.connect4
        model: DQN = Environment.instance.model
        c4.reset()
        
        print()
        model.train(c4, train_config.gamma, train_config.epsilon, train_config.epsilon_min, train_config.epsilon_decay, train_config.batch_size, train_config.episodes)
    
class Test_05_Test:
    def test_09_test_model(self):
        rewards_config: RewardsConfig = Environment.instance.config.agent_config.rewards_config
        c4: Connect4 = Environment.instance.connect4
        model: DQN = Environment.instance.model
        c4.reset()
        
        print()
        average_rewards = model.test(c4, rewards_config, 100)
        print(f"Average rewards per game {average_rewards}")

class Test_06_Save:
    def test_10_test_model(self):
        config: Config = Environment.instance.config
        model: DQN = Environment.instance.model
        
        layers_name = "_".join([l.type for l in config.model_config.layers])
        model.save_model(f"{model.input_shape[0]}x{model.input_shape[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{layers_name}", config)