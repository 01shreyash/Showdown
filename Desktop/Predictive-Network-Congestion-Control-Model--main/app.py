import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib
import psutil
import time
import threading
import collections
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Network Congestion Monitor",
    layout="wide",
    page_icon="🚦"
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1e2130 0%, #2a2f45 100%);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
    border-left: 4px solid #4f8ef7;
}
.congested-card { border-left-color: #ff4b4b !important; }
.normal-card    { border-left-color: #00cc88 !important; }
.metric-label  { font-size: 12px; color: #aab; text-transform: uppercase; letter-spacing: 1px; }
.metric-value  { font-size: 28px; font-weight: 700; color: #fff; }
.metric-sub    { font-size: 12px; color: #778; margin-top: 2px; }
.status-badge  { display: inline-block; padding: 4px 14px; border-radius: 20px;
                  font-weight: 700; font-size: 14px; }
.badge-normal    { background: #00cc8830; color: #00cc88; }
.badge-congested { background: #ff4b4b30; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

st.title("🚦 Real-Time Network Congestion Monitor")
st.caption("Live psutil capture · Random Forest prediction · Rolling 60-second window")

# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = collections.deque(maxlen=60)
if "running" not in st.session_state:
    st.session_state.running = False
if "model" not in st.session_state:
    st.session_state.model = None

FEATURE_COLS = [
    "IPv4 bytes", "IPv4 pkts", "IPv4 flows",
    "Unique IPv4 addresses", "Unique IPv4 source addresses",
    "Unique IPv4 destination addresses",
    "Unique IPv4 TCP source ports", "Unique IPv4 TCP destination ports",
    "Unique IPv4 UDP source ports", "Unique IPv4 UDP destination ports",
]
CONGESTION_THRESHOLD = 1e10   # bytes — matches training label


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def fmt_bytes(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def collect_live_snapshot(prev_io):
    """
    Collect one second of real psutil metrics and derive
    features in the same shape the model expects.
    """
    io1 = prev_io
    time.sleep(1)
    io2 = psutil.net_io_counters()

    bytes_total = (io2.bytes_sent - io1.bytes_sent) + (io2.bytes_recv - io1.bytes_recv)
    pkts_total  = (io2.packets_sent - io1.packets_sent) + (io2.packets_recv - io1.packets_recv)

    # Connection-level detail
    try:
        conns = psutil.net_connections(kind="inet")
    except Exception:
        conns = []

    src_ports_tcp = set()
    dst_ports_tcp = set()
    src_ports_udp = set()
    dst_ports_udp = set()
    src_ips = set()
    dst_ips = set()
    all_ips = set()
    flows = 0

    for c in conns:
        flows += 1
        laddr = c.laddr
        raddr = c.raddr if c.raddr else None
        is_udp = (c.type == 2)          # SOCK_DGRAM = UDP

        if laddr:
            src_ips.add(laddr.ip)
            all_ips.add(laddr.ip)
            if is_udp:
                src_ports_udp.add(laddr.port)
            else:
                src_ports_tcp.add(laddr.port)
        if raddr:
            dst_ips.add(raddr.ip)
            all_ips.add(raddr.ip)
            if is_udp:
                dst_ports_udp.add(raddr.port)
            else:
                dst_ports_tcp.add(raddr.port)

    # Scale bytes to match training data magnitude (1-second window → project to hour)
    # Training data appears to be per-hour aggregates; multiply to keep scale consistent
    SCALE = 3600
    snap = {
        "timestamp": datetime.now(),
        "IPv4 bytes":                          bytes_total * SCALE,
        "IPv4 pkts":                           pkts_total  * SCALE,
        "IPv4 flows":                          flows,
        "Unique IPv4 addresses":               len(all_ips),
        "Unique IPv4 source addresses":        len(src_ips),
        "Unique IPv4 destination addresses":   len(dst_ips),
        "Unique IPv4 TCP source ports":        len(src_ports_tcp),
        "Unique IPv4 TCP destination ports":   len(dst_ports_tcp),
        "Unique IPv4 UDP source ports":        len(src_ports_udp),
        "Unique IPv4 UDP destination ports":   len(dst_ports_udp),
        # raw (unscaled) for display
        "_raw_bytes": bytes_total,
        "_raw_pkts":  pkts_total,
    }
    return snap, io2


def predict(model, snap):
    row = pd.DataFrame([{k: snap[k] for k in FEATURE_COLS}])
    pred   = model.predict(row)[0]
    proba  = model.predict_proba(row)[0]
    # If model was trained on only 1 class, index [1] won't exist
    classes = list(model.classes_)
    prob = proba[classes.index(1)] if 1 in classes else 0.0
    return int(pred), float(prob)


def load_or_train_model(csv_path=None):
    """Load pkl if available, else train fresh from CSV."""
    try:
        m = joblib.load("network_congestion_model.pkl")
        return m, "Loaded pre-trained model (.pkl)"
    except Exception:
        pass
    if csv_path is None:
        return None, "No model found."
    df = pd.read_csv(csv_path)
    df["congestion"] = (df["IPv4 bytes"] > CONGESTION_THRESHOLD).astype(int)
    X = df[FEATURE_COLS]
    y = df["congestion"]
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    return model, "Trained fresh model from CSV"


# ─────────────────────────────────────────────
# Sidebar — model loading
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("Model")
    model_source = st.radio(
        "Load model from",
        ["Upload .pkl", "Upload CSV (retrain)", "Use bundled model"],
        index=2
    )

    if model_source == "Upload .pkl":
        pkl_file = st.file_uploader("Upload model .pkl", type=["pkl"])
        if pkl_file:
            import tempfile, os
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
                f.write(pkl_file.read())
                tmp = f.name
            try:
                st.session_state.model = joblib.load(tmp)
                st.success("✅ Model loaded!")
            except Exception as e:
                st.error(f"Failed: {e}")
            os.unlink(tmp)

    elif model_source == "Upload CSV (retrain)":
        csv_file = st.file_uploader("Upload training CSV", type=["csv"])
        if csv_file and st.button("Train model"):
            with st.spinner("Training…"):
                df = pd.read_csv(csv_file)
                df["congestion"] = (df["IPv4 bytes"] > CONGESTION_THRESHOLD).astype(int)
                X = df[FEATURE_COLS]; y = df["congestion"]
                X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
                m = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
                m.fit(X_tr, y_tr)
                st.session_state.model = m
                st.success("✅ Model trained!")
                report = classification_report(y_te, m.predict(X_te))
                st.text(report)

    else:  # bundled
        if st.session_state.model is None:
            try:
                import os
                path = "network_congestion_model.pkl"
                if not os.path.exists(path):
                    path = "/mnt/user-data/uploads/network_congestion_model.pkl"
                st.session_state.model = joblib.load(path)
                st.success("✅ Bundled model loaded")
            except Exception as e:
                st.warning(f"Could not load bundled model: {e}")

    st.divider()
    st.subheader("Capture")
    refresh_rate = st.slider("Refresh interval (s)", 1, 10, 2)
    window_size  = st.slider("History window (ticks)", 10, 60, 30)
    show_raw     = st.checkbox("Show raw feature table", False)

    st.divider()
    st.subheader("About")
    st.markdown("""
- **Live capture**: `psutil` (no root needed)
- **Model**: Random Forest Classifier
- **Features**: 10 IPv4 network metrics
- **Window**: rolling 60-tick ring buffer
""")

# ─────────────────────────────────────────────
# Main layout
# ─────────────────────────────────────────────
if st.session_state.model is None:
    st.warning("⚠️ No model loaded. Use the sidebar to load or train one.")
    st.stop()

model = st.session_state.model

# Control buttons
col_start, col_stop, col_clear = st.columns([1, 1, 4])
with col_start:
    start_btn = st.button("▶ Start Monitoring", type="primary", use_container_width=True)
with col_stop:
    stop_btn  = st.button("⏹ Stop", use_container_width=True)

if start_btn:
    st.session_state.running = True
if stop_btn:
    st.session_state.running = False

st.divider()

# ─────────────────────────────────────────────
# Live dashboard placeholders
# ─────────────────────────────────────────────
ph_status   = st.empty()
ph_metrics  = st.empty()
ph_charts   = st.empty()
ph_table    = st.empty()

# ─────────────────────────────────────────────
# Monitoring loop
# ─────────────────────────────────────────────
if st.session_state.running:
    prev_io = psutil.net_io_counters()
    tick = 0

    while st.session_state.running:
        snap, prev_io = collect_live_snapshot(prev_io)
        pred, prob    = predict(model, snap)
        snap["prediction"] = pred
        snap["prob"]       = prob
        st.session_state.history.append(snap)

        hist = list(st.session_state.history)[-window_size:]
        df_h = pd.DataFrame(hist)

        # ── Status banner ──────────────────────────────
        label = "CONGESTED" if pred == 1 else "NORMAL"
        badge_cls = "badge-congested" if pred == 1 else "badge-normal"
        card_cls  = "congested-card"  if pred == 1 else "normal-card"

        ph_status.markdown(f"""
<div class="metric-card {card_cls}">
  <div class="metric-label">Current Network Status · {snap['timestamp'].strftime('%H:%M:%S')}</div>
  <div style="display:flex; align-items:center; gap:16px; margin-top:6px;">
    <div class="metric-value">{label}</div>
    <span class="status-badge {badge_cls}">{prob*100:.1f}% congestion probability</span>
  </div>
  <div class="metric-sub">Raw bytes/s: {fmt_bytes(snap['_raw_bytes'])} &nbsp;|&nbsp;
       Packets/s: {snap['_raw_pkts']:,} &nbsp;|&nbsp;
       Active connections: {snap['IPv4 flows']}</div>
</div>
""", unsafe_allow_html=True)

        # ── Key metrics row ────────────────────────────
        m1, m2, m3, m4 = ph_metrics.columns(4)
        congested_pct = (df_h["prediction"].sum() / len(df_h) * 100) if df_h.shape[0] else 0
        avg_prob = df_h["prob"].mean() * 100 if df_h.shape[0] else 0
        m1.metric("Bytes/s (raw)",    fmt_bytes(snap["_raw_bytes"]))
        m2.metric("Packets/s",        f"{snap['_raw_pkts']:,}")
        m3.metric("Congestion rate",  f"{congested_pct:.0f}%",
                   delta=f"{congested_pct - 50:.0f}% vs 50% baseline")
        m4.metric("Avg probability",  f"{avg_prob:.1f}%")

        # ── Charts ────────────────────────────────────
        if len(df_h) >= 2:
            fig, axs = plt.subplots(1, 3, figsize=(18, 4),
                                     facecolor="#1a1d2e")
            for ax in axs:
                ax.set_facecolor("#1e2130")
                ax.tick_params(colors="#aab")
                ax.spines[:].set_color("#333")

            # 1. Congestion probability timeline
            colors = ["#ff4b4b" if p == 1 else "#00cc88"
                      for p in df_h["prediction"]]
            axs[0].bar(range(len(df_h)), df_h["prob"], color=colors, width=0.8)
            axs[0].axhline(0.5, color="#ffcc00", linestyle="--", linewidth=1, label="50% threshold")
            axs[0].set_title("Congestion Probability (per tick)", color="#fff", fontsize=11)
            axs[0].set_ylabel("Probability", color="#aab")
            axs[0].set_ylim(0, 1)
            axs[0].legend(facecolor="#1e2130", labelcolor="#fff", fontsize=8)

            # 2. Bytes trend (scaled)
            axs[1].plot(df_h["IPv4 bytes"].values, color="#4f8ef7", linewidth=2)
            axs[1].axhline(CONGESTION_THRESHOLD, color="#ff4b4b",
                           linestyle="--", linewidth=1, label="Congestion threshold")
            axs[1].fill_between(range(len(df_h)), df_h["IPv4 bytes"],
                                alpha=0.2, color="#4f8ef7")
            axs[1].set_title("IPv4 Bytes (scaled/hr)", color="#fff", fontsize=11)
            axs[1].set_ylabel("Bytes", color="#aab")
            axs[1].legend(facecolor="#1e2130", labelcolor="#fff", fontsize=8)

            # 3. Active connections & unique IPs
            ax3 = axs[2]
            ax3b = ax3.twinx()
            ax3.plot(df_h["IPv4 flows"].values,        color="#a78bfa", linewidth=2, label="Flows")
            ax3b.plot(df_h["Unique IPv4 addresses"].values, color="#34d399", linewidth=2, linestyle="--", label="Unique IPs")
            ax3.set_title("Flows & Unique IPs", color="#fff", fontsize=11)
            ax3.set_ylabel("Flows", color="#a78bfa")
            ax3b.set_ylabel("Unique IPs", color="#34d399")
            ax3.tick_params(axis="y", colors="#a78bfa")
            ax3b.tick_params(axis="y", colors="#34d399")
            ax3b.spines[:].set_color("#333")
            lines1, l1 = ax3.get_legend_handles_labels()
            lines2, l2 = ax3b.get_legend_handles_labels()
            ax3.legend(lines1 + lines2, l1 + l2,
                       facecolor="#1e2130", labelcolor="#fff", fontsize=8)

            plt.tight_layout(pad=1.5)
            ph_charts.pyplot(fig)
            plt.close(fig)

        # ── Raw table ─────────────────────────────────
        if show_raw and len(df_h) > 0:
            display_df = df_h[["timestamp", "prediction", "prob",
                                "_raw_bytes", "_raw_pkts", "IPv4 flows",
                                "Unique IPv4 addresses"]].copy()
            display_df.columns = ["Time", "Pred", "Prob",
                                  "Bytes/s", "Pkts/s", "Flows", "Unique IPs"]
            display_df["Time"]  = display_df["Time"].dt.strftime("%H:%M:%S")
            display_df["Prob"]  = display_df["Prob"].map("{:.2%}".format)
            display_df["Bytes/s"] = display_df["Bytes/s"].apply(fmt_bytes)
            display_df["Pred"]  = display_df["Pred"].map({0: "✅ Normal", 1: "🔴 Congested"})
            ph_table.dataframe(display_df.iloc[::-1].reset_index(drop=True),
                               use_container_width=True)

        tick += 1
        time.sleep(max(0, refresh_rate - 1))   # subtract the 1s already spent in collect

else:
    if len(st.session_state.history) == 0:
        st.info("👆 Press **▶ Start Monitoring** to begin live capture.")
    else:
        st.success("Monitoring paused. Press ▶ to resume.")

        # Show last known state from history
        hist = list(st.session_state.history)
        df_h = pd.DataFrame(hist)

        st.subheader("📊 Last Session Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total ticks recorded", len(df_h))
        c2.metric("Congested ticks",
                  int(df_h["prediction"].sum()),
                  delta=f"{df_h['prediction'].mean()*100:.0f}% of session")
        c3.metric("Peak congestion prob",
                  f"{df_h['prob'].max()*100:.1f}%")

        fig, ax = plt.subplots(figsize=(14, 3), facecolor="#1a1d2e")
        ax.set_facecolor("#1e2130")
        colors = ["#ff4b4b" if p else "#00cc88" for p in df_h["prediction"]]
        ax.bar(range(len(df_h)), df_h["prob"], color=colors, width=0.8)
        ax.axhline(0.5, color="#ffcc00", linestyle="--", linewidth=1)
        ax.set_title("Session — Congestion Probability per Tick", color="#fff")
        ax.tick_params(colors="#aab")
        ax.spines[:].set_color("#333")
        normal_patch    = mpatches.Patch(color="#00cc88", label="Normal")
        congested_patch = mpatches.Patch(color="#ff4b4b", label="Congested")
        ax.legend(handles=[normal_patch, congested_patch],
                  facecolor="#1e2130", labelcolor="#fff")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)