import matplotlib.pyplot as plt
import joblib
import json
import numpy as np
import pandas as pd

# Load the model
model_path = "models/random_forest_best_model.pkl"  # Replace with your model's path
model = joblib.load(model_path)

# Load metadata
metadata_path = "models/model_metadata.json"
with open(metadata_path, "r") as f:
    metadata = json.load(f)

features = metadata["features"]
targets = metadata["targets"]
feature_descriptions = metadata["feature_descriptions"]
target_descriptions = metadata["target_descriptions"]

# Generate synthetic input data
def generate_synthetic_data(n_samples=10):
    synthetic_data = {}
    for feature, stats in feature_descriptions.items():
        mean = stats["mean"]
        std = stats["std"]
        synthetic_data[feature] = np.random.normal(mean, std, n_samples)
    return pd.DataFrame(synthetic_data)

# Create synthetic data
synthetic_df = generate_synthetic_data()
print("Synthetic Input Data:")
print(synthetic_df)

# Make predictions
predictions = model.predict(synthetic_df.values)
predicted_df = pd.DataFrame(predictions, columns=targets)
print("\nPredicted Output Data:")
print(predicted_df)

# Example: Modify a feature and observe changes
synthetic_df["example_feature"] = synthetic_df["example_feature"] + 10  # Adjust a feature
adjusted_predictions = model.predict(synthetic_df.values)
adjusted_df = pd.DataFrame(adjusted_predictions, columns=targets)
print("\nAdjusted Predicted Output Data:")
print(adjusted_df)



# Example: Visualize the change in a specific target
plt.figure(figsize=(10, 6))
plt.plot(predicted_df["AHU2_DAT"], label="Original")
plt.plot(adjusted_df["AHU2_DAT"], label="Adjusted")
plt.title("Effect of Feature Adjustment on AHU2_DAT")
plt.xlabel("Sample Index")
plt.ylabel("Predicted Value")
plt.legend()
plt.show()
