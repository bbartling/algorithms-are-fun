import random

# Constants
NUM_HEAT_PUMPS = 60  # Number of heat pumps to generate up to 300 kW
POWER_THRESHOLD_KW = 250  # Maximum allowed total power usage (kW)
INITIAL_BUILDING_LOAD_KW = 50  # Initial building load at 3 AM (kW)
START_TIME_MINUTES = 180  # 3 AM in minutes
SCHOOL_START_TIME_MINUTES = 420  # 7 AM in minutes
TOTAL_MINUTES = SCHOOL_START_TIME_MINUTES - START_TIME_MINUTES  # Total warm-up window

# Model constants
SLOPE = 0.026
INTERCEPT = 7.25

# Input: Fake cold morning temperature
outside_temp = 20  # Example cold morning temperature at 3 AM in Fahrenheit

# Function to calculate warm-up time
def calculate_warmup_time(desired_temp_rise, outside_temp):
    warmup_rate = SLOPE * outside_temp + INTERCEPT
    time_hours = desired_temp_rise / warmup_rate
    time_minutes = time_hours * 60
    return time_minutes

# Generate random heat pump configurations
heat_pumps = {}
for hp_id in range(1, NUM_HEAT_PUMPS + 1):
    # Randomly assign power (3 kW or 6 kW)
    power_kw = random.choice([3, 6])
    
    # Randomly generate a desired temperature rise between 5 and 15 degrees Fahrenheit
    desired_temp_rise = random.uniform(5, 15)
    
    # Store this heat pump's configuration in a dictionary
    heat_pumps[hp_id] = {
        'Power_kW': power_kw,
        'DesiredTempRise': desired_temp_rise,
        'WarmupTime': calculate_warmup_time(desired_temp_rise, outside_temp)
    }

# Initialize DP table
# dp[t][p]: Maximum number of heat pumps warmed by time t with power p
dp = [[0] * (POWER_THRESHOLD_KW + 1) for _ in range(TOTAL_MINUTES + 1)]
# Track the schedule for decisions
schedule = [[[] for _ in range(POWER_THRESHOLD_KW + 1)] for _ in range(TOTAL_MINUTES + 1)]

# Initialize the power usage at the initial building load
dp[0][INITIAL_BUILDING_LOAD_KW] = 0  # At time 0 with initial building load
schedule[0][INITIAL_BUILDING_LOAD_KW] = []  # Empty list to track scheduled heat pumps

# Fill the DP table
for i in range(1, NUM_HEAT_PUMPS + 1):
    power_kw = heat_pumps[i]['Power_kW']
    warmup_time = int(heat_pumps[i]['WarmupTime'])
    
    # Go through the DP table backwards to avoid recomputing states within the same iteration
    for t in range(TOTAL_MINUTES, warmup_time - 1, -1):
        for p in range(POWER_THRESHOLD_KW, power_kw - 1, -1):
            # Only update if the previous state is valid
            if dp[t - warmup_time][p - power_kw] >= 0:
                # Check if adding this heat pump increases the count
                if dp[t][p] < dp[t - warmup_time][p - power_kw] + 1:
                    dp[t][p] = dp[t - warmup_time][p - power_kw] + 1
                    # Record the schedule by copying previous schedule and adding the current heat pump
                    schedule[t][p] = schedule[t - warmup_time][p - power_kw] + [(i, t)]

# Find the best solution by maximizing the number of heat pumps warmed
max_heat_pumps = 0
best_power = -1
best_schedule = []

for p in range(POWER_THRESHOLD_KW + 1):
    if dp[TOTAL_MINUTES][p] > max_heat_pumps:
        max_heat_pumps = dp[TOTAL_MINUTES][p]
        best_power = p
        best_schedule = schedule[TOTAL_MINUTES][p]

# Output the results
if max_heat_pumps == 0:
    print("No feasible solution found.")
else:
    print(f"Maximum number of heat pumps warmed: {max_heat_pumps} with total power: {best_power} kW")
    print("Schedule of heat pump starts:")
    for hp_id, start_time in best_schedule:
        warmup_time = heat_pumps[hp_id]['WarmupTime']
        print(f"Heat Pump {hp_id}: Power = {heat_pumps[hp_id]['Power_kW']} kW, "
              f"Start Time = {(START_TIME_MINUTES + start_time) / 60:.2f} AM, "
              f"Warm-up Time = {warmup_time:.2f} minutes")
