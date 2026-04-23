import pandas as pd
import joblib

# Load the trained model
model = joblib.load('network_congestion_model.pkl')

# Define a new data point (use real values matching the feature scale of your data)
new_data = pd.DataFrame([{
    'IPv4 bytes': 6e10,   # very high traffic (higher than threshold 2.5e10)
    'IPv4 pkts': 400000,  # high number of packets
    'IPv4 flows': 2500,   # lots of flows
    'Unique IPv4 addresses': 1000,
    'Unique IPv4 source addresses': 600,
    'Unique IPv4 destination addresses': 400,
    'Unique IPv4 TCP source ports': 200,
    'Unique IPv4 TCP destination ports': 180,
    'Unique IPv4 UDP source ports': 150,
    'Unique IPv4 UDP destination ports': 160
}])

# Predict congestion
prediction = model.predict(new_data)
print("Predicted Congestion:", "Yes" if prediction[0] == 1 else "No")