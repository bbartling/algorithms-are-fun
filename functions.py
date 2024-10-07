import pygame


# Heat loss function (uses global outside air temperature)
def calculate_heat_loss(heat_loss_rate, global_outside_air_temp):
    # Scale the heat loss rate to make the temperature decrease slower
    scaled_heat_loss = heat_loss_rate * (70 - global_outside_air_temp) / 20
    return scaled_heat_loss * 0.5  # Multiply by 0.5 to make the heat loss slower


# Reward calculation based on discussed strategy
def calculate_step_reward(zones, current_reward, high_kw_threshold, timer):
    total_reward = 0
    total_power = sum(zone["current_kw"] for zone in zones)
    time_left_in_episode = timer // 30

    for zone in zones:
        temp_diff = abs(zone["room_temp"] - zone["desired_temp"])
        temp_reward = 1 if temp_diff < 1 else 0.5 if temp_diff < 3 else 0
        final_warmup_boost = 1 + (1 / max(1, time_left_in_episode))
        temp_reward *= final_warmup_boost

        energy_penalty = -0.005 * zone["current_kw"]
        total_reward += temp_reward + energy_penalty

    high_demand_penalty = -1 if total_power > high_kw_threshold else 0
    total_reward += high_demand_penalty
    current_reward += total_reward


# Final reward based on temperature at 6 AM
def calculate_final_reward(zones):
    all_at_setpoint = all(
        abs(zone["room_temp"] - zone["desired_temp"]) < 1 for zone in zones
    )
    final_reward = (
        10 if all_at_setpoint else -10
    )  # Big reward if all zones are warm, big penalty if not
    return final_reward


def update_temperature(zone, max_kw, fan_kw_percent, heating_power, total_energy_kwh):
    # Simulate heat loss due to global outside temperature
    zone["room_temp"] -= calculate_heat_loss(zone["heat_loss"], zone["outside_temp"])

    if zone["heat_on"]:
        if zone["room_temp"] < zone["desired_temp"] - 1:
            if zone["cycle_timer"] <= 0:
                zone["heating_element_on"] = True
                zone["cycle_timer"] = 30  # Start the cycle timer
        elif zone["room_temp"] >= zone["desired_temp"] and zone["heating_element_on"]:
            if zone["cycle_timer"] > 0:
                zone["cycle_timer"] -= 1
            else:
                zone["heating_element_on"] = False
                if not zone[
                    "at_setpoint"
                ]:  # Trigger this only the first time the zone hits the setpoint
                    zone["at_setpoint"] = True
                    print(
                        f"Zone has reached setpoint: {zone['desired_temp']}F. Power will be cut by 50%."
                    )

        # Heating logic
        if zone["heating_element_on"]:
            zone["room_temp"] += heating_power * 0.6  # Make the simulation slower
            zone["current_kw"] = max_kw  # Full power when heating
        else:
            zone["current_kw"] = (
                max_kw * fan_kw_percent
            )  # Power usage when fan is running

        # Reduce power by 50% once the setpoint is reached
        if zone["at_setpoint"]:
            zone["current_kw"] *= 0.5  # Cut power by 50% once setpoint is reached
    else:
        zone["current_kw"] = 0  # No power usage if system is off

    # Clamp temperature to within min and max limits
    zone["room_temp"] = max(40, min(100, zone["room_temp"]))

    # Update energy consumption based on current power (kW) and time (in hours)
    time_in_hours = 1 / (30 * 3600) * 360  # Scaling to 6 hours
    total_energy_kwh += zone["current_kw"] * time_in_hours

    return total_energy_kwh  # Return the updated total energy in kWh


def update_combined_power_usage(
    zones, combined_power_usage, plot_width, max_kw, num_zones, max_kw_hit
):
    total_power = sum(zone["current_kw"] for zone in zones)
    combined_power_usage.append(total_power)

    # Update max_kw_hit if the current total power exceeds the previous max_kw_hit
    if total_power > max_kw_hit:
        max_kw_hit = total_power

    # Keep the list length within the width of the plot
    if len(combined_power_usage) > plot_width:
        combined_power_usage.pop(0)

    return max_kw_hit  # Return the updated max_kw_hit value


def draw_room(zone, x, y, screen, BLUE, RED, GREEN, BLACK, font):
    room_color = (
        BLUE if zone["room_temp"] < 65 else RED if zone["room_temp"] > 75 else GREEN
    )
    pygame.draw.rect(screen, room_color, (x, y, 200, 150))
    temp_text = font.render(f"{int(zone['room_temp'])}F", True, BLACK)
    text_rect = temp_text.get_rect(center=(x + 100, y + 75))
    screen.blit(temp_text, text_rect)

    if zone["heat_on"]:
        pygame.draw.circle(screen, RED, (x + 100, y + 130), 10)


def draw_real_time_plot(
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
):
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
    combined_kw_text = font.render(f"Total kW: {round(total_kw, 2)}", True, (0, 0, 0))
    screen.blit(combined_kw_text, (plot_x + plot_width + 40, plot_y))

    high_kw_text = font.render(
        f"High kW Limit: {high_kw_threshold} kW", True, (0, 0, 0)
    )
    screen.blit(high_kw_text, (plot_x + plot_width + 40, plot_y + 40))

    outside_temp_text = font.render(
        f"Outside Temp: {global_outside_air_temp} F", True, (0, 0, 0)
    )
    screen.blit(outside_temp_text, (plot_x + plot_width + 40, plot_y + 80))


def draw_energy_consumption(
    screen, plot_x, plot_y, plot_height, total_energy_kwh, font
):
    energy_text = font.render(
        f"Elapsed Electrical Energy: {round(total_energy_kwh, 2)} kWh", True, (0, 0, 0)
    )
    screen.blit(energy_text, (plot_x, plot_y + plot_height + 20))


def draw_timer(screen, plot_x, plot_y, plot_height, timer, font):
    time_left = timer // 30
    timer_text = font.render(f"Time Remaining: {time_left}s", True, (0, 0, 0))
    screen.blit(timer_text, (plot_x, plot_y + plot_height + 60))


def draw_max_kw_hit(screen, font, max_kw_hit, plot_x, plot_y, plot_height):
    # Display the maximum electrical power hit during the simulation
    max_kw_text = f"Max Electrical Power Hit: {round(max_kw_hit, 2)} kW"
    max_kw_text_formatted = font.render(max_kw_text, True, (0, 0, 0))
    # Display the text on the screen (you can adjust the position as needed)
    screen.blit(max_kw_text_formatted, (plot_x, plot_y + plot_height + 100))


def calculate_room_temp_stats(zones):
    temps = [zone["room_temp"] for zone in zones]
    max_temp = max(temps)
    min_temp = min(temps)
    avg_temp = sum(temps) / len(temps)
    return max_temp, min_temp, avg_temp


def show_final_screen(
    screen,
    font,
    zones,
    total_energy_kwh,
    max_kw_hit,
    current_reward,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
):
    screen.fill((255, 255, 255))

    # Calculate max, min, and average temperatures
    max_temp, min_temp, avg_temp = calculate_room_temp_stats(zones)

    # Display final temperature
    final_temp_text = f"Final Temp: {int(zones[0]['room_temp'])}F"
    final_temp_text_formatted = font.render(final_temp_text, True, (0, 0, 0))

    # Display energy, power, and reward
    energy_text = f"Elapsed Electrical Energy: {round(total_energy_kwh, 2)} kWh"
    energy_text_formatted = font.render(energy_text, True, (0, 0, 0))

    max_kw_text = f"Max Electrical Power Hit: {round(max_kw_hit, 2)} kW"
    max_kw_text_formatted = font.render(max_kw_text, True, (0, 0, 0))

    final_reward_text = f"Final Total Reward: {round(current_reward, 2)}"
    final_reward_text_formatted = font.render(final_reward_text, True, (0, 0, 0))

    # Display max, min, and average temperatures
    max_temp_text = f"Max Room Temp: {round(max_temp, 2)}F"
    min_temp_text = f"Min Room Temp: {round(min_temp, 2)}F"
    avg_temp_text = f"Average Room Temp: {round(avg_temp, 2)}F"

    max_temp_text_formatted = font.render(max_temp_text, True, (0, 0, 0))
    min_temp_text_formatted = font.render(min_temp_text, True, (0, 0, 0))
    avg_temp_text_formatted = font.render(avg_temp_text, True, (0, 0, 0))

    # Blit the texts to the screen
    screen.blit(
        final_temp_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150)
    )
    screen.blit(
        energy_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 120)
    )
    screen.blit(
        max_kw_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 90)
    )
    screen.blit(
        final_reward_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 60)
    )

    # Blit the temperature stats
    screen.blit(
        max_temp_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30)
    )
    screen.blit(min_temp_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
    screen.blit(
        avg_temp_text_formatted, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 30)
    )

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
