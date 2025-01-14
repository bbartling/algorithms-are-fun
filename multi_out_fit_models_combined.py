from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
import joblib
import json


# Directory for saving models
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(r"C:\\Users\\ben\\OneDrive\\Documents\\MMB_Master.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df[(df["timestamp"].dt.year > 2024) | ((df["timestamp"].dt.year == 2024) & (df["timestamp"].dt.month >= 4))]

# Remove any characters within parentheses, including the parentheses
df.columns = df.columns.str.replace(r"\s*\([^)]*\)", "", regex=True)

# Strip any leading or trailing whitespace
df.columns = df.columns.str.strip()

# Print cleaned column names for verification
print("Cleaned Column Names:")
print(df.columns)


for col in df.columns:
    print()
    print(col)
    print(df[col].describe())
    print()

# Define target and feature variables
targets = [
    "AHU2_DAT", "AHU1_DAT", "AHU4_DAT", "AHU3_DAT",

    "AV1_7_SpaceTemp", "AV2_7_SpaceTemp", "AV2_15_SpaceTemp",
    "AV1_48_SpaceTemp", "AV3_6_SpaceTemp", "AV3_28B_SpaceTemp",
    "AV4_6_SpaceTemp", "AV4_17_SpaceTemp",

    "Active_Power_Total"
]

feature_columns = [col for col in df.columns if col not in targets + ["timestamp"]]
X = df[feature_columns].fillna(0).values
y = df[targets].fillna(0).values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define models and hyperparameters
models = {
    "extra_trees": {
        "model": Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", ExtraTreesRegressor(random_state=42)),
        ]),
        "params": {
            "regressor__n_estimators": [100, 200, 300],
            "regressor__max_depth": [5, 10, 25, 50],
            "regressor__min_samples_split": [5, 10, 25, 50],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    },
    "random_forest": {
        "model": Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", RandomForestRegressor(random_state=42)),
        ]),
        "params": {
            "regressor__n_estimators": [100, 200, 300],
            "regressor__max_depth": [5, 10, 25, 50],
            "regressor__min_samples_split": [5, 10, 25, 50],
            "regressor__min_samples_leaf": [1, 2, 5],
        },
    }
}

# Save feature column names and descriptions
metadata = {
    "features": feature_columns,
    "targets": targets,
    "feature_descriptions": df[feature_columns].describe().to_dict(),
    "target_descriptions": df[targets].describe().to_dict(),
}
with open(os.path.join(model_dir, "model_metadata.json"), "w") as f:
    json.dump(metadata, f, indent=4)
print(f"Saved model metadata to {os.path.join(model_dir, 'model_metadata.json')}")


# Dictionary to store results
results = {}

# Train and evaluate models
for model_name, model_info in models.items():
    print(f"\nFitting {model_name.title()}...")
    grid_search = RandomizedSearchCV(
        model_info["model"],
        model_info["params"],
        scoring="neg_mean_squared_error",
        cv=3,
        verbose=1,
        n_iter=10,
        random_state=42,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    # Evaluate
    best_model = grid_search.best_estimator_
    predictions = best_model.predict(X_test)
    mse = mean_squared_error(y_test, predictions, multioutput="uniform_average")

    print(f"{model_name.title()} - Best Parameters: {grid_search.best_params_}")
    print(f"{model_name.title()} - Mean Squared Error: {mse:.4f}")

    # Save the best model
    model_path = os.path.join(model_dir, f"{model_name}_best_model.pkl")
    joblib.dump(best_model, model_path)
    print(f"Saved {model_name} model to {model_path}")

    # Save results
    results[model_name] = {
        "best_params": grid_search.best_params_,
        "mean_squared_error": mse,
        "model_path": model_path,
    }

# Save results to a JSON file
results_path = os.path.join(model_dir, "model_results.json")
with open(results_path, "w") as f:
    json.dump(results, f, indent=4)
print(f"Saved model results to {results_path}")
