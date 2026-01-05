import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("../data/logins_raw.csv")

# Step 1: Prepare the data
# We need to convert text into numbers for the algorithm
df_encoded = df.copy()

# Convert categorical columns to numbers
le_country = LabelEncoder()
le_device = LabelEncoder()

df_encoded["country_encoded"] = le_country.fit_transform(df["country"])
df_encoded["device_encoded"] = le_device.fit_transform(df["device_type"])
df_encoded["login_success_encoded"] = df["login_success"].astype(int)

# Step 2: Select features for the model
features = [
    "hour_of_day",
    "country_encoded",
    "device_encoded",
    "login_success_encoded",
    "sessions_per_hour",
]

X = df_encoded[features]

# Step 3: Train the Isolation Forest
iso_forest = IsolationForest(
    contamination=0.005,  # Expect 0.5% of data to be anomalies
    random_state=42,
    n_estimators=100,  # Number of trees
)

iso_forest.fit(X)

# Step 4: Predict anomalies
# Returns -1 for anomalies, 1 for normal
df["anomaly"] = iso_forest.predict(X)
df["anomaly_score"] = iso_forest.score_samples(X)  # Lower = more anomalous

# Step 5: Look at the anomalies
anomalies = df[df["anomaly"] == -1].sort_values("anomaly_score")
print("Detected Anomalies:")
print(anomalies)
print(f"\nTotal anomalies found: {len(anomalies)}")

suspicious = df[df['anomaly_score'] < -0.72]  # Your worst scores
print("Suspicious:")
print(suspicious)

# New login attempt to check
new_login = pd.DataFrame(
    {
        "hour_of_day": [3],
        "country": ["RU"],
        "device_type": ["desktop"],
        "login_success": [False],
        "sessions_per_hour": [15],
    }
)

# Encode it the same way
new_login["country_encoded"] = le_country.transform(new_login["country"])
new_login["device_encoded"] = le_device.transform(new_login["device_type"])
new_login["login_success_encoded"] = new_login["login_success"].astype(int)

# Predict
new_X = new_login[features]
prediction = iso_forest.predict(new_X)
score = iso_forest.score_samples(new_X)

if prediction[0] == -1:
    print(f"🚨 ANOMALY DETECTED! Score: {score[0]:.3f}")
else:
    print(f"✅ Normal login. Score: {score[0]:.3f}")

# We Should Evaluate It!

# Assuming you know which ones are actually anomalous
# (In our case, we added 3 anomalies manually)
# Let's create a true label column first
true_labels = [0] * len(df)  # 0 = normal
true_labels[-3:] = [1, 1, 1]  # Last 3 are anomalies
df["true_anomaly"] = true_labels

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    df["true_anomaly"],
    test_size=0.2,
    random_state=42,
    stratify=df["true_anomaly"],  # Keep anomaly ratio consistent
)

# Train ONLY on training data
iso_forest.fit(X_train)

# Test on held-out data
test_predictions = iso_forest.predict(X_test)
test_predictions = (test_predictions == -1).astype(int)  # Convert -1/1 to 1/0

# Evaluate
print(confusion_matrix(y_test, test_predictions))
print(classification_report(y_test, test_predictions))
