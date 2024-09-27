# flappy-hvac
This is silly hobby project for experimenting with building electrical power management strategies through games and potentially something fun to try with reinforcement learning.

**⚠️👷🚧🏗️ WARNING** - This project is new and highly experimental! It may take some time to get something actually working...


This is a simple heat pump HVAC system simulation using `pygame`. The simulation manages multiple zones (rooms), each with its own heating needs, based on global outside air temperature.

## Features

- Simulates heat loss and heating power in 15 zones, organized in a 3x5 grid.
- Visual representation of room temperatures, heating status, and power consumption.
- Tracks total energy consumption and combined power usage over time.
- Allows switching between:
  - Random Walk mode: Zones randomly toggle heating.
  - Q-Learning mode: Reinforcement learning using a Q-learning agent to control the heating system.

## Installation

To run the simulation, make sure you have Python installed along with the required libraries:

```bash
pip install pygame numpy
```

### Human Game Play Mode:

```bash
python human_flappy_heat_pump.py
```

## Running the bot Simulation

You can run the simulation in two modes to let the bot play the game that has an arg for number of episodes the bot will play the game.

### Normal (Random Walk) Mode with the default of 10 episodes the episode arg is not passed:

```bash
python bot_flappy_heat_pump.py
```

### Q-Learning Mode with 100 episodes:

```bash
python flappy_heat_pump.py q_learning 100

```

In this mode, the Q-learning agent will attempt to optimize the heating in the zones.

## Controls

- Click on any zone to manually toggle its heating system on or off.

## Visualization

The simulation includes real-time visualization of room temperatures, energy usage, and combined power consumption.

- **Blue**: Room temperature is below 65°F.
- **Red**: Room temperature is above 75°F.
- **Green**: Room temperature is within the desired comfort range.

### Additional Information:

- The simulation runs for a set duration (60 seconds by default) at 30 frames per second.
- The heating system in each zone cycles based on the room's temperature and the desired setpoint.
