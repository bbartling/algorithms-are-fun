import argparse
from catboost import CatBoostRegressor
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
        "catboost",
    ],
    help="Specify a model to train (e.g., random_forest, catboost, xgboost). If not provided, all models are trained.",
)
args = parser.parse_args()

# Define hour blocks
def categorize_hour(hour):
    if 4 <= hour < 8:
        return '4AM-8AM'
    elif 8 <= hour < 12:
        return '8AM-Noon'
    elif 12 <= hour < 16:
        return 'Noon-4PM'
    elif 16 <= hour < 20:
        return '4PM-8PM'
    else:
        return None


# Define directory for saving models
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(r"C:\\Users\\ben\\OneDrive\\Documents\\WPCRC_Master.csv")

# Preprocess data
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df[df["timestamp"].dt.year >= 2024]

# Remove rows where VAV2_7_SpaceTemp is zero
df = df[df["VAV2_7_SpaceTemp"] != 0]

# Remove data for August 3, 2024, and save for future testing
future_test_date = "2024-08-03"
future_test_data = df[df["timestamp"].dt.date == pd.to_datetime(future_test_date).date()]

# Extract day of the week for future test data (Monday=0, ..., Sunday=6)
future_test_data.loc[:, 'weekday'] = future_test_data['timestamp'].dt.dayofweek

# Add weekday dummy variables (exclude Sunday, which is weekday_6)
weekday_dummies_future = pd.get_dummies(future_test_data['weekday'], prefix='weekday', drop_first=True)  # Excludes Sunday
future_test_data = pd.concat([future_test_data, weekday_dummies_future], axis=1)

# Extract hour of the day for future test data
future_test_data.loc[:, 'hour'] = future_test_data['timestamp'].dt.hour

# Add hour dummy variables (exclude the first hour, e.g., 'hour_0')
hour_dummies_future = pd.get_dummies(future_test_data['hour'], prefix='hour', drop_first=True)  # Excludes midnight
future_test_data = pd.concat([future_test_data, hour_dummies_future], axis=1)

# Drop temporary columns
future_test_data = future_test_data.drop(columns=['weekday', 'hour'])

# Save the processed future test data
future_test_filename = os.path.join(model_dir, "future_test_data.csv")
future_test_data.to_csv(future_test_filename, index=False)
print(f"Saved future test data to file: {future_test_filename}")

# For the main dataset, do the same processing
df['weekday'] = df['timestamp'].dt.dayofweek

# Add weekday dummy variables (exclude Sunday, which is weekday_6)
weekday_dummies = pd.get_dummies(df['weekday'], prefix='weekday', drop_first=True)  # Excludes Sunday
df = pd.concat([df, weekday_dummies], axis=1)

# Extract hour of the day
df['hour'] = df['timestamp'].dt.hour

# Add hour dummy variables (exclude the first hour, e.g., 'hour_0')
hour_dummies = pd.get_dummies(df['hour'], prefix='hour', drop_first=True)  # Excludes midnight
df = pd.concat([df, hour_dummies], axis=1)

# Drop temporary columns
df = df.drop(columns=['weekday', 'hour'])


# Exclude August 3, 2024, from the training dataset
df = df[df["timestamp"].dt.date != pd.to_datetime(future_test_date).date()]

# Correctly drop columns
columns_to_drop = [
    "timestamp", 
    "CWS_Freeze_SPt", 
    "Eff_DaSPt", 
    "EffSetpoint", 
    "SaTempSPt", 
    "CurrentKWHrs"
]
df = df.drop(columns=columns_to_drop).reset_index(drop=True)

print(df.columns)
describe = df.describe()

print(df.head())

# Save df.describe() to a JSON file
describe_filename = os.path.join(model_dir, "df_describe.json")
df_describe_dict = describe.to_dict()
with open(describe_filename, "w") as f:
    json.dump(df_describe_dict, f, indent=4)
print(f"Saved df.describe() to file: {describe_filename}")


# Features and target (single target: 'CurrentKW')
targets = ["CurrentKW"]
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
    "catboost": {
        "model": CatBoostRegressor(verbose=0, random_state=42),
        "params": {
            "regressor__iterations": [100, 200, 500],
            "regressor__learning_rate": [0.01, 0.1, 0.2],
            "regressor__depth": [4, 6, 8],
        },
    },
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

