import gym
from gym import spaces
import numpy as np
import pygame


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
        self.action_space = spaces.Discrete(self.num_zones)

        # Observation space: Temperatures for 5 zones (40-90°F)
        self.observation_space = spaces.Box(
            low=40, high=90, shape=(self.num_zones,), dtype=np.float32
        )

        # Cooldown timer for each zone
        self.cooldown_timers = [0] * self.num_zones

        # Time windows and action limits
        self.total_steps = 24  # 6 hours of simulation, 15-min intervals
        self.steps_per_window = 6  # Max steps per time window
        self.num_windows = self.total_steps // self.steps_per_window
        self.current_window = 0
        self.actions_taken_in_window = 0

        # Initialize other variables
        self.heating_power = 0.15
        self.max_kw = np.random.uniform(4.5, 5.5)
        self.fan_kw_percent = 0.2
        self.total_energy_kwh = 0
        self.max_kw_hit = 0
        self.timer = self.total_steps

        # Set high_kw_threshold as part of the environment
        self.high_kw_threshold = round(self.num_zones * self.max_kw * 0.66)

    def initialize_zones(self, global_outside_air_temp=None):
        """Initialize zones with consistent outside air temperature for human and bot."""
        if global_outside_air_temp is None:
            global_outside_air_temp = np.random.randint(16, 40)

        return [
            {
                "room_temp": np.random.randint(55, 65),
                "desired_temp": 70,
                "heat_on": False,
                "heating_element_on": False,
                "heat_loss": np.random.uniform(0.03, 0.06),
                "outside_temp": global_outside_air_temp,
                "current_kw": 0,
                "cycle_timer": 0,
                "at_setpoint": False,
            }
            for _ in range(self.num_zones)
        ]

    def reset(self, global_outside_air_temp=None):
        """Resets the environment."""
        self.zones = self.initialize_zones(global_outside_air_temp)
        self.cooldown_timers = [0] * self.num_zones
        self.current_window = 0
        self.actions_taken_in_window = 0
        self.total_energy_kwh = 0
        self.max_kw_hit = 0
        self.timer = self.total_steps
        self.current_reward = 0
        return np.array([zone["room_temp"] for zone in self.zones], dtype=np.float32)

    def step(self, action):
        """Performs a step in the environment."""
        self.cooldown_timers = [max(0, timer - 1) for timer in self.cooldown_timers]

        if self.actions_taken_in_window < self.steps_per_window:
            for i, zone in enumerate(self.zones):
                if action == i and self.cooldown_timers[i] == 0:
                    zone["heat_on"] = not zone["heat_on"]
                    self.cooldown_timers[i] = 15
                    self.actions_taken_in_window += 1

        for zone in self.zones:
            self.total_energy_kwh = self.update_temperature(
                zone,
                self.max_kw,
                self.fan_kw_percent,
                self.heating_power,
                self.total_energy_kwh,
            )

        self.max_kw_hit = self.update_combined_power_usage(
            self.zones, [], 300, self.max_kw, self.num_zones, self.max_kw_hit
        )

        done = self.timer <= 0
        if done:
            final_reward = self.calculate_real_life_reward(
                self.zones,
                self.high_kw_threshold,
                self.total_energy_kwh,
                baseline_energy_kwh=100,
            )
            self.current_reward += final_reward

        self.timer -= 1
        state = np.array([zone["room_temp"] for zone in self.zones], dtype=np.float32)
        return state, self.current_reward, done, {}

    def render(self, mode="human"):
        """Renders the environment."""
        self.screen.fill((255, 255, 255))
        for i, zone in enumerate(self.zones):
            row = i // 5
            col = i % 5
            x = col * 240 + 20
            y = row * 180 + 20
            self.draw_room(zone, x, y)

        pygame.display.flip()

    def close(self):
        pygame.quit()

    def calculate_baseline_energy(self, global_outside_air_temp=None, render=False):
        """Simulates baseline energy consumption with all zones heating on."""
        baseline_energy_kwh = 0
        self.reset(global_outside_air_temp=global_outside_air_temp)

        for _ in range(self.total_steps):
            for zone in self.zones:
                zone["heat_on"] = True
                zone["heating_element_on"] = True

            _, _, done, _ = self.step(0)
            baseline_energy_kwh += self.total_energy_kwh

            if render:
                self.render()

            if done:
                break

        return baseline_energy_kwh

    def draw_real_time_plot(
        self,
        screen,
        combined_power_usage,
        max_kw,
        num_zones,
        plot_x,
        plot_y,
        plot_width,
        plot_height,
        font,
        total_energy_kwh,
        global_outside_air_temp,
        zones,
    ):
        """Draws the real-time plot showing power usage."""
        pygame.draw.rect(
            screen, (255, 255, 255), (plot_x, plot_y, plot_width, plot_height), 1
        )

        if len(combined_power_usage) > 1:
            for i in range(1, len(combined_power_usage)):
                x1 = plot_x + i - 1
                y1 = (
                    plot_y
                    + plot_height
                    - (combined_power_usage[i - 1] / (max_kw * num_zones)) * plot_height
                )
                x2 = plot_x + i
                y2 = (
                    plot_y
                    + plot_height
                    - (combined_power_usage[i] / (max_kw * num_zones)) * plot_height
                )
                pygame.draw.line(screen, (255, 165, 0), (x1, y1), (x2, y2), 2)

        kw_label = font.render("kW", True, (0, 0, 0))
        screen.blit(kw_label, (plot_x - 30, plot_y + plot_height // 2))

        total_kw = sum(zone["current_kw"] for zone in zones)
        combined_kw_text = font.render(
            f"Total kW: {round(total_kw, 2)}", True, (0, 0, 0)
        )
        screen.blit(combined_kw_text, (plot_x + plot_width + 40, plot_y))

        high_kw_text = font.render(
            f"High kW Limit: {self.high_kw_threshold} kW", True, (0, 0, 0)
        )
        screen.blit(high_kw_text, (plot_x + plot_width + 40, plot_y + 40))

        outside_temp_text = font.render(
            f"Outside Temp: {global_outside_air_temp} F", True, (0, 0, 0)
        )
        screen.blit(outside_temp_text, (plot_x + plot_width + 40, plot_y + 80))

    def calculate_real_life_reward(
        self,
        zones,
        high_kw_threshold,
        total_energy_kwh,
        baseline_energy_kwh,
        debug=False,
    ):
        """Calculates the reward based on HVAC system performance."""
        total_reward = 0
        base_pay = 100
        comfort_bonus = 0
        energy_savings_bonus = 0
        demand_management_bonus = 0
        penalties = 0

        total_power = sum(zone["current_kw"] for zone in zones)

        all_within_comfort = all(
            abs(zone["room_temp"] - zone["desired_temp"]) < 3 for zone in zones
        )
        if all_within_comfort:
            total_reward += base_pay
        else:
            penalties -= 25

        for zone in zones:
            temp_diff = abs(zone["room_temp"] - zone["desired_temp"])
            if temp_diff < 1:
                comfort_bonus += 10
            elif temp_diff >= 3:
                penalties -= 25

        energy_savings = max(0, baseline_energy_kwh - total_energy_kwh)
        energy_savings_bonus += energy_savings * 2

        if total_power <= high_kw_threshold:
            demand_management_bonus += 20
        else:
            penalties -= 5

        total_reward += (
            comfort_bonus + energy_savings_bonus + demand_management_bonus + penalties
        )
        if total_reward < 0:
            total_reward = 0

        return total_reward

    def update_temperature(
        self, zone, max_kw, fan_kw_percent, heating_power, total_energy_kwh
    ):
        """Updates the temperature and energy consumption for a zone."""
        zone["room_temp"] -= self.calculate_heat_loss(
            zone["heat_loss"], zone["outside_temp"]
        )

        if zone["heat_on"]:
            if zone["room_temp"] < zone["desired_temp"] - 1:
                if zone["cycle_timer"] <= 0:
                    zone["heating_element_on"] = True
                    zone["cycle_timer"] = 30
            elif (
                zone["room_temp"] >= zone["desired_temp"] and zone["heating_element_on"]
            ):
                if zone["cycle_timer"] > 0:
                    zone["cycle_timer"] -= 1
                else:
                    zone["heating_element_on"] = False
                    if not zone["at_setpoint"]:
                        zone["at_setpoint"] = True

            if zone["heating_element_on"]:
                zone["room_temp"] += heating_power * 0.6
                zone["current_kw"] = max_kw
            else:
                zone["current_kw"] = max_kw * fan_kw_percent

            if zone["at_setpoint"]:
                zone["current_kw"] *= 0.5
        else:
            zone["current_kw"] = 0

        zone["room_temp"] = max(40, min(100, zone["room_temp"]))
        time_in_hours = 1 / (30 * 3600) * 360
        total_energy_kwh += zone["current_kw"] * time_in_hours

        return total_energy_kwh

    def calculate_heat_loss(self, heat_loss_rate, global_outside_air_temp):
        """Calculates heat loss."""
        scaled_heat_loss = heat_loss_rate * (70 - global_outside_air_temp) / 20
        return scaled_heat_loss * 0.5

    def update_combined_power_usage(
        self, zones, combined_power_usage, plot_width, max_kw, num_zones, max_kw_hit
    ):
        """Updates and tracks the combined power usage for all zones."""
        total_power = sum(zone["current_kw"] for zone in zones)
        combined_power_usage.append(total_power)

        if total_power > max_kw_hit:
            max_kw_hit = total_power

        if len(combined_power_usage) > plot_width:
            combined_power_usage.pop(0)

        return max_kw_hit

    def draw_room(self, zone, x, y):
        """Draws a room with the current temperature and heat status."""
        room_color = (
            (0, 0, 255)
            if zone["room_temp"] < 65
            else (255, 0, 0) if zone["room_temp"] > 75 else (0, 255, 0)
        )
        pygame.draw.rect(self.screen, room_color, (x, y, 200, 150))
        temp_text = self.font.render(f"{int(zone['room_temp'])}F", True, (0, 0, 0))
        text_rect = temp_text.get_rect(center=(x + 100, y + 75))
        self.screen.blit(temp_text, text_rect)

        if zone["heat_on"]:
            pygame.draw.circle(self.screen, (255, 0, 0), (x + 100, y + 130), 10)
