# Flappy Heat Pump HVAC Simulation with Q-Learning

This project simulates an HVAC system with heat pumps and uses reinforcement learning (specifically Q-learning) to optimize the operation of these heat pumps, minimizing power consumption and maximizing comfort across multiple zones.

## Simulation Overview

The simulation environment is inspired by `Flappy Bird`, with the goal of managing electrical power in an HVAC system with heat pumps. The system needs to maintain desired temperatures in several zones, minimize power consumption, and avoid demand peaks (high kW usage).

<p align="center">
  <img src="https://github.com/bbartling/flappy-heat-pump/blob/develop/images/flappy_bird.gif" alt="Flappy GIF">
</p>

### How It Works

The system simulates multiple zones, each with its own temperature and heating needs. The agent can turn on or off the heat in each zone, and the goal is for ***five HVAC heat pump units*** to:
- Maintain comfortable room temperatures.
- Minimize energy consumption (kWh).
- Prevent high power demand peaks (kW).

### Goal of the Game

The goal of the game is to simulate a scenario where a building's HVAC system must warm up a cold building during winter, mimicking the time period from midnight to 6 AM. The challenge is to optimize heating in such a way that electrical demand (kW) and electrical energy consumption (kWh) are minimized, while ensuring the building is comfortably warmed up by the time it is occupied. 

In this simulation, each episode represents 24 time steps, with each step corresponding to 15 minutes in real-time. The bot has 24 steps, symbolizing 6 hours, to optimize the HVAC system's performance before occupants arrive in the building. This fast-paced simulation replicates a real-world scenario where a building operator or an AI bot would work overnight to ensure energy-efficient and effective heating, balancing energy savings with comfort.


### Environment Setup

1. **Action Space**: The agent can toggle heating in each of the zones.
   - For each zone, the agent has an action to either turn the heat on or off.
   - Action space is defined by `spaces.Discrete(self.num_zones)`.

2. **Observation Space**: The environment provides the current temperatures of the zones.
   - Each zone's temperature is represented as a continuous value between 0 and 100.
   - Observation space is `spaces.Box(low=0, high=100, shape=(self.num_zones,), dtype=np.float32)`.

3. **Reward Calculation**:
   - Rewards are based on maintaining temperatures within a comfortable range, minimizing energy consumption, and preventing high demand spikes.

### Q-Learning

In this version, Q-learning is applied to learn the optimal policy for controlling the HVAC system. The agent learns to:
- **Maximize comfort**: Keep the room temperatures within a narrow range (70°F ± 1°F).
- **Minimize energy consumption**: Reduce kWh usage.
- **Manage power demand**: Keep kW usage under a certain threshold.

The Q-learning algorithm works by exploring different actions and updating a Q-table that records the expected rewards for each state-action pair.

#### Q-learning Formula:
- Q(s, a) = Q(s, a) + α [r + γ max(Q(s', a')) - Q(s, a)]

Where:
- `Q(s, a)` is the current value of the state-action pair.
- `α` is the learning rate.
- `r` is the reward.
- `γ` is the discount factor for future rewards.
- `max(Q(s', a'))` is the maximum value of the next state-action pair.

### Reward Policy

The reward policy is designed to emulate the decision-making process of a real-life building operator, incentivizing both energy efficiency and occupant comfort. The policy works by prioritizing three main objectives: first, ensuring that all zones reach the desired temperature during occupancy; second, minimizing the total electrical energy consumption (kWh) required to heat those zones; and third, managing electrical power demand (kW) to avoid costly spikes. 

In real-world HVAC systems, particularly those using heat pumps during cold winters, electricity demand charges can dramatically increase utility bills. By mimicking this challenge in the reward structure, we aim to replicate the considerations a human operator would take when running a building automation system—balancing comfort with cost savings. This is a real-world problem that AI has yet to fully solve, and our approach brings us one step closer by optimizing energy use and demand in a way that makes practical sense in a real building environment.

```python
def calculate_real_life_reward(self, zones, high_kw_threshold, total_energy_kwh, baseline_energy_kwh, debug=False):
    total_reward = 0
    base_pay = 100
    comfort_bonus = 0
    energy_savings_bonus = 0
    demand_management_bonus = 0
    penalties = 0

    total_power = sum(zone["current_kw"] for zone in zones)

    all_within_comfort = all(abs(zone["room_temp"] - zone["desired_temp"]) < 3 for zone in zones)
    if all_within_comfort:
        total_reward += base_pay
    else:
        penalties -= 25

    for zone in zones:
        temp_diff = abs(zone["room_temp"] - zone["desired_temp"])
        if temp_diff < 1:
            comfort_bonus += 10
        elif temp_diff >= 3:
            penalties -= 25

    energy_savings = max(0, baseline_energy_kwh - total_energy_kwh)
    energy_savings_bonus += energy_savings * 2

    if total_power <= high_kw_threshold:
        demand_management_bonus += 20
    else:
        penalties -= 5

    total_reward += comfort_bonus + energy_savings_bonus + demand_management_bonus + penalties
    if total_reward < 0:
        total_reward = 0

    return total_reward
```

### Installation

To install the required packages, run:

```bash
pip install gym pygame numpy
```

Make sure to install specific versions if needed (e.g., for Python 3.9 on Windows):

```bash
py -3.9 -m pip install numpy==1.26.4
py -3.9 -m pip install pygame==2.6.1
py -3.9 -m pip install gym==0.26.2
```

### Running the Simulation

To run the random walk simulation:
```bash
py -3.9 random_walk.py
```

![Sim GIF](https://github.com/bbartling/flappy-heat-pump/blob/develop/images/random_walk.gif)

* Each red dot represents the bot turning on the heat in the 5 zone heat pump HVAC system. If the zone turns green this means the heat pump is up to a proper zone air temperature setpoint.

### Future Work

- Implement Q-learning to train the agent.
- Improve the reward function for better energy efficiency and comfort management.
- Incorporate with a real physics energy simulation tool or engine to be more life like as possible instead of made up calculations or a `Flappy` looking sim.