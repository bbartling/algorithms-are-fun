import argparse
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pandas as pd
import time
import os
import joblib
import json

"""
python .\fit_models_combined.py --model extra_trees --dummies

"""

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Fit models and save the best one.")
parser.add_argument(
    "--model",
    type=str,
    choices=[
        "random_forest",
        "extra_trees",
        "decision_tree",
        "k_neighbors",
        "adaboost",
        "gradient_boosting",
    ],
    help="Specify a model to train (e.g., random_forest, extra_trees, xgboost). If not provided, all models are trained.",
)
parser.add_argument(
    "--dummies",
    action="store_true",
    help="Add dummy variables for weekday and hour to the dataset.",
)
args = parser.parse_args()

# Directory for saving models
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(r"C:\\Users\\ben\\OneDrive\\Documents\\MMB_Master.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Preprocess data
#df = df[df["timestamp"].dt.year >= 2024]
# Filter data to keep only rows from April 2024 onward
df = df[(df["timestamp"].dt.year > 2024) | ((df["timestamp"].dt.year == 2024) & (df["timestamp"].dt.month >= 4))]
df = df[df["AV4_17_SpaceTemp"] != 0]
df = df[df["Apparent_Power_Total"] != 0]

print("Original df colummns")
for col in df.columns:
    print(col)
print()

# Handle future test data
future_test_date = "2024-08-02"
future_test_data = df[df["timestamp"].dt.date == pd.to_datetime(future_test_date).date()]

# Define the columns to keep
columns_to_keep = [
    "timestamp",
    "AHU1_CW_ValveAO (%)", "AHU1_MA_RA_DamperAO (%)", "AHU1_MATemp (°F)",
    "AHU1_RATemp_value (°F)", "AHU1_SaFanSpeedAO_value (%)", "AHU2_CW_ValveAO (%)",
    "AHU2_MA_RA_DamperAO (%)", "AHU2_MATemp (°F)",  "AHU2_RATemp_value (°F)",
    "AHU2_SaFanSpeedAO_value (%)", "AHU3_CW_ValveAO (%)", "AHU3_MA_RA_DamperAO (%)",
    "AHU3_MATemp (°F)", "AHU3_SaFanSpeedAO_value (%)",
    "AHU4_CW_ValveAO (%)", "AHU4_MA_RA_DamperAO (%)", "AHU4_MATemp (°F)", 
    "AHU4_RATemp_value (°F)", "AHU4_SaFanSpeedAO_value (%)", 

    "AHU2_DAT (°F)",
    "AHU1_DAT (°F)",
    "AHU4_DAT (°F)",
    "AHU3_DAT (°F)",
    
    "Boiler2_FireRate_value (%)",
    "Boiler1_FireRate_value (%)", "Boiler_Flow_value (gal/min)", "Boiler1_HWS_value (°F)",
    "Boiler_HWR_value (°F)", 
    
    "Active_Power_Total", 

    "Chiller_RtnTemp_value (°F)",
    "Chiller_CompStages_value", "Chiller_CWS_Temp_value (°F)",
    "Chiller_DP_value (Δpsi)", "Chiller_Flow_value (gal/min)", "Chiller_BypassValve_value (%)",

    "AV1_7_SpaceTemp", 
    "AV2_7_SpaceTemp", 
    "AV2_15_SpaceTemp", 
    "AV1_48_SpaceTemp", 
    "AV3_6_SpaceTemp", 
    "AV3_28B_SpaceTemp",
    "AV4_6_SpaceTemp",
    "AV4_17_SpaceTemp", 

    "AV1_7_Co2",
    "AV1_48_Co2",
    "AV4_6_Co2",
    "AV4_17_Co2"
]

# Retain only the specified columns
df = df.loc[:, columns_to_keep]

print("Cleaned df colummns")
for col in df.columns:
    print(col)
print()

print()
print("Check time stamps: ")
print(df.head())
print(df.tail())
print()

if args.dummies:
    # Add weekday and hour dummy variables for future test data
    future_test_data["weekday"] = future_test_data["timestamp"].dt.dayofweek
    weekday_dummies_future = pd.get_dummies(future_test_data["weekday"], prefix="weekday", drop_first=True)
    future_test_data = pd.concat([future_test_data, weekday_dummies_future], axis=1)

    future_test_data["hour"] = future_test_data["timestamp"].dt.hour
    hour_dummies_future = pd.get_dummies(future_test_data["hour"], prefix="hour", drop_first=True)
    future_test_data = pd.concat([future_test_data, hour_dummies_future], axis=1)

    future_test_data = future_test_data.drop(columns=["weekday", "hour"])

    future_test_filename = os.path.join(model_dir, "future_test_data.csv")
    future_test_data.to_csv(future_test_filename, index=False)
    print(f"Saved future test data with dummies to file: {future_test_filename}")

# Exclude August 3, 2024, from the training dataset
df = df[df["timestamp"].dt.date != pd.to_datetime(future_test_date).date()]

if args.dummies:
    # Add weekday and hour dummy variables for main dataset
    df["weekday"] = df["timestamp"].dt.dayofweek
    weekday_dummies = pd.get_dummies(df["weekday"], prefix="weekday", drop_first=True)
    df = pd.concat([df, weekday_dummies], axis=1)

    df["hour"] = df["timestamp"].dt.hour
    hour_dummies = pd.get_dummies(df["hour"], prefix="hour", drop_first=True)
    df = pd.concat([df, hour_dummies], axis=1)

    df = df.drop(columns=["weekday", "hour"])

# Drop unused columns
columns_to_drop = [
    "timestamp",
]
df = df.drop(columns=columns_to_drop).reset_index(drop=True)

# Save processed dataset describe
describe_filename = os.path.join(model_dir, "df_describe.json")
describe = df.describe().to_dict()
with open(describe_filename, "w") as f:
    json.dump(describe, f, indent=4)
print(f"Saved df.describe() to file: {describe_filename}")

# Features and target (single target: 'CurrentKW')
targets = ["Active_Power_Total"]
features = [col for col in df.columns if col not in targets]

for feature in features:
    print(f"feature: {feature}")
    print(f"describe: {df[feature].describe()}")
    print()

X = df[features].fillna(0).values
y = df[targets[0]].fillna(0).values  # Fixed: Access as a Series or flatten the array

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True, random_state=42
)

# Define models and hyperparameter grids
models = {
    "extra_trees": {
        "model": ExtraTreesRegressor(random_state=42),
        "params": {
            "regressor__n_estimators": [100, 200, 300],
            "regressor__max_depth": [5, 10, 25, 50],
            "regressor__min_samples_split": [2, 5, 10],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
    "decision_tree": {
        "model": DecisionTreeRegressor(random_state=42),
        "params": {
            "regressor__max_depth": [10, 20, 50],
            "regressor__min_samples_split": [2, 5, 10],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
    "k_neighbors": {
        "model": KNeighborsRegressor(),
        "params": {
            "regressor__n_neighbors": [5, 10, 15],
            "regressor__weights": ["uniform", "distance"],
            "regressor__leaf_size": [10, 20],
        },
    },
    "random_forest": {
        "model": RandomForestRegressor(random_state=42),
        "params": {
            "regressor__n_estimators": [100, 200, 300],
            "regressor__max_depth": [10, 20, 50],
            "regressor__min_samples_split": [2, 5, 10],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
    "adaboost": {
        "model": AdaBoostRegressor(random_state=42),
        "params": {
            "regressor__n_estimators": [50, 100, 200],
            "regressor__learning_rate": [0.01, 0.1, 1.0],
            "regressor__loss": ["linear", "square", "exponential"],
        },
    },
    "gradient_boosting": {
        "model": GradientBoostingRegressor(random_state=42),
        "params": {
            "regressor__n_estimators": [100, 200, 300],
            "regressor__learning_rate": [0.01, 0.1, 0.2],
            "regressor__max_depth": [3, 5, 10],
            "regressor__min_samples_split": [2, 5, 10],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
}


# Filter models if a specific model is specified
if args.model:
    models = {args.model: models[args.model]}

results = {}
for model_name, model_info in models.items():
    print(f"\nFitting {model_name.replace('_', ' ').title()}...")
    start_time = time.time()

    pipeline = Pipeline(
        [("scaler", StandardScaler()), ("regressor", model_info["model"])]
    )

    n_iter = min(50, len(model_info["params"]))
    grid_search = RandomizedSearchCV(
        pipeline,
        model_info["params"],
        scoring="neg_mean_squared_error",
        cv=3,
        verbose=1,
        n_iter=n_iter,
        random_state=42,
        n_jobs=-1,
    )
    grid_search.fit(X_train, y_train)

    elapsed_time = time.time() - start_time
    best_model = grid_search.best_estimator_

    # Save the best model
    model_filename = os.path.join(model_dir, f"{model_name}_best_model.pkl")
    joblib.dump(best_model, model_filename)

    # Evaluate the model (single target case)
    predictions = best_model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)

    # Save the results as a text file
    results_filename = os.path.join(model_dir, f"{model_name}_results.txt")
    with open(results_filename, "w") as f:
        f.write(f"Model: {model_name.replace('_', ' ').title()}\n")
        f.write(f"Total Fit Time: {elapsed_time:.2f} seconds\n")
        f.write(f"Best Parameters:\n")
        for param, value in grid_search.best_params_.items():
            f.write(f"  {param}: {value}\n")
        f.write(f"\nMean Squared Error: {mse:.4f}\n")

    # Save the results as a JSON file
    json_filename = os.path.join(model_dir, f"{model_name}_results.json")
    with open(json_filename, "w") as f:
        json.dump(
            {
                "best_params": grid_search.best_params_,
                "time": elapsed_time,
                "mse": mse,
            },
            f,
            indent=4,
        )

    print(
        f"Saved {model_name.replace('_', ' ').title()}",
        f"best model to file: {model_filename}"
    )
    print(
        f"Saved {model_name.replace('_', ' ').title()}",
        f"results to files: {results_filename} and {json_filename}"
    )

    # Print the evaluation metrics
    print(f"{model_name.replace('_', ' ').title()} Best Parameters: {grid_search.best_params_}")
    print(f"{model_name.replace('_', ' ').title()} Fit Time: {elapsed_time:.2f} seconds")
    print(f"Mean Squared Error: {mse:.4f}")

