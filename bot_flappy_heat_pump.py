import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200  # Adjusted for 15 boxes (3x5 grid)
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Heat Pump with Multiple Zones")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# Font
font = pygame.font.SysFont(None, 36)

# Global Outside Air Temperature
global_outside_air_temp = random.randint(16, 40)

# Seed the random generator for consistent heat loss characteristics
random.seed(42)

# Number of zones
num_zones = 15  # 15 zones for 3 rows and 5 columns

# Cooldown time (in frames, adjust this variable to tune the cooldown)
COOLDOWN_TIME = 60  # 2 seconds at 30 FPS

# Function to reset the environment (zones) at the start of each episode
def reset_zones():
    return [
        {
            "room_temp": random.randint(55, 65),  # Starting room temperature in Fahrenheit
            "desired_temp": 70,  # Desired comfortable temperature
            "heat_on": False,  # Controls whether the system is running or not
            "heating_element_on": False,  # Controls whether the heating element is on or off
            "heat_loss": random.uniform(0.03, 0.06),  # Random heat loss for each zone
            "outside_temp": global_outside_air_temp,  # Use global outside air temperature
            "current_kw": 0,  # Current power consumption
            "cycle_timer": 0,  # Timer for cycling heat off and on
            "cooldown_timer": 0  # Cooldown timer to prevent rapid toggling
        }
        for _ in range(num_zones)
    ]

# Game settings
heating_power = 0.15  # Heating rate when heating element is on
max_kw = 5.0  # Maximum power of the heater in kW per zone
fan_kw_percent = 0.2  # 20% of power when fan is running without heat
high_kw_threshold = 50  # Threshold for high power demand penalty

# Energy tracking
total_energy_kwh = 0  # Total energy in kWh
combined_power_usage = []  # List to store combined power usage over time
max_kw_hit = 0  # Maximum kW hit during the simulation

# Real-time plot settings
plot_width = 300
plot_height = 100
plot_x = (SCREEN_WIDTH - plot_width) // 2
plot_y = SCREEN_HEIGHT - 300  # Spacing for plot below the zones

# Heat loss function
def calculate_heat_loss(heat_loss_rate):
    return heat_loss_rate * (70 - global_outside_air_temp) / 20  # Adjust rate based on global outside temp

# Update temperature based on zone status
def update_temperature(zone):
    global total_energy_kwh

    # Simulate heat loss due to global outside temperature
    zone["room_temp"] -= calculate_heat_loss(zone["heat_loss"])

    if zone["heat_on"]:
        # If the temperature is below setpoint, turn on the heating element
        if zone["room_temp"] < zone["desired_temp"] - 1:
            if zone["cycle_timer"] <= 0:
                zone["heating_element_on"] = True
                zone["cycle_timer"] = 30  # Reset cycle_timer to 1 second
        elif zone["room_temp"] >= zone["desired_temp"] and zone["heating_element_on"]:
            if zone["cycle_timer"] > 0:
                zone["cycle_timer"] -= 1
            else:
                zone["heating_element_on"] = False

        if zone["heating_element_on"]:
            zone["room_temp"] += heating_power
            zone["current_kw"] = max_kw  # Full power
        else:
            zone["current_kw"] = max_kw * fan_kw_percent  # Fan only at 20% power
    else:
        zone["current_kw"] = 0  # System is off, no power usage

    # Clamp temperature to within min and max limits
    zone["room_temp"] = max(40, min(100, zone["room_temp"]))

    # Update energy consumption based on current power (kW) and time (in hours)
    time_in_hours = 1 / (30 * 3600) * 360  # Scale by 360 to represent real-life time (6 hours)
    total_energy_kwh += zone["current_kw"] * time_in_hours

# Update power usage
def update_combined_power_usage(zones):
    global max_kw_hit

    total_power = sum(zone["current_kw"] for zone in zones)
    combined_power_usage.append(total_power)

    if total_power > max_kw_hit:
        max_kw_hit = total_power

    if len(combined_power_usage) > plot_width:
        combined_power_usage.pop(0)

# Drawing the zones
def draw_room(zone, x, y):
    room_color = BLUE if zone["room_temp"] < 65 else RED if zone["room_temp"] > 75 else GREEN
    pygame.draw.rect(screen, room_color, (x, y, 200, 150))
    temp_text = font.render(f"{int(zone['room_temp'])}F", True, BLACK)
    text_rect = temp_text.get_rect(center=(x + 100, y + 75))
    screen.blit(temp_text, text_rect)
    if zone["heat_on"]:
        pygame.draw.circle(screen, RED, (x + 100, y + 130), 10)

# Real-time power usage plot
def draw_real_time_plot():
    pygame.draw.rect(screen, WHITE, (plot_x, plot_y, plot_width, plot_height), 1)
    if len(combined_power_usage) > 1:
        for i in range(1, len(combined_power_usage)):
            x1 = plot_x + i - 1
            y1 = plot_y + plot_height - (combined_power_usage[i - 1] / (max_kw * num_zones)) * plot_height
            x2 = plot_x + i
            y2 = plot_y + plot_height - (combined_power_usage[i] / (max_kw * num_zones)) * plot_height
            pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 2)
    kw_label = font.render("kW", True, BLACK)
    screen.blit(kw_label, (plot_x - 30, plot_y + plot_height // 2))

# Timer and energy consumption display
def draw_timer():
    time_left = timer // 30
    timer_text = font.render(f"Time Remaining: {time_left}s", True, BLACK)
    screen.blit(timer_text, (plot_x, plot_y + plot_height + 60))

def draw_energy_consumption():
    energy_text = font.render(f"Elapsed Electrical Energy: {round(total_energy_kwh, 2)} kWh", True, BLACK)
    screen.blit(energy_text, (plot_x, plot_y + plot_height + 20))

# Reward calculation
def calculate_step_reward(zone):
    temp_diff = abs(zone["room_temp"] - zone["desired_temp"])
    temp_reward = 1 if temp_diff < 1 else 0.5 if temp_diff < 3 else 0
    energy_penalty = -0.01 * zone["current_kw"]
    total_power = sum(zone["current_kw"] for zone in zones)
    high_demand_penalty = -1 if total_power > high_kw_threshold else 0
    return temp_reward + energy_penalty + high_demand_penalty

# End of episode reward
def calculate_end_reward(zones):
    all_at_setpoint = all(abs(zone["room_temp"] - zone["desired_temp"]) < 1 for zone in zones)
    return 10 if all_at_setpoint else 0

# Q-Learning Agent
class QLearningAgent:
    def __init__(self, env):
        self.env = env
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.q_table = {}

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, len(self.env) - 1)
        state_key = tuple(zone["room_temp"] for zone in state)
        if state_key not in self.q_table:
            return random.randint(0, len(self.env) - 1)
        return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def learn(self, state, action, reward, next_state):
        state_key = tuple(zone["room_temp"] for zone in state)
        next_state_key = tuple(zone["room_temp"] for zone in next_state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {i: 0 for i in range(len(self.env))}
        old_q_value = self.q_table[state_key][action]
        future_q = max(self.q_table.get(next_state_key, {a: 0 for a in range(len(self.env))}).values())
        self.q_table[state_key][action] = old_q_value + self.alpha * (reward + self.gamma * future_q - old_q_value)

# Main game loop with multiple episodes
def main(run_q_learning=False, num_episodes=100):
    global timer  # Declare global variables here

    clock = pygame.time.Clock()
    zones = reset_zones()  # Initialize/reset zones at the start of each episode
    agent = QLearningAgent(zones) if run_q_learning else None

    # Loop for multiple episodes
    for episode in range(num_episodes):
        print(f"Starting episode {episode + 1}/{num_episodes}")
        zones = reset_zones()  # Reinitialize/reset zones for each episode
        running = True
        timer = 60 * 30  # Reset timer for each episode (60 seconds * 30 FPS)

        while running:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if run_q_learning:
                action = agent.choose_action(zones)

                # Only toggle heat if the cooldown timer is 0
                if zones[action]["cooldown_timer"] <= 0:
                    zones[action]["heat_on"] = not zones[action]["heat_on"]
                    zones[action]["cooldown_timer"] = COOLDOWN_TIME  # Using adjustable cooldown

                # Add a delay between each action
                time.sleep(0.5)  # 0.5-second delay between actions
            else:
                for i, zone in enumerate(zones):
                    if random.uniform(0, 1) < 0.5:
                        zone["heat_on"] = not zone["heat_on"]

            # Update temperatures, kW usage, and energy for each zone
            for zone in zones:
                update_temperature(zone)

            # Update cooldown timers
            for zone in zones:
                if zone["cooldown_timer"] > 0:
                    zone["cooldown_timer"] -= 1

            update_combined_power_usage(zones)  # Pass zones to the function

            # Draw each zone
            for i, zone in enumerate(zones):
                row = i // 5  # 3 rows
                col = i % 5  # 5 columns
                draw_room(zone, col * 240 + 20, row * 180 + 20)

            draw_real_time_plot()
            draw_energy_consumption()
            draw_timer()

            timer -= 1
            if timer <= 0:
                running = False
                if run_q_learning:
                    reward = calculate_end_reward(zones)
                    agent.learn(zones, action, reward, zones)

            pygame.display.flip()
            clock.tick(10)  # Reduced FPS to slow down overall simulation

        # Print some feedback at the end of each episode (optional)
        if run_q_learning:
            print(f"Episode {episode + 1} finished. Rewards: {reward}")

if __name__ == "__main__":
    q_learning_mode = len(sys.argv) > 1 and sys.argv[1] == "q_learning"
    
    # Set default number of episodes to 10, and allow overriding via command-line arguments
    num_episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    main(run_q_learning=q_learning_mode, num_episodes=num_episodes)

pygame.quit()
