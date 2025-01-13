from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
import joblib

# Directory for saving models
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(r"C:\\Users\\ben\\OneDrive\\Documents\\MMB_Master.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df[(df["timestamp"].dt.year > 2024) | ((df["timestamp"].dt.year == 2024) & (df["timestamp"].dt.month >= 4))]

# Define target and feature variables
targets = [
    "AHU2_DAT (°F)", "AHU1_DAT (°F)", "AHU4_DAT (°F)", "AHU3_DAT (°F)",
    "AV1_7_SpaceTemp", "AV2_7_SpaceTemp", "AV2_15_SpaceTemp",
    "AV1_48_SpaceTemp", "AV3_6_SpaceTemp", "AV3_28B_SpaceTemp",
    "AV4_6_SpaceTemp", "AV4_17_SpaceTemp"
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
            ("regressor", MultiOutputRegressor(ExtraTreesRegressor(random_state=42))),
        ]),
        "params": {
            "regressor__estimator__n_estimators": [100, 200, 300],
            "regressor__estimator__max_depth": [5, 10, 25],
            "regressor__estimator__min_samples_split": [2, 5],
            "regressor__estimator__min_samples_leaf": [1, 2],
        },
    },
    "random_forest": {
        "model": Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", MultiOutputRegressor(RandomForestRegressor(random_state=42))),
        ]),
        "params": {
            "regressor__estimator__n_estimators": [100, 200],
            "regressor__estimator__max_depth": [10, 20],
            "regressor__estimator__min_samples_split": [2, 5],
            "regressor__estimator__min_samples_leaf": [1, 2],
        },
    },
    "gradient_boosting": {
        "model": Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", MultiOutputRegressor(GradientBoostingRegressor(random_state=42))),
        ]),
        "params": {
            "regressor__estimator__n_estimators": [100, 200],
            "regressor__estimator__learning_rate": [0.01, 0.1],
            "regressor__estimator__max_depth": [3, 5],
        },
    },
}

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
