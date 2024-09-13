import numpy as np

# Mock data for the next 24 hours (hourly weather forecast and power costs)
weather_forecast = [75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 
                    63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52]  # Example: outside temp (°F)
power_costs = [0.15, 0.14, 0.12, 0.11, 0.13, 0.16, 0.18, 0.20, 0.22, 0.21, 
               0.19, 0.18, 0.17, 0.15, 0.14, 0.12, 0.11, 0.10, 0.13, 0.14, 
               0.16, 0.18, 0.19, 0.20]  # Example: cost per kWh ($)

# Mock HVAC state space (e.g., SpaceTemp, VAV2_6_SpaceTemp, VAV2_7_SpaceTemp, fan speed)
state_space = [
    (72, 71, 70, 50),  # Tuple represents (SpaceTemp, VAV2_6_SpaceTemp, VAV2_7_SpaceTemp, fan speed)
    (74, 73, 72, 60),
    (70, 69, 68, 40),
    (68, 67, 66, 30)
]

# Transition cost function (example: cost for adjusting setpoints/fan speed)
def transition_cost(prev_state, current_state):
    adjustment_cost = sum(np.abs(np.array(current_state) - np.array(prev_state))) * 0.05
    return adjustment_cost  # Example: cost based on magnitude of changes

# Comfort penalty function (penalty for deviating from comfort targets)
def comfort_penalty(state):
    # Assume comfort is defined as maintaining SpaceTemp between 70 and 74 °F
    space_temp = state[0]
    penalty = 0
    if space_temp < 70:
        penalty += (70 - space_temp) * 2  # Penalty for being too cold
    elif space_temp > 74:
        penalty += (space_temp - 74) * 2  # Penalty for being too warm
    return penalty

# Energy consumption function (example: rough estimate of energy consumption)
def energy_consumption(state, weather):
    space_temp, vav2_6, vav2_7, fan_speed = state
    # Example: consumption depends on temperature difference and fan speed
    temp_diff = np.abs(space_temp - weather)
    return temp_diff * 0.1 + fan_speed * 0.05

# Step 1: Initialize the DP table
dp_table = {}

for hour in range(24):
    dp_table[hour] = {}
    for state in state_space:
        dp_table[hour][state] = float('inf')  # Initialize cost to infinity

# Base case: Initial conditions at hour 0
initial_state = (72, 71, 70, 50)  # Example starting state
dp_table[0][initial_state] = 0  # No cost at the start

# Step 2: Populate DP table with costs over 24 hours
for hour in range(1, 24):
    weather = weather_forecast[hour]  # Get weather for this hour
    power_rate = power_costs[hour]  # Get electricity price for this hour
    
    for prev_state in state_space:
        prev_cost = dp_table[hour - 1][prev_state]  # Cost for the previous state
        
        for current_state in state_space:
            # Estimate energy consumption
            energy_used = energy_consumption(current_state, weather)
            
            # Calculate real-time cost
            real_time_cost = energy_used * power_rate
            
            # Calculate transition cost
            transition_cost_value = transition_cost(prev_state, current_state)
            
            # Calculate comfort penalty
            comfort_penalty_value = comfort_penalty(current_state)
            
            # Total cost to move from prev_state at hour-1 to current_state at this hour
            total_cost = prev_cost + real_time_cost + transition_cost_value + comfort_penalty_value
            
            # Update DP table with the minimum cost for reaching current_state at this hour
            dp_table[hour][current_state] = min(dp_table[hour][current_state], total_cost)

# Step 3: Backtrack to find the optimal setpoints for the day
optimal_path = []  # Store the best HVAC settings for each hour
best_state = min(dp_table[23], key=dp_table[23].get)  # Best state at the last hour

# Backtrack to find the optimal path
for hour in range(23, 0, -1):
    optimal_path.insert(0, best_state)  # Add the best state for this hour to the path
    best_state = min(state_space, key=lambda s: dp_table[hour - 1][s] + transition_cost(s, best_state))

# Step 4: Output optimal HVAC settings for the next 24 hours
print("Optimal HVAC Settings for Next 24 Hours:")
for hour, state in enumerate(optimal_path):
    print(f"Hour {hour}: Setpoints = {state}")
