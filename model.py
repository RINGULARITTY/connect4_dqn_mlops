import tensorflow as tf

class DQN:
    def __init__(self, input_shape, num_actions):
        self.model = self.create_model(input_shape, num_actions)
        self.target_model = self.create_model(input_shape, num_actions)
        self.update_target_model()

    def create_model(self, input_shape, num_actions) -> tf.keras.Sequential:
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=input_shape),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(num_actions)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def save_model(self, path):
        self.model.save(path)

    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())