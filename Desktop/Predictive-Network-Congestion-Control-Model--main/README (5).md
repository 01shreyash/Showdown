# 🚦 Real-Time Network Congestion Monitor

A live network congestion detection dashboard built with **Streamlit**, powered by a **Random Forest Classifier** trained on IPv4 traffic metrics. The app captures real-time network data using `psutil`, predicts congestion probability each second, and displays results in an interactive dark-themed dashboard.

---

## 📸 Features

- **Live traffic capture** via `psutil` — no root/admin privileges required
- **ML-based prediction** using a pre-trained Random Forest model (`.pkl`)
- **Rolling 60-tick history** with configurable window size
- **Interactive dark dashboard** with real-time charts:
  - Congestion probability timeline (per tick)
  - IPv4 byte volume vs. congestion threshold
  - Active flows & unique IP trends
- **Flexible model loading** — use a bundled `.pkl`, upload your own, or retrain from a CSV
- **Raw feature table** (optional toggle) for debugging and inspection
- **Session summary** shown after monitoring is paused

---

## 🗂️ Project Structure

```
.
├── app.py                          # Main Streamlit dashboard
├── data.py                         # Standalone script to test a single prediction
├── python.py                       # Minimal Streamlit + matplotlib test app
├── network_congestion_model.pkl    # Pre-trained Random Forest model
└── network_congestion_data.csv     # Training dataset (IPv4 network metrics)
```

---

## ⚙️ Requirements

- Python 3.8+
- Install dependencies:

```bash
pip install streamlit pandas numpy matplotlib seaborn scikit-learn joblib psutil
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/network-congestion-monitor.git
cd network-congestion-monitor
```

### 2. Run the dashboard

```bash
streamlit run app.py
```

### 3. Load a model

In the sidebar, choose one of:

| Option | Description |
|---|---|
| **Use bundled model** | Loads `network_congestion_model.pkl` automatically |
| **Upload .pkl** | Upload your own pre-trained model file |
| **Upload CSV (retrain)** | Upload `network_congestion_data.csv` to train a fresh model |

### 4. Start monitoring

Click **▶ Start Monitoring** to begin live capture. Click **⏹ Stop** to pause and view a session summary.

---

## 🧠 Model Details

| Property | Value |
|---|---|
| Algorithm | Random Forest Classifier |
| Features | 10 IPv4 network metrics (see below) |
| Label | Congested (`1`) if `IPv4 bytes > 1×10¹⁰` per hour, else Normal (`0`) |
| Training split | 80% train / 20% test |
| Class weighting | `balanced` (handles imbalanced congestion events) |

### Input Features

| Feature | Description |
|---|---|
| `IPv4 bytes` | Total bytes transferred (scaled to per-hour) |
| `IPv4 pkts` | Total packets transferred |
| `IPv4 flows` | Number of active network connections |
| `Unique IPv4 addresses` | Count of unique IPs seen |
| `Unique IPv4 source addresses` | Unique source IPs |
| `Unique IPv4 destination addresses` | Unique destination IPs |
| `Unique IPv4 TCP source ports` | Unique TCP source ports |
| `Unique IPv4 TCP destination ports` | Unique TCP destination ports |
| `Unique IPv4 UDP source ports` | Unique UDP source ports |
| `Unique IPv4 UDP destination ports` | Unique UDP destination ports |

> **Note:** Live snapshots are captured over 1-second windows and scaled by ×3600 to align with the per-hour magnitude of the training data.

---

## 🧪 Running a Quick Prediction

You can test the model directly without the dashboard using `data.py`:

```bash
python data.py
```

Edit the feature values inside `data.py` to simulate different traffic scenarios. Example output:

```
Predicted Congestion: Yes
```

---

## 📊 Dashboard Sidebar Options

| Setting | Description |
|---|---|
| Refresh interval | How often (in seconds) the dashboard updates (1–10s) |
| History window | Number of recent ticks shown in charts (10–60) |
| Show raw feature table | Toggle a live table of all captured metrics |

---

## 📁 Dataset

`network_congestion_data.csv` contains historical IPv4 network metrics used to train the model. The congestion label is derived automatically at training time based on the `IPv4 bytes` threshold (`1×10¹⁰`).

---

## 🛠️ How It Works

```
psutil (1s capture)
       ↓
Feature extraction (10 IPv4 metrics)
       ↓
Scale ×3600 to match training magnitude
       ↓
Random Forest → predict() + predict_proba()
       ↓
Live dashboard update (status, charts, metrics)
```

---

## 📄 License

MIT License. Feel free to use, modify, and distribute.

---

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.
