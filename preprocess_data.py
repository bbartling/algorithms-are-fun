import pandas as pd

# Load the dataset (replace with your file path)
file_path = r"C:\Users\bbartling\Slipstream\Connected Communities Team Collaboration-EXT - Documents\1. Municipal Demonstration\1.6 Pre-Retrofit Monitoring\Data\BAS\WPCRC_Master.csv"
data = pd.read_csv(file_path)

# Convert timestamp to datetime
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Add Sa_FanSpeed to the relevant columns
relevant_columns = [
    'timestamp', 'HWR_value', 'HWS_value', 'CWR_Temp', 'CWS_Temp', 'CW_Valve',
    'Oa_Temp', 'MA_Temp', 'SpaceTemp', 'VAV2_6_SpaceTemp', 'VAV2_7_SpaceTemp',
    'VAV3_2_SpaceTemp', 'VAV3_5_SpaceTemp', 'EffSetpoint', 'CurrentKW', 'Sa_FanSpeed'
]

# Extract relevant data
processed_data = data[relevant_columns]

# Handle missing values by forward filling
processed_data = processed_data.ffill()

# Save preprocessed data
processed_data.to_csv('processed_ahu_data.csv', index=False)
print("Preprocessing complete. Data saved as 'processed_ahu_data.csv'.")
