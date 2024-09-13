import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

# Load preprocessed data
data = pd.read_csv('processed_ahu_data.csv')

# Calculate the average of the space temperatures
data['Avg_SpaceTemp'] = data[['SpaceTemp', 'VAV2_6_SpaceTemp', 'VAV2_7_SpaceTemp', 'VAV3_2_SpaceTemp', 'VAV3_5_SpaceTemp']].mean(axis=1)

# Define features and target for the models
features = ['Avg_SpaceTemp', 'Oa_Temp', 'Sa_FanSpeed']
target = 'CurrentKW'

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2, random_state=42)

# Initialize models
models = {
    'Ridge': Ridge(alpha=1.0),
    'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
    'AdaBoost': AdaBoostRegressor(n_estimators=100, random_state=42)
}

# Track the best model and its MSE
best_model = None
best_mse = float('inf')

# Train and evaluate each model
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"{name} Model Mean Squared Error: {mse}")
    
    # Update the best model if current model is better
    if mse < best_mse:
        best_mse = mse
        best_model = model
        best_model_name = name

# Save the best model
if best_model:
    joblib.dump(best_model, f'{best_model_name}_best_model.pkl')
    print(f"Best Model: {best_model_name} with MSE: {best_mse} saved as {best_model_name}_best_model.pkl")
