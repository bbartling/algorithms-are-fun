import argparse
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
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
    choices=["random_forest", "extra_trees", "decision_tree", "k_neighbors"],
    help="Specify a model to train (e.g., random_forest, extra_trees). If not provided, all models are trained.",
)
args = parser.parse_args()

# Define directory for saving models
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(r"C:\Users\ben\OneDrive\Documents\WPCRC_Master.csv")

# Preprocess data
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df[df["timestamp"].dt.year >= 2024]
df = df.drop(columns=["timestamp"]).reset_index(drop=True)

df["Avg_SpaceTemp"] = df[
    [
        "SpaceTemp",
        "VAV2_6_SpaceTemp",
        "VAV2_7_SpaceTemp",
        "VAV3_2_SpaceTemp",
        "VAV3_5_SpaceTemp",
    ]
].mean(axis=1)
df = df.drop(
    columns=[
        "SpaceTemp",
        "VAV2_6_SpaceTemp",
        "VAV2_7_SpaceTemp",
        "VAV3_2_SpaceTemp",
        "VAV3_5_SpaceTemp",
    ]
)

targets = ["CurrentKW", "Avg_SpaceTemp", "DischargeTemp"]
features = [col for col in df.columns if col not in targets]

X = df[features].fillna(0).values
y = df[targets].fillna(0).values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define models and hyperparameter grids
models = {
    "extra_trees": {
        "model": ExtraTreesRegressor(random_state=42),
        "params": {
            "regressor__n_estimators": [50, 100, 200],
            "regressor__max_depth": [5, 10, 20, None],
            "regressor__min_samples_split": [2, 5, 10],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
    "decision_tree": {
        "model": DecisionTreeRegressor(random_state=42),
        "params": {
            "regressor__max_depth": [5, 10, 20, None],
            "regressor__min_samples_split": [2, 5, 10],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
    "k_neighbors": {
        "model": KNeighborsRegressor(),
        "params": {
            "regressor__n_neighbors": [5, 10, 15, 20, 30, 50, 75],
            "regressor__weights": ["uniform", "distance"],
            "regressor__p": [1, 2, 3],
            "regressor__algorithm": ["auto", "ball_tree", "kd_tree", "brute"],
            "regressor__leaf_size": [10, 20, 30, 40, 50],
        },
    },
    "random_forest": {
        "model": RandomForestRegressor(random_state=42),
        "params": {
            "regressor__n_estimators": [50, 100, 200],
            "regressor__max_depth": [5, 10, 20, None],
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

    grid_search = GridSearchCV(
        pipeline,
        model_info["params"],
        scoring="neg_mean_squared_error",
        cv=3,
        verbose=1,
    )
    grid_search.fit(X_train, y_train)

    elapsed_time = time.time() - start_time
    best_model = grid_search.best_estimator_

    # Evaluate the model
    predictions = best_model.predict(X_test)
    mse = {
        targets[i]: mean_squared_error(y_test[:, i], predictions[:, i])
        for i in range(len(targets))
    }

    # Save the best model
    model_filename = os.path.join(model_dir, f"{model_name}_best_model.pkl")
    joblib.dump(best_model, model_filename)

    # Save the results as a text file
    results_filename = os.path.join(model_dir, f"{model_name}_results.txt")
    with open(results_filename, "w") as f:
        f.write(f"Model: {model_name.replace('_', ' ').title()}\n")
        f.write(f"Total Fit Time: {elapsed_time:.2f} seconds\n")
        f.write(f"Best Parameters:\n")
        for param, value in grid_search.best_params_.items():
            f.write(f"  {param}: {value}\n")
        f.write(f"\nMean Squared Error for Each Target:\n")
        for target, target_mse in mse.items():
            f.write(f"  {target}: {target_mse:.4f}\n")

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
        f"Saved {model_name.replace('_', ' ').title()} best model to file: {model_filename}"
    )
    print(
        f"Saved {model_name.replace('_', ' ').title()} results to files: {results_filename} and {json_filename}"
    )

    # Print the evaluation metrics
    print(
        f"{model_name.replace('_', ' ').title()} - Best Parameters: {grid_search.best_params_}"
    )
    print(
        f"{model_name.replace('_', ' ').title()} - Fit Time: {elapsed_time:.2f} seconds"
    )
    for target, target_mse in mse.items():
        print(f"  {target} - Mean Squared Error: {target_mse:.4f}")
