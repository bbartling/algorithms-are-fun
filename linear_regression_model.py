from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd

# Load preprocessed data
data = pd.read_csv('processed_ahu_data.csv')

# Drop the target variable
X = data.drop(columns=['CurrentKW', 'timestamp'])
y = data['CurrentKW']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Ridge regression model (you could use Lasso as well)
model = Ridge(alpha=1.0)  # Alpha controls regularization strength; tune this hyperparameter
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error with Ridge: {mse}")

# Optional: Save model for RL use
import joblib
joblib.dump(model, 'ridge_regression_model.pkl')
