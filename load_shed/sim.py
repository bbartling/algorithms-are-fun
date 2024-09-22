import time
from load_shed import LoadShed


# Simulated config for load shedding
config = {
    "POWER_THRESHOLD": 120.0,  # Threshold to initiate load shedding
    "STAGE_UP_TIMER": 5,  # Time before moving to the next stage (seconds)
    "STAGE_DOWN_TIMER": 5,  # Time before releasing a stage (seconds)
    "stages": [
        {"description": "Stage 1"},
        {"description": "Stage 2"},
    ],
}

# Simulated building power data
simulated_power_data = [130, 100, 130, 100, 130, 100]

# Create the LoadShed instance
load_shed = LoadShed(config)

# max_iterations for the loop (seconds)
max_iterations = 600  # Run for 10 minutes (600 seconds)

# Track time outside the LoadShed class
start_time = time.monotonic()

# Use a for loop to iterate through the simulation
for iteration in range(max_iterations):
    current_time = time.monotonic() - start_time  # Simulate elapsed time
    current_power = simulated_power_data[
        (iteration // 30) % len(simulated_power_data)
    ]  # Change power every 30 seconds

    # Get current status including timers, power, and threshold
    status = load_shed.get_status(current_time, current_power)

    # Printing current state and power
    print(f"Current Stage: {load_shed.current_stage}")
    print(f"Time Elapsed: {status['time_elapsed']} seconds")
    print(f"Up Timer Remaining: {status['up_timer_remaining']} seconds")
    print(f"Down Timer Remaining: {status['down_timer_remaining']} seconds")
    print(f"Current Power: {status['current_power']} kW")
    print(f"Power Threshold: {status['power_threshold']} kW")
    print(f"State: {status['state']}")
    print("=" * 50)

    time.sleep(1)  # Simulate sleep for 1 second (instead of 60 for quicker demo)
