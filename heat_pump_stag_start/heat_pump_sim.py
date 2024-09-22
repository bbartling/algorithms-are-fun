import random

# Constants
NUM_HEAT_PUMPS = 60  # Number of heat pumps
SCHOOL_START_TIME_MINUTES = 420  # 7 AM in minutes

# Warm-up Rate=(SLOPE×Outside Temperature)+INTERCEPT
SLOPE = 0.026
INTERCEPT = 7.25

OUTSIDE_TEMP = 20


# Function to calculate warm-up time for a given temperature rise
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
    heat_pumps[hp_id] = {"Power_kW": power_kw, "DesiredTempRise": desired_temp_rise}


# Calculate start times for each heat pump
def calculate_start_times():
    results = []
    for hp_id, config in heat_pumps.items():
        power_kw = config["Power_kW"]
        desired_temp_rise = config["DesiredTempRise"]
        warmup_time_minutes = calculate_warmup_time(desired_temp_rise, OUTSIDE_TEMP)
        latest_start_time = SCHOOL_START_TIME_MINUTES - warmup_time_minutes
        results.append(
            {
                "HeatPumpID": hp_id,
                "Power_kW": power_kw,
                "DesiredTempRise": desired_temp_rise,
                "Warm-upTimeMinutes": warmup_time_minutes,
                "LatestStartTime": latest_start_time,
            }
        )
    return results


# Run the calculation
initial_results = calculate_start_times()

# Output the results for each heat pump
for result in initial_results:
    print(
        f"Heat Pump {result['HeatPumpID']}: Power = {result['Power_kW']} kW, "
        f"Desired Temp Rise = {result['DesiredTempRise']}°F, "
        f"Warm-up Time = {result['Warm-upTimeMinutes']:.2f} minutes, "
        f"Latest Start Time = {result['LatestStartTime'] / 60:.2f} AM"
    )
