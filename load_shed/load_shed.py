class ConfigError(Exception):
    """Custom exception for invalid configuration"""
    pass


class LoadShed:
    def __init__(self, config_dict):
        """Initialize the Load Shedding algorithm with the given config."""
        self.config_dict = config_dict
        self.validate_config(config_dict)
        self.last_operation_time = 0
        self.current_stage = 0
        self.stages = config_dict.get("stages", [])
        self.sleep_interval_seconds = config_dict.get("SLEEP_INTERVAL_SECONDS", 60)
        self.stage_up_timer = config_dict.get("STAGE_UP_TIMER", 300)
        self.stage_down_timer = config_dict.get("STAGE_DOWN_TIMER", 300)
        self.power_threshold = config_dict.get("POWER_THRESHOLD", 120.0)

        # Simulated building power data (can be replaced with real sensor readings)
        self.simulated_power_data = [130, 115, 125, 110, 105, 130, 135, 140, 100]

    def validate_config(self, config_dict):
        """Validate config dictionary for required keys and correct data types."""
        required_keys = {
            "POWER_THRESHOLD": (int, float),
            "SLEEP_INTERVAL_SECONDS": (int, float),
            "STAGE_UP_TIMER": (int, float),
            "STAGE_DOWN_TIMER": (int, float),
            "stages": list,
        }

        for key, expected_type in required_keys.items():
            if key not in config_dict:
                raise ConfigError(f"Missing required config key: {key}")
            if not isinstance(config_dict[key], expected_type):
                raise ConfigError(
                    f"Incorrect type for {key}. Expected {expected_type}, got {type(config_dict[key])}"
                )

        for i, stage in enumerate(config_dict["stages"], 1):
            if not isinstance(stage, dict):
                raise ConfigError(f"Stage {i} must be a dictionary, got {type(stage)}")
            if "description" not in stage:
                raise ConfigError(f"Stage {i} is missing the required 'description' key")

    def should_initiate_stage(self, building_power, time_elapsed, stage_timer_remaining):
        """Determine whether a new stage should be initiated based on power and timer."""
        return building_power > self.power_threshold and time_elapsed >= stage_timer_remaining

    def should_release_stage(self, building_power, time_elapsed, stage_timer_remaining):
        """Determine whether a stage should be released based on power and timer."""
        return building_power <= self.power_threshold and time_elapsed >= stage_timer_remaining

    def run(self, max_iterations=None):
        """Run the load shedding algorithm."""
        iterations = 0
        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break

            # Simulate reading building power
            building_power = self.simulated_power_data[iterations % len(self.simulated_power_data)]
            current_time = iterations * self.sleep_interval_seconds  # Simulate time passing
            time_elapsed = current_time - self.last_operation_time
            up_timer_remaining = max(0, self.stage_up_timer - time_elapsed)
            down_timer_remaining = max(0, self.stage_down_timer - time_elapsed)

            print(f"Iteration {iterations}: Building Power = {building_power} kW")

            # Check to initiate a new stage
            if self.should_initiate_stage(building_power, time_elapsed, up_timer_remaining):
                if self.current_stage < len(self.stages):
                    self.current_stage += 1
                    self.last_operation_time = current_time
                    self.initiate_stage(self.stages[self.current_stage - 1])

            # Check to release a stage
            if self.should_release_stage(building_power, time_elapsed, down_timer_remaining):
                if self.current_stage > 0:
                    self.release_stage(self.stages[self.current_stage - 1])
                    self.current_stage -= 1
                    self.last_operation_time = current_time

            iterations += 1
            print(f"Sleeping for {self.sleep_interval_seconds} seconds...\n")

    def initiate_stage(self, stage_config):
        """Simulate initiating a load-shedding stage."""
        print(f"Stage Up: {stage_config.get('description', 'No Description')}")

    def release_stage(self, stage_config):
        """Simulate releasing a load-shedding stage."""
        print(f"Stage Down: {stage_config.get('description', 'No Description')}")


# Simulated config for load shedding (without detailed BACnet points)
config = {
    "POWER_THRESHOLD": 120.0,  # Threshold to initiate load shedding
    "SLEEP_INTERVAL_SECONDS": 60,  # Interval between checks (seconds)
    "STAGE_UP_TIMER": 300,  # Time before moving to the next stage (seconds)
    "STAGE_DOWN_TIMER": 300,  # Time before releasing a stage (seconds)
    "stages": [
        {
            "description": "Stage 1"
        },
        {
            "description": "Stage 2"
        }
    ]
}

# Create the LoadShed instance and run it
load_shed = LoadShed(config)
load_shed.run(max_iterations=10)
