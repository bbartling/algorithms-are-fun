# flappy_heatpump_env.py

import gym
from gym import spaces
import numpy as np
import pygame
from functions import draw_room, update_temperature, update_combined_power_usage


class FlappyHeatPumpEnv(gym.Env):
    def __init__(self):
        super(FlappyHeatPumpEnv, self).__init__()

        # Screen settings
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 900
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Heat Pump with Multiple Zones")
        self.font = pygame.font.SysFont(None, 36)

        # Define action and observation space
        self.action_space = spaces.Discrete(5)  # Toggle heat for 5 zones
        self.observation_space = spaces.Box(
            low=0, high=100, shape=(5,), dtype=np.float32
        )  # Room temps

        # Initialize zones
        self.num_zones = 5
        self.zones = self.initialize_zones()

        # Initialize other variables
        self.heating_power = 0.15
        self.max_kw = np.random.uniform(4.5, 5.5)
        self.fan_kw_percent = 0.2
        self.total_energy_kwh = 0
        self.max_kw_hit = 0
        self.timer = 60 * 30  # 60 seconds at 30 FPS

    def initialize_zones(self):
        return [
            {
                "room_temp": np.random.randint(55, 65),
                "desired_temp": 70,
                "heat_on": False,
                "heating_element_on": False,
                "heat_loss": np.random.uniform(0.03, 0.06),
                "outside_temp": np.random.randint(16, 40),
                "current_kw": 0,
                "cycle_timer": 0,
                "at_setpoint": False,
            }
            for _ in range(self.num_zones)
        ]

    def reset(self):
        self.zones = self.initialize_zones()
        self.total_energy_kwh = 0
        self.max_kw_hit = 0
        self.timer = 60 * 30
        return np.array([zone["room_temp"] for zone in self.zones], dtype=np.float32)

    def step(self, action):
        for i, zone in enumerate(self.zones):
            if action == i:  # Toggle the heat for zone[i]
                zone["heat_on"] = not zone["heat_on"]

        # Update temperatures, kW usage, and energy for each zone
        for zone in self.zones:
            self.total_energy_kwh = update_temperature(
                zone,
                self.max_kw,
                self.fan_kw_percent,
                self.heating_power,
                self.total_energy_kwh,
            )

        # Update the combined power usage
        self.max_kw_hit = update_combined_power_usage(
            self.zones, [], 300, self.max_kw, self.num_zones, self.max_kw_hit
        )

        # Reward is not the main focus in this basic example
        reward = 0
        done = self.timer <= 0  # End episode after timer expires
        info = {}  # Additional info if needed

        # Decrement timer
        self.timer -= 1

        # Observation (state)
        state = np.array([zone["room_temp"] for zone in self.zones], dtype=np.float32)

        return state, reward, done, info

    def render(self, mode="human"):
        self.screen.fill((255, 255, 255))
        for i, zone in enumerate(self.zones):
            row = i // 5
            col = i % 5
            x = col * 240 + 20
            y = row * 180 + 20
            draw_room(
                zone,
                x,
                y,
                self.screen,
                (0, 0, 255),
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 0),
                self.font,
            )

        pygame.display.flip()

    def close(self):
        pygame.quit()
