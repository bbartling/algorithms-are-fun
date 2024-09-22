class ConfigError(Exception):
    """Custom exception for invalid configuration"""

    pass


class AHUStaticPressureReset:
    def __init__(self, config_dict):
        """Initialize the AHU static pressure reset algorithm with the given config."""
        self.config_dict = config_dict
        self.validate_ahu_config(config_dict)
        self.current_sp = config_dict["SP0"]
        self.total_pressure_increase = 0

    def validate_ahu_config(self, config_dict):
        """Validate AHU config dictionary for required keys and correct data types."""
        required_keys = {
            "VAV_BOXES": list,  # List of VAV boxes with damper position, airflow, and airflow setpoint
            "SP0": (int, float),  # Initial static pressure setpoint
            "SPmin": (int, float),  # Minimum static pressure
            "SPmax": (int, float),  # Maximum static pressure
            "I": int,  # Ignore requests count
            "SPtrim": (int, float),  # Trim amount
            "SPres": (int, float),  # Response amount
            "SPres_max": (int, float),  # Maximum response amount
        }

        for key, expected_type in required_keys.items():
            if key not in config_dict:
                raise ConfigError(f"Missing required config key: {key}")
            if not isinstance(config_dict[key], expected_type):
                raise ConfigError(
                    f"Incorrect type for {key}. Expected {expected_type}, got {type(config_dict[key])}"
                )

    def run(self, max_iterations=None):
        """Run the AHU static pressure reset algorithm."""
        I = self.config_dict["I"]
        SPres_max = self.config_dict["SPres_max"]
        SPres = self.config_dict["SPres"]
        SPtrim = self.config_dict["SPtrim"]
        SPmin = self.config_dict["SPmin"]
        SPmax = self.config_dict["SPmax"]

        iterations = 0

        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break

            total_reset_requests = 0
            damper_data = []

            # Collect damper positions, airflow measurements, and airflow setpoints for all VAV boxes
            for vav_box in self.config_dict["VAV_BOXES"]:
                damper_position = vav_box["damper_position"]
                airflow = vav_box["airflow"]  # Measured airflow
                airflow_setpoint = vav_box["airflow_setpoint"]  # Airflow setpoint
                damper_data.append((damper_position, airflow, airflow_setpoint))

            # Sort the damper data by damper position in descending order
            damper_data.sort(reverse=True, key=lambda x: x[0])

            # Ignore the highest I dampers
            damper_data = damper_data[I:]

            # Logic to determine the number of reset requests for the remaining VAV boxes
            for damper_position, airflow, airflow_setpoint in damper_data:
                if airflow_setpoint > 0 and damper_position > 95:
                    if airflow < 0.5 * airflow_setpoint:
                        total_reset_requests += 3
                    elif airflow < 0.7 * airflow_setpoint:
                        total_reset_requests += 2
                    else:
                        total_reset_requests += 1
                elif damper_position < 95:
                    total_reset_requests = 0

            # Adjust the static pressure
            if total_reset_requests > 0:
                # Only increase pressure if we haven't reached the maximum increase (SPres_max)
                if self.total_pressure_increase < SPres_max:
                    pressure_increase = min(
                        SPres, SPres_max - self.total_pressure_increase
                    )  # Ensure we don’t exceed SPres_max
                    self.current_sp = min(
                        self.current_sp + pressure_increase, SPmax
                    )  # Cap at SPmax
                    self.total_pressure_increase += pressure_increase
                else:
                    print(
                        f"Maximum pressure increase ({SPres_max} inches) reached, no further increase."
                    )
            else:
                self.current_sp = max(self.current_sp + SPtrim, SPmin)  # Cap at SPmin

            print(f"Adjusting static pressure to {self.current_sp} inches WC")

            iterations += 1


# Simulated data to run the algorithm
config = {
    "VAV_BOXES": [
        {"damper_position": 98, "airflow": 0.35, "airflow_setpoint": 0.8},
        {"damper_position": 96, "airflow": 0.45, "airflow_setpoint": 0.6},
        {"damper_position": 92, "airflow": 0.2, "airflow_setpoint": 0.4},
        {"damper_position": 90, "airflow": 0.15, "airflow_setpoint": 0.3},
    ],
    "SP0": 1.5,  # Initial static pressure setpoint
    "SPmin": 0.5,  # Minimum static pressure
    "SPmax": 3.0,  # Maximum static pressure
    "I": 1,  # Ignore the highest 1 damper
    "SPtrim": -0.1,  # Trim amount when no reset requests
    "SPres": 0.2,  # Response amount per reset request
    "SPres_max": 1.0,  # Maximum response increase allowed
}

ahu_pressure_reset = AHUStaticPressureReset(config)
ahu_pressure_reset.run(max_iterations=10)  # Simulate for 10 iterations
