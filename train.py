import numpy as np
import random
from connect4 import Connect4
from model import DQN

def train(env: Connect4, agent: DQN, gamma, epsilon, epsilon_decay, batch_size, episodes):
    memory = []

    from tqdm import tqdm

    for _ in tqdm(episodes):
        state = env.reset()
        done = False
        while not done:
            if random.random() < epsilon:
                action = np.random.choice(env.board.shape[1])
            else:
                q_values = agent.model.predict(state.reshape(1, *env.board), verbose=0)
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

                targets = agent.model.predict(states, verbose=0)
                next_q_values = agent.target_model.predict(next_states, verbose=0).max(axis=1)
                targets[range(batch_size), actions] = rewards + gamma * next_q_values * ~dones

                agent.model.train_on_batch(states, targets)

        if epsilon > 0.1:
            epsilon *= epsilon_decay

        agent.update_target_model()