This is a fun hobby project inspired by Flappy Bird, aimed at experimenting with reinforcement learning (RL) to develop strategies for managing electrical power in heat pump HVAC systems.

In reality, there's a geothermal-based school in Wisconsin that faces significant challenges in managing electrical demand (kW), especially during the frigid winter months of January. Building operators try to stagger equipment startups in the mornings before school, but it’s a complex problem. How early should the equipment be staggered, and for how long? How many heat pumps can be run simultaneously to warm the building without triggering peak demand? Could RL help solve this? What kind of reward system could be designed to minimize electrical demand spikes, reduce total energy consumption (kWh), and ensure all zones are sufficiently warm for school to start on time?

This project explores how Reinforcement Learning (RL) can be used to manage electrical power demand in heat pump HVAC systems by optimizing equipment staggering, all through a simplified simulation.

If RL can master Flappy Bird using simplified, made-up calculations that certainly don’t follow Newton’s law of gravitation, yet still produce a convincing, life-like mimic of reality, could it also learn to stagger HVAC equipment in a similar way?

While the simulation might not precisely follow the heat transfer formula Q = c × m × ΔT, could RL still optimize equipment operation using a simulation that mimics real-life electrical load profiles and historical data? Just as Flappy Bird "feels" right despite its abstract physics, could RL successfully manage electrical demand without perfectly following the rules of thermodynamics, by leveraging historical trends and load patterns to make effective decisions?

This project explores exactly that — using RL to experiment with building electrical power management in a heat pump HVAC system through an intentionally simplified yet practical simulation.

**⚠️👷🚧🏗️ WARNING** - This project is new and highly experimental! It may take some time to get something actually working...


## Getting Setup in Python


Pip install these 3 packages.
```bash
pip install gym pygame numpy
```
If you run into issues with errors on versions of Numpy I am testing on Windows 10 with Python 3.9.
```python
NumPy version: 1.26.4
Pygame version: 2.6.1
Gym version: 0.26.2
```

You can install specific package version in Windows Powershell.
```bash
py -3.9 -m pip install numpy==1.26.4
py -3.9 -m pip install pygame==2.6.1
py -3.9 -m pip install gym==0.26.2
```

![Sim GIF](https://github.com/bbartling/flappy-hvac/blob/develop/images/video.gif)


## Random Walk

**⚠️👷🚧🏗️ WARNING** - Its not working yet... 😆😂🤣


In this simulation environment, the **action space** is defined as a discrete space where the agent can choose between 5 different actions, each corresponding to toggling the heat for one of the 5 zones. This is represented by `spaces.Discrete(self.num_zones)`, indicating that the agent can only take one action per zone at each time step. 

The **observation space** is designed to reflect the current temperatures of the 5 zones, with each temperature represented as a continuous value. The observation space is defined as `spaces.Box(low=0, high=100, shape=(self.num_zones,), dtype=np.float32)`, meaning that the temperatures can vary between 0 and 100 degrees Fahrenheit, and the environment returns these values as a 5-element vector (one for each zone). This continuous observation space provides the agent with detailed state information about the system's current conditions.

- [ ] Experiment with reward policy and describe in README
- [ ] Experiment with a form of batch learning where the random agent runs for several episodes and store the transitions (state, action, reward, next state)


## Q-learning
TODO

## Deep Q-learing
TODO