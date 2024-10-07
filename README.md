This is a fun hobby project inspired by Flappy Bird, aimed at experimenting with reinforcement learning (RL) to develop strategies for managing electrical power in heat pump HVAC systems.

In reality, there's a geothermal-based school in Wisconsin that faces significant challenges in managing electrical demand (kW), especially during the frigid winter months of January. Building operators try to stagger equipment startups in the mornings before school, but it’s a complex problem. How early should the equipment be staggered, and for how long? How many heat pumps can be run simultaneously to warm the building without triggering peak demand? Could RL help solve this? What kind of reward system could be designed to minimize electrical demand spikes, reduce total energy consumption (kWh), and ensure all zones are sufficiently warm for school to start on time?

This project explores how Reinforcement Learning (RL) can be used to manage electrical power demand in heat pump HVAC systems by optimizing equipment staggering, all through a simplified simulation.

If RL can master Flappy Bird using simplified, made-up calculations that certainly don’t follow Newton’s law of gravitation, yet still produce a convincing, life-like mimic of reality, could it also learn to stagger HVAC equipment in a similar way?

While the simulation might not precisely follow the heat transfer formula Q = c × m × ΔT, could RL still optimize equipment operation using a simulation that mimics real-life electrical load profiles and historical data? Just as Flappy Bird "feels" right despite its abstract physics, could RL successfully manage electrical demand without perfectly following the rules of thermodynamics, by leveraging historical trends and load patterns to make effective decisions?

This project explores exactly that — using RL to experiment with building electrical power management in a heat pump HVAC system through an intentionally simplified yet practical simulation.

**⚠️👷🚧🏗️ WARNING** - This project is new and highly experimental! It may take some time to get something actually working...


## Getting Setup in Python
```bash
pip install gym pygame numpy
```

![Sim GIF](https://github.com/bbartling/flappy-hvac/blob/develop/images/video.gif)