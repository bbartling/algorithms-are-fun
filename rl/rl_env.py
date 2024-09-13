import numpy as np
import pandas as pd
import joblib

class AHUEnvironment:
    def __init__(self):
        # Load processed data
        self.data = pd.read_csv('processed_ahu_data.csv', parse_dates=['timestamp'])
        self.current_step = 0
        self.max_steps = len(self.data)

        # Set a target KW setpoint
        self.target_kw_setpoint = 50.0  # example target, can be modified

        # Load the trained Ridge regression model
        self.ridge_model = joblib.load('ridge_regression_model.pkl')

    def reset(self):
        """Resets the environment to the initial state."""
        self.current_step = 0
        return self._get_current_state()

    def step(self, action):
        """Simulates a step in the environment.

        action: The temperature adjustment (from the RL agent).
        """
        if self.current_step >= self.max_steps:
            done = True
            return None, 0, done

        # Get the current state
        current_state = self._get_current_state()

        # Only adjust temperatures if the AHU is running (Sa_FanSpeed > 5.0)
        sa_fan_speed = current_state['Sa_FanSpeed']
        if sa_fan_speed > 5.0:
            # Update space temperature based on the action
            temp_columns = ['SpaceTemp', 'VAV2_6_SpaceTemp', 'VAV2_7_SpaceTemp', 'VAV3_2_SpaceTemp', 'VAV3_5_SpaceTemp']
            for col in temp_columns:
                current_state[col] = np.clip(current_state[col] + action, 60, 80)  # temp bounds for safety

            # Prepare the feature array for the Ridge model (ensure all 14 features are used)
            features = np.array([current_state[col] for col in self.data.columns if col != 'CurrentKW' and col != 'timestamp']).reshape(1, -1)
            
            # Use Ridge regression model to predict new power consumption
            new_kw = self.ridge_model.predict(features)[0]
        else:
            new_kw = current_state['CurrentKW']  # If AHU is off, no change in power consumption

        # Calculate reward (goal: stay under the target KW)
        reward = -abs(new_kw - self.target_kw_setpoint)  # negative reward for being above the target

        # Move to the next step
        self.current_step += 1
        done = self.current_step >= self.max_steps

        return self._get_current_state(), reward, done

    def _get_current_state(self):
        """Fetches the current state (data row) in the environment."""
        return self.data.iloc[self.current_step].to_dict()
