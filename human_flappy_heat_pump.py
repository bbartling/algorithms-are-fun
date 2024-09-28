import pygame
import random

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
num_zones = 3

# Zone variables
zones = []
for _ in range(num_zones):
    zones.append({
        "room_temp": random.randint(55, 65),  # Starting room temperature in Fahrenheit
        "desired_temp": 70,  # Desired comfortable temperature
        "heat_on": False,  # Controls whether the system is running or not
        "heating_element_on": False,  # Controls whether the heating element is on or off
        "heat_loss": random.uniform(0.03, 0.06),  # Random heat loss for each zone
        "outside_temp": global_outside_air_temp,  # Use global outside air temperature
        "current_kw": 0,  # Current power consumption
        "cycle_timer": 0,  # Timer for cycling heat off and on
    })

# Game settings
heating_power = 0.15  # Heating rate when heating element is on
max_kw = 5.0  # Maximum power of the heater in kW per zone
fan_kw_percent = 0.2  # 20% of power when fan is running without heat
high_kw_threshold = 50  # Threshold for high power demand penalty

# Energy tracking
total_energy_kwh = 0  # Total energy in kWh
combined_power_usage = []  # List to store combined power usage over time
max_kw_hit = 0  # Maximum kW hit during the simulation
current_reward = 0  # Track the reward during the game

# Real-time plot settings
plot_width = 300
plot_height = 100
plot_x = (SCREEN_WIDTH - plot_width) // 2
plot_y = SCREEN_HEIGHT - 300  # Spacing for plot below the zones

# Countdown timer (60 seconds)
game_duration = 60  # Duration in seconds
timer = game_duration * 30  # 30 FPS for 60 seconds

# Heat loss function (uses global outside air temperature)
def calculate_heat_loss(heat_loss_rate):
    return heat_loss_rate * (70 - global_outside_air_temp) / 20  # Adjust rate based on global outside temp

# Reward calculation based on discussed strategy
def calculate_step_reward(zones):
    global current_reward
    
    total_reward = 0
    total_power = sum(zone["current_kw"] for zone in zones)
    time_left_in_episode = timer // 30

    for zone in zones:
        # Temperature-based reward (comfort)
        temp_diff = abs(zone["room_temp"] - zone["desired_temp"])
        temp_reward = 1 if temp_diff < 1 else 0.5 if temp_diff < 3 else 0
        final_warmup_boost = 1 + (1 / max(1, time_left_in_episode))
        temp_reward *= final_warmup_boost
        
        # Energy penalty
        energy_penalty = -0.005 * zone["current_kw"]
        
        total_reward += temp_reward + energy_penalty

    # Power demand penalty
    high_demand_penalty = -1 if total_power > high_kw_threshold else 0
    total_reward += high_demand_penalty
    
    current_reward += total_reward  # Add to current cumulative reward
    return total_reward

# Final reward based on temperature at 6 AM
def calculate_final_reward(zones):
    all_at_setpoint = all(abs(zone["room_temp"] - zone["desired_temp"]) < 1 for zone in zones)
    final_reward = 10 if all_at_setpoint else -10  # Big reward if all zones are warm, big penalty if not
    return final_reward

# Main game loop
running = True
clock = pygame.time.Clock()

def draw_room(zone, x, y):
    # Change color based on room temperature
    room_color = BLUE if zone["room_temp"] < 65 else RED if zone["room_temp"] > 75 else GREEN
    pygame.draw.rect(screen, room_color, (x, y, 200, 150))  # Each room is 200x150

    # Display temperature inside the room
    temp_text = font.render(f"{int(zone['room_temp'])}F", True, BLACK)
    text_rect = temp_text.get_rect(center=(x + 100, y + 75))
    screen.blit(temp_text, text_rect)

    # Draw the heat pump enabled indicator (red circle)
    if zone["heat_on"]:
        pygame.draw.circle(screen, RED, (x + 100, y + 130), 10)  # Red if the heat pump is enabled

def update_temperature(zone):
    global total_energy_kwh

    # Simulate heat loss due to global outside temperature
    zone["room_temp"] -= calculate_heat_loss(zone["heat_loss"])

    if zone["heat_on"]:
        # If the temperature is below setpoint, turn on the heating element
        if zone["room_temp"] < zone["desired_temp"] - 1:
            if zone["cycle_timer"] <= 0:  # Ensure the 1 second timer has elapsed before turning on heat
                zone["heating_element_on"] = True
                zone["cycle_timer"] = 30  # Reset cycle_timer to 1 second (30 frames at 30 FPS)
        elif zone["room_temp"] >= zone["desired_temp"] and zone["heating_element_on"]:
            # If the room is at or above setpoint, start the 1 second cycle timer to turn off heat
            if zone["cycle_timer"] > 0:
                zone["cycle_timer"] -= 1
            else:
                zone["heating_element_on"] = False

        # If the heating element is on, increase the temperature
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

def update_combined_power_usage():
    global max_kw_hit

    # Sum up power usage across all zones
    total_power = sum(zone["current_kw"] for zone in zones)
    combined_power_usage.append(total_power)

    # Track maximum power hit
    if total_power > max_kw_hit:
        max_kw_hit = total_power

    # Keep the list length within the width of the plot
    if len(combined_power_usage) > plot_width:
        combined_power_usage.pop(0)

def draw_real_time_plot():
    # Draw the plot background
    pygame.draw.rect(screen, WHITE, (plot_x, plot_y, plot_width, plot_height), 1)

    # Draw the line representing combined power usage over time
    if len(combined_power_usage) > 1:
        for i in range(1, len(combined_power_usage)):
            x1 = plot_x + i - 1
            y1 = plot_y + plot_height - (combined_power_usage[i - 1] / (max_kw * num_zones)) * plot_height
            x2 = plot_x + i
            y2 = plot_y + plot_height - (combined_power_usage[i] / (max_kw * num_zones)) * plot_height
            pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 2)

    # Add labels for the plot
    kw_label = font.render("kW", True, BLACK)
    screen.blit(kw_label, (plot_x - 30, plot_y + plot_height // 2))

    # Calculate and display total combined kW
    total_kw = sum(zone["current_kw"] for zone in zones)
    combined_kw_text = font.render(f"Total kW: {round(total_kw, 2)}", True, BLACK)
    screen.blit(combined_kw_text, (plot_x + plot_width + 40, plot_y))

    # Display global outside air temperature
    outside_temp_text = font.render(f"Outside Temp: {global_outside_air_temp} F", True, BLACK)
    screen.blit(outside_temp_text, (plot_x + plot_width + 40, plot_y + 40))

def draw_energy_consumption():
    # Display total energy consumption (kWh)
    energy_text = font.render(f"Elapsed Electrical Energy: {round(total_energy_kwh, 2)} kWh", True, BLACK)
    screen.blit(energy_text, (plot_x, plot_y + plot_height + 20))  # Positioned below the chart

def draw_timer():
    # Show the remaining time below the energy consumption
    time_left = timer // 30  # Convert frames back to seconds
    timer_text = font.render(f"Time Remaining: {time_left}s", True, BLACK)
    screen.blit(timer_text, (plot_x, plot_y + plot_height + 60))  # Positioned below the energy consumption

def draw_current_reward():
    # Display current reward on screen
    reward_text = font.render(f"Current Reward: {round(current_reward, 2)}", True, BLACK)
    screen.blit(reward_text, (plot_x, plot_y + plot_height + 100))  # Positioned below timer

def show_final_screen():
    screen.fill(WHITE)
    # Display final metrics on a new screen
    final_temp_text = font.render(f"Final Temp: {int(zones[0]['room_temp'])}F", True, BLACK)  # Example for zone 1
    energy_text = font.render(f"Elapsed Electrical Energy: {round(total_energy_kwh, 2)} kWh", True, BLACK)
    max_kw_text = font.render(f"Max Electrical Power Hit: {round(max_kw_hit, 2)} kW", True, BLACK)
    final_reward_text = font.render(f"Final Total Reward: {round(current_reward, 2)}", True, BLACK)

    screen.blit(final_temp_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 120))
    screen.blit(energy_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 60))
    screen.blit(max_kw_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
    screen.blit(final_reward_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60))

    pygame.display.flip()

    # Wait for mouse click to close the final screen
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Iterate over each zone to check if the click was inside it
            for i, zone in enumerate(zones):
                # Calculate the row and column for this zone
                row = i // 5  # 3 rows
                col = i % 5   # 5 columns
                
                # Calculate the top-left corner of this zone
                x = col * 240 + 20  # X position of this zone
                y = row * 180 + 20  # Y position of this zone

                # Check if the click is within the bounds of this zone
                if x <= mouse_x <= x + 200 and y <= mouse_y <= y + 150:
                    # Toggle the heat_on state for this specific zone
                    zone["heat_on"] = not zone["heat_on"]


    # Update temperatures, kW usage, and energy for each zone
    for zone in zones:
        update_temperature(zone)

    # Update the combined power usage
    update_combined_power_usage()

    # Draw each zone in a 3x5 grid
    for i, zone in enumerate(zones):
        row = i // 5  # 3 rows
        col = i % 5  # 5 columns
        x = col * 240 + 20  # Spacing between zones
        y = row * 180 + 20
        draw_room(zone, x, y)

    # Calculate reward at each step and add to the dashboard
    calculate_step_reward(zones)

    # Draw the real-time power plot, energy consumption, the countdown timer, and the current reward
    draw_real_time_plot()
    draw_energy_consumption()
    draw_timer()
    draw_current_reward()

    # Check if time is up
    if timer <= 0:
        # Calculate the final reward based on end conditions (temperatures)
        final_reward = calculate_final_reward(zones)
        current_reward += final_reward  # Add final reward to total reward

        # Show the final screen with the metrics
        show_final_screen()
        running = False

    # Decrease the timer
    timer -= 1

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
