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

        # Initialize number of zones
        self.num_zones = 5

        # Define action and observation space
        # Action space: Discrete actions to toggle heat for 5 zones
        self.action_space = spaces.Discrete(self.num_zones)

        # Observation space: Temperatures for 5 zones (continuous values between 0 and 100)
        self.observation_space = spaces.Box(
            low=0, high=100, shape=(self.num_zones,), dtype=np.float32
        )

        # Cooldown timer for each zone
        self.cooldown_timers = [0] * self.num_zones  # Initialize cooldown for each zone

        # Time windows and action limits
        self.total_steps = (
            24  # Total steps for the episode (24 steps for 6 hours, 15-min increments)
        )
        self.steps_per_window = 6  # 6 steps allowed per time window
        self.num_windows = (
            self.total_steps // self.steps_per_window
        )  # Divide into equal time windows
        self.current_window = 0
        self.actions_taken_in_window = 0

        # Initialize other variables
        self.heating_power = 0.15
        self.max_kw = np.random.uniform(4.5, 5.5)
        self.fan_kw_percent = 0.2
        self.total_energy_kwh = 0
        self.max_kw_hit = 0
        self.timer = self.total_steps  # 24 steps (15-minute increments over 6 hours)

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
        self.cooldown_timers = [0] * self.num_zones  # Reset cooldown timers
        self.current_window = 0  # Reset the action window
        self.actions_taken_in_window = 0  # Reset actions taken in the window
        self.total_energy_kwh = 0
        self.max_kw_hit = 0
        self.timer = self.total_steps  # Reset to 24 steps (15-minute increments)
        return np.array([zone["room_temp"] for zone in self.zones], dtype=np.float32)

    def step(self, action):
        # Decrement the cooldown timers
        self.cooldown_timers = [max(0, timer - 1) for timer in self.cooldown_timers]

        # Ensure the agent can't take more than the allowed steps in a window
        if self.actions_taken_in_window < self.steps_per_window:
            for i, zone in enumerate(self.zones):
                if (
                    action == i and self.cooldown_timers[i] == 0
                ):  # Only toggle if no cooldown
                    zone["heat_on"] = not zone["heat_on"]
                    self.cooldown_timers[i] = (
                        15  # 15-step cooldown (representing 15 minutes)
                    )
                    self.actions_taken_in_window += (
                        1  # Increment the action count for this window
                    )

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

        # Check if we need to move to the next time window
        if self.timer % self.steps_per_window == 0:
            self.current_window += 1
            self.actions_taken_in_window = 0  # Reset actions for the new window

        # Reward logic and check if the episode is done
        reward = 0
        done = self.timer <= 0  # End episode after 24 time steps
        info = {}

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
