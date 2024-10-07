import pygame
import random
from functions import (
    draw_max_kw_hit,
    calculate_step_reward,
    calculate_final_reward,
    update_temperature,
    update_combined_power_usage,
    draw_room,
    draw_real_time_plot,
    draw_energy_consumption,
    draw_timer,
    show_final_screen,
)

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
num_zones = 5

# Zone variables
zones = []
for _ in range(num_zones):
    zones.append(
        {
            "room_temp": random.randint(
                55, 65
            ),  # Starting room temperature in Fahrenheit
            "desired_temp": 70,  # Desired comfortable temperature
            "heat_on": False,  # Controls whether the system is running or not
            "heating_element_on": False,  # Controls whether the heating element is on or off
            "heat_loss": random.uniform(0.03, 0.06),  # Random heat loss for each zone
            "outside_temp": global_outside_air_temp,  # Use global outside air temperature
            "current_kw": 0,  # Current power consumption
            "cycle_timer": 0,  # Timer for cycling heat off and on
            "at_setpoint": False,  # Tracks if the zone has reached the setpoint
        }
    )


# Game settings
heating_power = 0.15  # Heating rate when heating element is on
max_kw = random.uniform(4.5, 5.5)  # Maximum power of the heater in kW per heat pump
fan_kw_percent = 0.2  # 20% of power when fan is running without heat
high_kw_threshold = round(
    num_zones * max_kw * 0.66, 2
)  # Threshold for high power demand penalty

print("kW high limit setpoint for this game: ", high_kw_threshold)

# Energy tracking
total_energy_kwh = 0  # Total energy in kWh
combined_power_usage = []  # List to store combined power usage over time
max_kw_hit = 0  # Maximum kW hit during the simulation
current_reward = 0  # Track the reward during the game

# Real-time plot settings
plot_width = 300
plot_height = 100
plot_x = (SCREEN_WIDTH - plot_width) // 2
plot_y = SCREEN_HEIGHT - 600  # Spacing for plot below the zones

# Countdown timer (60 seconds)
game_duration = 60  # Duration in seconds
timer = game_duration * 30  # 30 FPS for 60 seconds

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i, zone in enumerate(zones):
                row = i // 5
                col = i % 5
                x = col * 240 + 20
                y = row * 180 + 20
                if x <= mouse_x <= x + 200 and y <= y + 150:
                    zone["heat_on"] = not zone["heat_on"]

    # Update temperatures, kW usage, and energy for each zone
    for zone in zones:
        total_energy_kwh = update_temperature(
            zone, max_kw, fan_kw_percent, heating_power, total_energy_kwh
        )

    # Update the combined power usage and capture the updated max_kw_hit value
    max_kw_hit = update_combined_power_usage(
        zones, combined_power_usage, plot_width, max_kw, num_zones, max_kw_hit
    )

    # Draw each zone in a 3x5 grid
    for i, zone in enumerate(zones):
        row = i // 5
        col = i % 5
        x = col * 240 + 20
        y = row * 180 + 20
        draw_room(zone, x, y, screen, BLUE, RED, GREEN, BLACK, font)

    # Calculate reward at each step and accumulate it
    calculate_step_reward(zones, current_reward, high_kw_threshold, timer)

    # Draw the real-time power plot, energy consumption, the countdown timer, the current reward, and the max power hit
    draw_real_time_plot(
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
        high_kw_threshold,
        zones,
    )
    draw_energy_consumption(screen, plot_x, plot_y, plot_height, total_energy_kwh, font)
    draw_timer(screen, plot_x, plot_y, plot_height, timer, font)
    draw_max_kw_hit(screen, font, max_kw_hit, plot_x, plot_y, plot_height)

    # Check if time is up (End of Episode)
    if timer <= 0:
        final_reward = calculate_final_reward(zones)
        current_reward += final_reward
        show_final_screen(
            screen,
            font,
            zones,
            total_energy_kwh,
            max_kw_hit,
            current_reward,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
        )
        running = False

    timer -= 1
    pygame.display.flip()
    clock.tick(30)


pygame.quit()
