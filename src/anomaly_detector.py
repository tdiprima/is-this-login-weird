import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("../data/logins_raw.csv")

# Step 1: Prepare the data
# We need to convert text into numbers for the algorithm
df_encoded = df.copy()

# Convert categorical columns to numbers
le_country = LabelEncoder()
le_device = LabelEncoder()

df_encoded['country_encoded'] = le_country.fit_transform(df['country'])
df_encoded['device_encoded'] = le_device.fit_transform(df['device_type'])
df_encoded['login_success_encoded'] = df['login_success'].astype(int)

# Step 2: Select features for the model
features = ['hour_of_day', 'country_encoded', 'device_encoded',
            'login_success_encoded', 'sessions_per_hour']

X = df_encoded[features]

# Step 3: Train the Isolation Forest
iso_forest = IsolationForest(
    contamination=0.01,  # Expect 1% of data to be anomalies
    random_state=42,
    n_estimators=100     # Number of trees
)

iso_forest.fit(X)

# Step 4: Predict anomalies
# Returns -1 for anomalies, 1 for normal
df['anomaly'] = iso_forest.predict(X)
df['anomaly_score'] = iso_forest.score_samples(X)  # Lower = more anomalous

# Step 5: Look at the anomalies
anomalies = df[df['anomaly'] == -1].sort_values('anomaly_score')
print("Detected Anomalies:")
print(anomalies)

print(f"\nTotal anomalies found: {len(anomalies)}")
