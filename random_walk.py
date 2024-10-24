import random
from flappy_heatpump_env import FlappyHeatPumpEnv
import pygame

# Number of episodes for random walk
episodes = 100

# Create the Gym environment
env = FlappyHeatPumpEnv()
action_size = env.action_space.n

# Initialize Pygame clock to control frame rate
clock = pygame.time.Clock()

# Random Walk (Fast Simulation)
for episode in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        # Event handling for Pygame (important to prevent freezing)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Select a random action
        action = env.action_space.sample()

        # Take a step in the environment (each step is 15 minutes)
        next_state, reward, done, _ = env.step(action)

        # Render the environment (Pygame window)
        env.render()

        # Control the frame rate to match the simulation speed (faster than human mode)
        clock.tick(120)  # Faster rate for fast training mode (e.g., 120 FPS)

        state = next_state
        total_reward += reward

    print(f"Episode {episode + 1}: Total Reward: {total_reward}")

# Watch the random agent play after training (human mode)
for _ in range(10):  # Watch 10 episodes
    state = env.reset()
    done = False
    while not done:
        # Event handling for Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Render the environment (Pygame window)
        env.render()

        # Select random actions
        action = env.action_space.sample()
        state, _, done, _ = env.step(action)

        # Control frame rate for real-time human mode (30 FPS)
        clock.tick(30)

env.close()
