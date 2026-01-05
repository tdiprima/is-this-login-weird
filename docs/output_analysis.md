Let's investigate why these are flagged as anomalies. The issue is that Isolation Forest is finding patterns that are **unusual combinations**, not just individual weird values.

Let me show you how to understand what makes them anomalous:

```python
import pandas as pd

# Look at the distribution of normal vs anomalous data
normal = df[df['anomaly'] == 1]
anomalous = df[df['anomaly'] == -1]

print("=== NORMAL DATA STATISTICS ===")
print(normal.describe())
print("\n=== ANOMALOUS DATA STATISTICS ===")
print(anomalous.describe())

print("\n=== COUNTRY DISTRIBUTION ===")
print("Normal:")
print(normal['country'].value_counts(normalize=True))
print("\nAnomalous:")
print(anomalous['country'].value_counts(normalize=True))

print("\n=== HOUR DISTRIBUTION ===")
print("Normal:")
print(normal['hour_of_day'].value_counts().sort_index())
print("\nAnomalous:")
print(anomalous['hour_of_day'].value_counts().sort_index())

print("\n=== DEVICE DISTRIBUTION ===")
print("Normal:")
print(normal['device_type'].value_counts(normalize=True))
print("\nAnomalous:")
print(anomalous['device_type'].value_counts(normalize=True))
```

Looking at your results, I can see some patterns:

1. **Australia (AU) shows up a LOT** - probably because it's only 5% of your data, so combinations with AU are "rare"
2. **Late night hours (0, 1, 2, 3am)** - these are low-probability times
3. **Unusual combinations** - like "AU + midnight + 7 sessions" might be rare even if each individual feature seems normal

## The Real Issue: Your contamination parameter!

```python
contamination=0.01  # Expects 1% anomalies
```

But you're getting 51 out of 5003 rows = **1.02% anomalies**! The model is doing exactly what you told it to do.

## To Fix This:

**Option 1**: Lower the contamination if you truly expect fewer anomalies:

```python
iso_forest = IsolationForest(
    contamination=0.001,  # Expect 0.1% (only ~5 anomalies)
    random_state=42
)
```

**Option 2**: Use the anomaly score to set your own threshold:

```python
# Instead of using predict(), use score_samples()
df['anomaly_score'] = iso_forest.score_samples(X)

# Look at the distribution
print(df['anomaly_score'].describe())

# Set your own threshold (more negative = more anomalous)
threshold = -0.7
df['is_anomaly'] = df['anomaly_score'] < threshold

print(f"Anomalies with threshold {threshold}: {df['is_anomaly'].sum()}")
```

Try the second option and look at different thresholds. You'll see your 3 intentional anomalies (RU, CN, BR with high sessions) have the most negative scores!

<br>
