import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import shap
import matplotlib.pyplot as plt

# ---------------------------
# Load data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"data\Flipkart\FiPhones_01-08-25.csv")
    df = df.dropna()
    return df

data = load_data()

# ---------------------------
# Prepare features and target
# ---------------------------
target_col = "rating_average"
if target_col not in data.columns:
    target_col = data.columns[-1] 

X = data.drop(columns=[target_col])

# Encode categorical/text features automatically
X = pd.get_dummies(X, drop_first=True)
y = data[target_col]

# ---------------------------
# Train model
# ---------------------------
@st.cache_resource
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, X_train, X_test, y_train, y_test

model, X_train, X_test, y_train, y_test = train_model(X, y)

# ---------------------------
# Sidebar: select sample
# ---------------------------
st.sidebar.title("Predictive Dashboard")
selected_index = st.sidebar.slider("Select sample index", 0, len(data)-1, 0)
sample = X.iloc[selected_index:selected_index+1]

# ---------------------------
# Prediction
# ---------------------------
st.subheader("Prediction")
prediction = model.predict(sample)
st.write(f"Predicted value: {prediction[0]:.2f}")

# ---------------------------
# Model Performance Metrics
# ---------------------------
st.subheader("Model Performance Metrics")
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

metrics = {
    "R² Train": r2_score(y_train, y_pred_train),
    "R² Test": r2_score(y_test, y_pred_test),
    "MSE Test": mean_squared_error(y_test, y_pred_test),
    "MAE Test": mean_absolute_error(y_test, y_pred_test),
    "RMSE Test": mean_squared_error(y_test, y_pred_test, squared=False),
}

for k, v in metrics.items():
    st.write(f"{k}: {v:.3f}")

# ---------------------------
# SHAP Feature Importance
# ---------------------------
st.subheader("SHAP Feature Importance")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

fig, ax = plt.subplots()
shap.summary_plot(shap_values, X, show=False)
st.pyplot(fig)

# ---------------------------
# Data Drift Check (Rolling Z-Score)
# ---------------------------
st.subheader("Data Drift Check (Rolling Z-Score)")
window_size = 20
rolling_mean = y.rolling(window=window_size).mean()
rolling_std = y.rolling(window=window_size).std()
z_score = (y - rolling_mean) / rolling_std
drift_flags = z_score.abs() > 3  # flag if >3 std dev

st.write(f"Drift detected in {drift_flags.sum()} samples out of {len(y)}")
st.line_chart(pd.DataFrame({"Target": y, "Drift": drift_flags.astype(int)}))

# ---------------------------
# Responsible AI Checklist
# ---------------------------
st.subheader("Responsible AI Checklist")
st.markdown("""
- **Fairness:** Check model performance across demographic/product groups.
- **Privacy:** Ensure sensitive info is protected.
- **Consent:** Verify data collection was authorized.
- **Transparency:** Provide interpretable predictions (SHAP plots).
- **Robustness:** Monitor model drift over time.
""")
