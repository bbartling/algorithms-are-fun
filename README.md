# rl-is-fun
This is an unfinished hobby project for experimenting with dynamic programming and RL for use in building electrical power management. 
In this setup, we are integrating Ridge regression with a reinforcement learning (RL) agent to optimize energy consumption in an HVAC system. 
The environment, represented by the AHU system, predicts building power usage (`CurrentKW`) based on various input features like space temperatures (`SpaceTemp`, `VAV2_6_SpaceTemp`, etc.) and AHU fan speed (`Sa_FanSpeed`). 
The Ridge regression model, pre-trained on historical data, is used to predict the building's power consumption during each step of the RL agent's actions. 
The RL agent attempts to adjust the zone temperatures (via actions) to minimize power usage and stay under a target setpoint. 
The agent explores different actions (temperature adjustments) and learns from the rewards (based on how close the consumption is to the target), gradually improving its policy to optimize energy efficiency over time.

## FUTURE TODO
Incorporating time-of-day considerations into the RL learning strategy opens up a powerful avenue for optimizing energy consumption based on fluctuating electrical load profiles. 
The next phase of the project would involve integrating time-stamped data into the environment's state, enabling the agent to recognize the time of day and adjust its actions accordingly. 
This time-awareness would allow the RL agent to shift energy-intensive tasks to off-peak hours, where energy is cheaper and more abundant, while minimizing consumption during high-demand, expensive periods.

For example, the RL agent could exploit low-cost periods by adjusting system settings (such as SpaceTemp and VAV2_6_SpaceTemp) to increase cooling during valleys in the load profile. 
During peak times, it would reduce cooling or make other system adjustments to shave off power usage and avoid high costs. 
Moving forward, the next step would be to refine the reward function to incorporate real-time or projected time-of-day pricing, allowing the agent to balance energy costs with comfort by dynamically optimizing its actions based on daily electrical demand fluctuations.