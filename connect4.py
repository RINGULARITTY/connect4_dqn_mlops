import numpy as np
from typing import Tuple
from config import RewardsConfig

class Connect4:
    def __init__(self, rewards, width=7, height=6):
        self.width = width
        self.height = height
        self.rewards: RewardsConfig = rewards
        self.reset()

    def reset(self) -> np.ndarray:
        self.board = np.zeros((self.height, self.width), dtype=np.int8)
        self.done = False
        self.turn = 1
        return self.board

    def step(self, action, player) -> Tuple[np.ndarray, float, bool]:
        if self.done:
            return self.board, 0, True

        if action < 0 or action >= self.width:
            return self.board, self.rewards.forbidden_move, True

        col_data = self.board[:, action]
        if np.all(col_data != 0):
            return self.board, - self.rewards.win, True

        row = np.argmax(col_data == 0)
        self.board[row, action] = player
        if self.check_win(row, action, player):
            self.done = True
            return self.board, self.rewards.win, True

        self.turn *= -1
        return self.board, 0, False

    def check_win(self, row, col, player) -> bool:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 0
            for step in range(-3, 4):
                r, c = row + step * dr, col + step * dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    count = count + 1 if self.board[r, c] == player else 0
                    if count == 4:
                        return True
        return False