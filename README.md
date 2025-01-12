# hvac-ml-dataset-fun

This is a hobby project focused on analyzing a historical dataset from a medium-sized office HVAC system. The goal is to explore fitting machine learning models for fun while studying electrical load-shifting strategies and potentially delving into reinforcement learning.

**⚠️👷🚧🏗️ WARNING** - This is a highly experimental hobby project!

# Model Fitting and Evaluation for Time-Series Dataset

This document describes the process of training and evaluating several regression models using Scikit-Learn on a time-series dataset. The dataset includes the following features:

### Dataset Features (Excerpt from `df.describe()`)
| Feature Name         | Count   | Mean   | Std Dev | Min   | 25%   | 50%   | 75%   | Max    |
|----------------------|---------|--------|---------|-------|-------|-------|-------|--------|
| `HWR_value`          | 84750   | 98.68  | 30.35   | 62.55 | 73.56 | 83.44 | 126.36| 178.16 |
| `CWS_Temp`           | 84750   | 57.19  | 11.03   | 0.00  | 47.14 | 56.40 | 66.83 | 91.04  |
| `Ra_Temp`            | 84750   | 69.52  | 2.81    | 0.00  | 67.93 | 69.08 | 70.74 | 83.60  |
| `EaDamper`           | 84750   | 14.65  | 18.94   | 0.00  | 0.00  | 10.00 | 20.00 | 100.00 |
| `VAV2_6_SpaceTemp`   | 84750   | 69.61  | 2.77    | 0.00  | 67.69 | 70.60 | 71.72 | 75.06  |

**Note**: The full dataset contains 38 features and approximately 84,750 rows.

---

## Training and Evaluation Process

1. **Data Preprocessing**:
   - The dataset was filtered to include only data from 2024.
   - Unnecessary HVAC setpoint columns (`timestamp`, `CWS_Freeze_SPt`, `Eff_DaSPt`, `EffSetpoint`, `SaTempSPt`, `CurrentKWHrs`) were dropped.
   - A specific date (`2024-08-03`) was removed for future testing and saved as a separate file.

2. **Models and Hyperparameter Tuning**:
   The following models were trained using a randomized grid search with 3-fold cross-validation:
   - **Cat Boost** 
   - **Extra Trees**
   - **Decision Tree**
   - **K-Neighbors**
   - **Random Forest**
   - **AdaBoost**
   - **Gradient Boosting**

3. **Metrics**:
   The performance of each model was evaluated using Mean Squared Error (MSE) on the test set. Best-fit parameters and MSE values were recorded for each model.

4. **Model Saving**:
   - The best-fit model for each type was saved as a `.pkl` file.
   - Results were saved as `.txt` and `.json` files for each model.



### BAS Points Summary
One year of data from a medium-sized office building in the Upper Midwest, featuring a VAV AHU system with hot water reheat and an air-cooled chiller.

- **HWR_value (Hot Water Return Temperature)**  
  Temperature of the water returning from the heating loop.  
  Min: 62.55°F, Max: 178.16°F

- **HWS_value (Hot Water Supply Temperature)**  
  Temperature of the water supplied to the heating loop.  
  Min: 61.67°F, Max: 180.31°F

- **Heat_Calls**  
  Number of calls for heat in the system.  
  Min: 0, Max: 15

- **Oa_Temp (Outside Air Temperature)**  
  Temperature of the air outside the building.  
  Min: -21.2°F, Max: 101.51°F

- **OaTemp_Enable (Outside Air Enable Temperature)**  
  Setpoint for enabling the outside air system.  
  Min: 0°F, Max: 75°F

- **CWR_Temp (Chilled Water Return Temperature)**  
  Temperature of the water returning from the cooling loop.  
  Min: 0°F, Max: 92.1°F

- **CWS_Temp (Chilled Water Supply Temperature)**  
  Temperature of the water supplied to the cooling loop.  
  Min: 0°F, Max: 91.04°F

- **CW_Valve (Chilled Water Valve Position)**  
  Percentage of the chilled water valve opening.  
  Min: 0%, Max: 100%

- **HW_Valve (Hot Water Valve Position)**  
  Percentage of the hot water valve opening.  
  Min: 0%, Max: 100%

- **DischargeTemp (Discharge Air Temperature)**  
  Temperature of the air discharged from the HVAC system.  
  Min: 0°F, Max: 95.8°F

- **Eff_DaSP (Effective Discharge Air Setpoint)**  
  Effective setpoint for discharge air temperature.  
  Min: 0°F, Max: 63°F

- **RaHumidity (Return Air Humidity)**  
  Relative humidity of the air returning to the HVAC system.  
  Min: 0%, Max: 89.31%

- **Ra_Temp (Return Air Temperature)**  
  Temperature of the air returning to the HVAC system.  
  Min: 0°F, Max: 81.82°F

- **Ra_FanSpeed (Return Air Fan Speed)**  
  Speed of the return air fan as a percentage.  
  Min: 0%, Max: 86%

- **OaTemp (Outside Air Temperature)**  
  Temperature of the air outside the building (redundant reading).  
  Min: -21.2°F, Max: 101.5°F

- **Ma_Dampers (Mixing Air Dampers Position)**  
  Position of the dampers that mix outside and return air.  
  Min: 0%, Max: 100%

- **Ma_Temp (Mixing Air Temperature)**  
  Temperature of the air after mixing outside and return air.  
  Min: 0°F, Max: 80.38°F

- **SaStaticSPt (Supply Air Static Pressure Setpoint)**  
  Setpoint for supply air static pressure.  
  Min: 0 in. w.g., Max: 0.9 in. w.g.

- **Sa_FanSpeed (Supply Air Fan Speed)**  
  Speed of the supply air fan as a percentage.  
  Min: 0%, Max: 100%

- **SaTempSP (Supply Air Temperature Setpoint)**  
  Setpoint for supply air temperature.  
  Min: 0°F, Max: 70°F

- **RaCO2 (Return Air CO₂ Level)**  
  Concentration of CO₂ in return air (ppm).  
  Min: 0 ppm, Max: 1336.9 ppm

- **SaStatic (Supply Air Static Pressure)**  
  Measured static pressure of supply air.  
  Min: -0.04 in. w.g., Max: 1.02 in. w.g.

- **CurrentKW (Current Power Consumption)**  
  Power consumption of the system (kW).  
  Min: 0 kW, Max: 242.76 kW

- **RaTemp (Return Air Temperature)**  
  Temperature of return air (redundant reading).  
  Min: 0°F, Max: 79.77°F

- **MaLowSPt (Mixing Air Low Setpoint)**  
  Low setpoint for mixing air temperature.  
  Min: 0°F, Max: 63°F

- **MaDampers (Mixing Air Dampers Position)**  
  Position of mixing air dampers (redundant reading).  
  Min: 0%, Max: 50%

- **SaStatic_SPt (Supply Air Static Pressure Setpoint)**  
  Setpoint for supply air static pressure (redundant reading).  
  Min: 0 in. w.g., Max: 0.9 in. w.g.

- **CoolValve (Cooling Valve Position)**  
  Position of the cooling valve.  
  Min: 0%, Max: 100%

- **OA_Damper (Outside Air Damper Position)**  
  Position of the damper controlling outside air.  
  Min: 0%, Max: 100%

- **MA_Temp (Mixed Air Temperature)**  
  Temperature of mixed air (redundant reading).  
  Min: 0°F, Max: 82.57°F

- **EaDamper (Exhaust Air Damper Position)**  
  Position of the exhaust air damper.  
  Min: 0%, Max: 100%

- **SpaceTemp (Space Temperature)**  
  Temperature within the conditioned space.  
  Min: 0°F, Max: 75.63°F

- **RA_CO2 (Return Air CO₂ Level)**  
  Concentration of CO₂ in return air (redundant reading).  
  Min: 0 ppm, Max: 1264.31 ppm

- **RA_Temp (Return Air Temperature)**  
  Temperature of return air (redundant reading).  
  Min: 0°F, Max: 83.6°F

- **VAV2_6_SpaceTemp (Zone 2-6 Space Temperature)**  
  Space temperature for zone 2-6.  
  Min: 0°F, Max: 75.06°F

- **VAV2_7_SpaceTemp (Zone 2-7 Space Temperature)**  
  Space temperature for zone 2-7.  
  Min: 0°F, Max: 75.87°F

- **VAV3_2_SpaceTemp (Zone 3-2 Space Temperature)**  
  Space temperature for zone 3-2.  
  Min: 0°F, Max: 81.05°F

- **VAV3_5_SpaceTemp (Zone 3-5 Space Temperature)**  
  Space temperature for zone 3-5.  
  Min: 0°F, Max: 76.79°F


