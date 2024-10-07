import numpy as np
import random
from flappy_heatpump_env import FlappyHeatPumpEnv

# Q-Learning hyperparameters
alpha = 0.1  # Learning rate
gamma = 0.99  # Discount factor
epsilon = 1.0  # Exploration-exploitation trade-off
epsilon_min = 0.1
epsilon_decay = 0.995
episodes = 1000  # Number of training episodes

# Create the Gym environment
env = FlappyHeatPumpEnv()
action_size = env.action_space.n
state_size = env.observation_space.shape[0]

# Initialize Q-table
q_table = np.zeros([state_size, action_size])

# Q-Learning algorithm
for episode in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        if random.uniform(0, 1) < epsilon:
            # Explore: select a random action
            action = env.action_space.sample()
        else:
            # Exploit: select the action with max Q-value
            action = np.argmax(q_table[state])

        next_state, reward, done, _ = env.step(action)

        # Q-learning formula
        q_table[state, action] = q_table[state, action] + alpha * (
            reward + gamma * np.max(q_table[next_state]) - q_table[state, action]
        )

        state = next_state
        total_reward += reward

    # Decay epsilon for less exploration over time
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    print(f"Episode {episode+1}: Total Reward: {total_reward}")

# Watch the bot play after training
for _ in range(10):  # Watch 10 episodes
    state = env.reset()
    done = False
    while not done:
        env.render()  # Render the environment (Pygame window)
        action = np.argmax(q_table[state])
        state, _, done, _ = env.step(action)

env.close()
