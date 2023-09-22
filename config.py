import jsonpickle

class BoardConfig:
    def __init__(self):
        self.width = 7
        self.height = 6

class ModelLayerConfig:
    def __init__(self):
        self.type = "Dense"
        self.params = {
            "units": 32,
            "activation": "relu"
        }

class ModelConfig:
    def __init__(self):
        self.creation_date = "20232009"
        self.edit_date = "20232009"
        self.optimizer = "adam"
        self.loss = "mse"
        self.layers = [ModelLayerConfig(), ModelLayerConfig()]

class RewardsConfig:
    def __init__(self):
        self.forbidden_move = -50
        self.win = 15
        self.two_row = 0
        self.tree_row = 0

class AgentConfig:
    def __init__(self):
        self.rewards_config = RewardsConfig()

class TrainConfig:
    def __init__(self):
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.15
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.episodes = 25

class Config:
    def __init__(self):
        self.seed = 42
        self.board_config = BoardConfig()
        self.model_config = ModelConfig()
        self.agent_config = AgentConfig()
        self.train_config = TrainConfig()
    
    def save(self):
        with open("./config.json", 'w') as f:
            f.write(jsonpickle.encode(self, indent=4))