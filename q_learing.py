import random
import numpy as np
import pygame
from flappy_building_sim_env import FlappyHeatPumpEnv

# Hyperparameters for Q-learning
episodes = 1000  # Total number of training episodes
learning_rate = 0.1  # Alpha
discount_factor = 0.99  # Gamma
epsilon = 1.0  # Epsilon for exploration-exploitation tradeoff
epsilon_decay = 0.995  # Epsilon decay rate
min_epsilon = 0.01  # Minimum value for epsilon
num_actions = 5  # Assuming 5 discrete actions (same as num_zones)

# Create the Gym environment
env = FlappyHeatPumpEnv()
state_size = env.observation_space.shape[0]

# Initialize Q-table with zeros
q_table = np.zeros((state_size, num_actions))

global_outside_air_temp = random.randint(16, 40)
baseline_energy_kwh = env.calculate_baseline_energy(
    global_outside_air_temp=global_outside_air_temp, render=False
)
print(f"Baseline kWh: {baseline_energy_kwh}")

# Initialize Pygame clock to control the frame rate for rendering
clock = pygame.time.Clock()

# Training loop for Q-learning
for episode in range(episodes):
    state = env.reset(global_outside_air_temp=global_outside_air_temp)
    state = np.argmax(state)  # Discretize the state (for simplicity)
    total_reward = 0
    done = False

    while not done:
        # Exploration-exploitation tradeoff
        if random.uniform(0, 1) < epsilon:
            action = random.choice(range(num_actions))  # Explore action space
        else:
            action = np.argmax(q_table[state])  # Exploit learned values

        # Take the chosen action
        next_state, reward, done, _ = env.step(action)
        next_state = np.argmax(next_state)  # Discretize next state

        # Q-learning update
        best_next_action = np.argmax(q_table[next_state])  # Best action for next state
        q_table[state, action] = q_table[state, action] + learning_rate * (
            reward
            + discount_factor * q_table[next_state, best_next_action]
            - q_table[state, action]
        )

        state = next_state
        total_reward += reward

    # At the end of the episode, calculate the final reward and add it to total_reward
    final_reward = env.calculate_real_life_reward(
        env.zones,
        high_kw_threshold=6,
        total_energy_kwh=env.total_energy_kwh,
        baseline_energy_kwh=baseline_energy_kwh,
    )
    total_reward += final_reward

    # Reduce epsilon (exploration-exploitation balance)
    epsilon = max(min_epsilon, epsilon * epsilon_decay)

    print(f"Episode {episode + 1}: Total Reward: {total_reward}")

# Testing the agent (after training)
for _ in range(10):
    state = env.reset(global_outside_air_temp=global_outside_air_temp)
    state = np.argmax(state)
    done = False

    while not done:
        # Exploit learned values
        action = np.argmax(q_table[state])
        next_state, _, done, _ = env.step(action)
        next_state = np.argmax(next_state)

        # Render environment for human observation
        env.render()

        # Control frame rate for real-time human mode (30 FPS)
        clock.tick(30)

        state = next_state

env.close()
