import tensorflow as tf
from config import Config, ModelConfig, RewardsConfig
from model_layers import LAYER_TYPES
from connect4 import Connect4
import random
import numpy as np
from tqdm import tqdm
import jsonpickle

class Model:
    def __init__(self, model_name: str):
        with open(f"../models/{model_name}/details.json", 'r') as f:
            config: Config = jsonpickle.decode(f.read())
        
        self.input_shape = [config.board_config.height, config.board_config.width]
        self.model = tf.keras.models.load_model(f"../models/{model_name}")
    
    def predict(self, game: Connect4) -> int:
        return np.argmax(self.model.predict(game.board.reshape(1, *game.board.shape), verbose=0))

class DQN:
    def __init__(self, input_shape, num_actions, model_config: ModelConfig, create=True):
        self.input_shape = input_shape
        self.model: tf.keras.Sequential = self.create_model(input_shape, num_actions, model_config)
        self.target_model: tf.keras.Sequential = self.create_model(input_shape, num_actions, model_config)
        self.update_target_model()

    def create_model(self, input_shape, num_actions, model_config: ModelConfig) -> tf.keras.Sequential:
        model_layers = [LAYER_TYPES[l.type.lower()](**l.params) for l in model_config.layers]
        model_layers.insert(0, tf.keras.layers.Input(shape=input_shape))
        model_layers.append(tf.keras.layers.Dense(num_actions))
        
        model = tf.keras.Sequential(model_layers)
        model.compile(optimizer=model_config.optimizer.lower(), loss=model_config.loss.lower())

        return model

    def save_model(self, filename, config):
        self.model.save(f"../models/{filename}")
        with open(f"../models/{filename}/details.json", 'w') as f:
            f.write(jsonpickle.encode(config))

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())
    
    def train(self, env: Connect4, gamma, epsilon, epsilon_min, epsilon_decay, batch_size, episodes):
        memory = []

        for _ in tqdm(range(episodes)):
            state = env.reset()
            done = False
            while not done:
                if random.random() < epsilon:
                    action = np.random.choice(env.board.shape[1])
                else:
                    q_values = self.model.predict(state.reshape(1, *env.board.shape), verbose=0)
                    action = np.argmax(q_values)
                next_state, reward, done = env.step(action, env.turn)
                memory.append((state, action, reward, next_state, done))
                state = next_state

                if len(memory) > batch_size:
                    minibatch = random.sample(memory, batch_size)
                    states, actions, rewards, next_states, dones = zip(*minibatch)
                    states = np.array(states)
                    actions = np.array(actions)
                    rewards = np.array(rewards)
                    next_states = np.array(next_states)
                    dones = np.array(dones)

                    targets = self.model.predict(states, verbose=0)
                    next_q_values = self.target_model.predict(next_states, verbose=0).max(axis=1)
                    targets[range(batch_size), actions] = rewards + gamma * next_q_values * ~dones

                    self.model.train_on_batch(states, targets)

            if epsilon > epsilon_min:
                epsilon *= epsilon_decay

            self.update_target_model()
    
    def test(self, env: Connect4, rewards_config: RewardsConfig, games_amount):
        total_rewards = 0
        for _ in tqdm(range(games_amount)):
            state = env.reset()
            done = False
            while not done:
                q_values = self.model.predict(state.reshape(1, *env.board.shape), verbose=0)
                action = np.argmax(q_values)
                _, rewards_p, done = env.step(action, -1)
                
                if done:
                    total_rewards += rewards_p
                    break
                
                _, rewards_m, done = env.step(random.choice(range(env.board.shape[1])), 1)
                while rewards_m == rewards_config.forbidden_move:
                    _, rewards_m, done = env.step(random.choice(range(env.board.shape[1])), 1)
                
                total_rewards += rewards_p - rewards_m

        return total_rewards / games_amount