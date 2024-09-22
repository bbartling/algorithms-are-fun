import random

# Simulated daily load profile in kW for 96 time steps (15-minute intervals for 24 hours)
# Example: HVAC, lighting, etc.
load_profile = [random.randint(20, 60) for _ in range(96)]  # 96 intervals for the day

# Simulated real-time pricing ($/kWh) - higher during peak hours (12 PM to 6 PM)
pricing_profile = [random.uniform(0.1, 0.3) if 12 <= i // 4 < 18 else random.uniform(0.05, 0.15) for i in range(96)]

# Simulated PV array output (kW) - output during daylight hours (6 AM to 6 PM)
pv_output = [random.uniform(0, 20) if 6 <= i // 4 < 18 else 0 for i in range(96)]  # PV output for each 15 min interval

# Simulated battery specs
battery_capacity = 100  # kWh total capacity
battery_charge_limit = 20  # kW maximum charge rate per interval
battery_discharge_limit = 20  # kW maximum discharge rate per interval
battery_current_charge = 50  # kWh current charge level

# Simulated battery efficiency (round-trip efficiency for charge/discharge)
battery_efficiency = 0.9  # 90% efficiency


# Adjust dynamic programming function to optimize battery, PV, and load management
def optimize_load_with_battery_pv(load_profile, pricing_profile, pv_output, battery_capacity, battery_charge_limit,
                                  battery_discharge_limit, battery_current_charge, battery_efficiency):
    # Track battery charge level and cost over time
    battery_charge_level = battery_current_charge
    total_cost = 0
    
    # Iterate over each 15-minute interval (time step)
    for t in range(len(load_profile)):
        # Load demand and PV supply at time t
        load = load_profile[t]
        pv = pv_output[t]
        price = pricing_profile[t]
        
        # Net load after accounting for PV array
        net_load = max(0, load - pv)  # Reduce grid load with PV output
        
        # If price is low, charge the battery (if room available)
        if price < 0.1 and net_load > 0:
            charge_amount = min(battery_charge_limit, battery_capacity - battery_charge_level, net_load)
            battery_charge_level += charge_amount * battery_efficiency
            net_load -= charge_amount
        
        # If price is high, discharge the battery to offset load
        elif price >= 0.1 and battery_charge_level > 0:
            discharge_amount = min(battery_discharge_limit, battery_charge_level, net_load)
            battery_charge_level -= discharge_amount / battery_efficiency
            net_load -= discharge_amount
        
        # Calculate cost for the remaining load (grid-supplied)
        interval_cost = net_load * price
        total_cost += interval_cost
    
    return total_cost


# Example usage for one day
total_cost = optimize_load_with_battery_pv(load_profile, pricing_profile, pv_output, battery_capacity,
                                           battery_charge_limit, battery_discharge_limit, battery_current_charge, battery_efficiency)
print(f"Total electricity cost for the day: ${total_cost:.2f}")


# Optional: Plot the load profile, PV output, and pricing over time to visualize the optimization
import matplotlib.pyplot as plt

time_steps = [i / 4 for i in range(96)]  # Time in hours (each step is 15 minutes)

plt.figure(figsize=(10, 6))

# Plot load profile
plt.plot(time_steps, load_profile, label='Load Profile (kW)', color='blue')

# Plot PV output
plt.plot(time_steps, pv_output, label='PV Output (kW)', color='green')

# Plot pricing profile
plt.plot(time_steps, pricing_profile, label='Electricity Price ($/kWh)', color='red')

plt.title('Daily Load Profile, PV Output, and Electricity Pricing')
plt.xlabel('Time (Hours)')
plt.ylabel('Power (kW) / Price ($/kWh)')
plt.legend()
plt.grid(True)
plt.show()
