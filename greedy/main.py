import random

# Constants
NUM_HEAT_PUMPS = 60  # Increased number of heat pumps to generate up to 300 kW
POWER_THRESHOLD_KW = 250  # Maximum allowed total power usage (kW)
INITIAL_BUILDING_LOAD_KW = 50  # Initial building load at 3 AM (kW)
SCHOOL_START_TIME = 7  # School starts at 7 AM
START_TIME_MINUTES = 180  # 3 AM in minutes
SCHOOL_START_TIME_MINUTES = 420  # 7 AM in minutes

# Model constants
SLOPE = 0.026
INTERCEPT = 7.25

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
        'DesiredTempRise': desired_temp_rise
    }

# Input: Fake cold morning temperature
outside_temp = 20  # Example cold morning temperature at 3 AM in Fahrenheit

# Data structure to hold results
results = []

# Track total power usage including the initial building load
active_power_usage_kw = INITIAL_BUILDING_LOAD_KW

# Start the scheduling
current_time_minutes = START_TIME_MINUTES  # Start at 3 AM

# Main loop for scheduling heat pumps
for hp_id, config in heat_pumps.items():
    power_kw = config['Power_kW']
    desired_temp_rise = config['DesiredTempRise']
    
    # Calculate warm-up time for this heat pump
    warmup_time_minutes = calculate_warmup_time(desired_temp_rise, outside_temp)
    
    # Calculate the latest possible start time to ensure warm-up by 7 AM
    latest_start_time = SCHOOL_START_TIME_MINUTES - warmup_time_minutes
    
    # Find a start time that does not exceed the power threshold
    while current_time_minutes < latest_start_time:
        # Check if adding this heat pump keeps the power below the threshold
        if active_power_usage_kw + power_kw <= POWER_THRESHOLD_KW:
            # Start this heat pump
            active_power_usage_kw += power_kw
            results.append({
                'HeatPumpID': hp_id,
                'Power_kW': power_kw,
                'DesiredTempRise': desired_temp_rise,
                'StartTime': current_time_minutes,
                'WarmupTimeMinutes': warmup_time_minutes
            })
            # Move to the next heat pump
            break
        else:
            # If adding this heat pump exceeds the threshold, increment the current time
            current_time_minutes += 1
            # Simulate power consumption drop-off (assuming previous HPs have completed warm-up)
            # For simplicity, assume a power drop of 3 kW every minute (representing some HPs finishing)
            # Adjust as needed for the actual power drop profile
            active_power_usage_kw = max(INITIAL_BUILDING_LOAD_KW, active_power_usage_kw - 3)

# Output the results
for result in results:
    print(f"Heat Pump {result['HeatPumpID']}: Power = {result['Power_kW']} kW, "
          f"Desired Temp Rise = {result['DesiredTempRise']}°F, "
          f"Start Time = {result['StartTime'] / 60:.2f} AM, "
          f"Warm-up Time = {result['WarmupTimeMinutes']:.2f} minutes")
