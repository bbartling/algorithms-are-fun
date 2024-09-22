class ConfigError(Exception):
    """Custom exception for invalid configuration."""

    pass


class PowerError(Exception):
    """Custom exception for invalid power data."""

    pass


class LoadShed:
    IDLE = "IDLE"
    STAGE_UP_PENDING = "STAGE_UP_PENDING"
    STAGE_DOWN_PENDING = "STAGE_DOWN_PENDING"
    AT_MAX_STAGE = "AT_MAX_STAGE"

    def __init__(self, config_dict):
        """Initialize the Load Shedding algorithm with the given config."""
        try:
            self.config_dict = config_dict
            self.validate_config(config_dict)
        except ConfigError as e:
            raise ConfigError(f"Configuration Error: {e}")

        self.last_operation_time = 0  # Initialize the operation time
        self.current_stage = 0  # Track the current stage
        self.stages = config_dict.get("stages", [])
        self.stage_up_timer = config_dict.get("STAGE_UP_TIMER", 300)
        self.stage_down_timer = config_dict.get("STAGE_DOWN_TIMER", 300)
        self.power_threshold = config_dict.get("POWER_THRESHOLD", 120.0)

        # Internal variables to manage timers
        self.time_elapsed = 0
        self.up_timer_remaining = self.stage_up_timer
        self.down_timer_remaining = self.stage_down_timer
        self.state = self.IDLE

    def validate_config(self, config_dict):
        """Validate config dictionary for required keys and correct data types."""
        required_keys = {
            "POWER_THRESHOLD": (int, float),
            "STAGE_UP_TIMER": (int, float),
            "STAGE_DOWN_TIMER": (int, float),
            "stages": list,
        }

        for key, expected_type in required_keys.items():
            if key not in config_dict:
                raise ConfigError(f"Missing required config key: {key}")
            if not isinstance(config_dict[key], expected_type):
                raise ConfigError(
                    f"Incorrect type for {key}. Expected {expected_type}, got {type(config_dict[key])}."
                )

        for i, stage in enumerate(config_dict["stages"], 1):
            if not isinstance(stage, dict):
                raise ConfigError(f"Stage {i} must be a dictionary, got {type(stage)}")
            if "description" not in stage:
                raise ConfigError(
                    f"Stage {i} is missing the required 'description' key"
                )

    def update_timers(self, current_time):
        """Update the elapsed time and remaining timers based on the current state."""
        if self.state == self.STAGE_UP_PENDING:
            self.time_elapsed = current_time - self.last_operation_time
            self.up_timer_remaining = max(0, self.stage_up_timer - self.time_elapsed)
        elif self.state == self.STAGE_DOWN_PENDING:
            self.time_elapsed = current_time - self.last_operation_time
            self.down_timer_remaining = max(
                0, self.stage_down_timer - self.time_elapsed
            )
        else:
            self.time_elapsed = 0
            self.up_timer_remaining = self.stage_up_timer
            self.down_timer_remaining = self.stage_down_timer

    def validate_power(self, current_power):
        """Ensure that the current power is a valid number and not a negative value."""
        if not isinstance(current_power, (int, float)):
            raise PowerError(
                f"Invalid power type: {type(current_power)}. Expected int or float."
            )
        if current_power < 0:
            raise PowerError(
                f"Invalid power value: {current_power}. Power must be non-negative."
            )

    def manage_stage(self, current_time, current_power):
        """Manage stage transitions based on building power."""
        # Validate power input
        try:
            self.validate_power(current_power)
        except PowerError as e:
            print(f"Power Error: {e}")
            return  # Skip further processing if power is invalid

        # Update timers
        self.update_timers(current_time)

        if current_power > self.power_threshold and self.state != self.AT_MAX_STAGE:
            # We're in the process of staging up
            self.state = self.STAGE_UP_PENDING
            if self.up_timer_remaining == 0:
                if self.current_stage < len(self.stages):
                    self.current_stage += 1
                    self.last_operation_time = current_time
                    print(f"Staged up to {self.current_stage}")
                    if self.current_stage == len(self.stages):
                        self.state = self.AT_MAX_STAGE
                self.reset_timers()

        elif current_power <= self.power_threshold:
            # We're in the process of staging down
            self.state = self.STAGE_DOWN_PENDING
            if self.down_timer_remaining == 0:
                if self.current_stage > 0:
                    self.current_stage -= 1
                    self.last_operation_time = current_time
                    print(f"Staged down to {self.current_stage}")
                self.reset_tTimers()

    def reset_timers(self):
        """Reset the timers after stage transitions."""
        self.up_timer_remaining = self.stage_up_timer
        self.down_timer_remaining = self.stage_down_timer

    def get_status(self, current_time, current_power):
        """Return the current values of the timers, power, and threshold."""
        try:
            self.manage_stage(current_time, current_power)

            return {
                "error": None, 
                "time_elapsed": round(self.time_elapsed, 1),
                "up_timer_remaining": round(self.up_timer_remaining, 1),
                "down_timer_remaining": round(self.down_timer_remaining, 1),
                "current_power": current_power,
                "power_threshold": self.power_threshold,
                "state": self.state,
            }

        except Exception as e:
            
            print(f"Error managing stages: {e}")
            return {
                "error": str(e), 
                "time_elapsed": None,
                "up_timer_remaining": None,
                "down_timer_remaining": None,
                "current_power": None,
                "power_threshold": None,
                "state": None,
            }
