import numpy as np
import random
from rl_env import AHUEnvironment

class RLAgent:
    def __init__(self, action_space):
        self.action_space = action_space
        self.q_table = np.zeros((100, action_space))  # Example size, adapt as needed

    def choose_action(self, state):
        sa_fan_speed = state['Sa_FanSpeed']
        if sa_fan_speed > 5.0:
            if random.uniform(0, 1) < 0.1:
                # Explore: choose a random action
                return random.uniform(-5, 5)
            else:
                # Exploit: choose the best action based on Q-table (simplified)
                return np.argmax(self.q_table)
        else:
            # If AHU is off, take no action
            return 0

    def learn(self, state, action, reward, next_state):
        # Simplified Q-learning update, ignoring state transitions for now
        state_idx = int(state['SpaceTemp'])  # use temperature as state index (simple example)
        action_idx = int((action + 5) * (self.action_space / 10))  # scale action for table indexing

        # Update Q-table (learning rate and discount factor could be added)
        self.q_table[state_idx, action_idx] = reward


# Training loop for the RL agent
env = AHUEnvironment()
agent = RLAgent(action_space=10)

for episode in range(100):  # Example number of episodes
    state = env.reset()
    done = False
    print(f"\nEpisode {episode + 1}")

    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.learn(state, action, reward, next_state)
        state = next_state

        print(f"Step: {env.current_step}, Action: {action}, Reward: {reward}")
