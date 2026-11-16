import streamlit as st

st.title('🎈 6_Wheel_Rover_App')

import json
import time
import paho.mqtt.client as mqtt
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# PAGE CONFIG & DWIN ROYAL BLUE THEME CSS
# ============================================================
st.set_page_config(
    page_title="IoT Smart Energy Management System",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(135deg, #1b5299 0%, #246bc2 50%, #164480 100%);
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #154685 0%, #1e60b5 100%);
        border-right: 2px solid #5ca4ff;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    .hmi-header {
        background: rgba(16, 52, 102, 0.75);
        border-bottom: 3px solid #66b2ff;
        padding: 15px 25px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .hmi-title {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .hmi-subtitle {
        font-size: 14px;
        color: #cce4ff;
        margin-top: 4px;
    }
    .dwin-panel {
        background: rgba(20, 65, 125, 0.65);
        border: 2px solid #7ab8ff;
        border-radius: 22px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .dwin-subcard {
        background: rgba(15, 52, 105, 0.8);
        border: 1.5px solid #66a3ff;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .card-label {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
    }
    .card-value-red {
        font-size: 28px;
        font-weight: 800;
        color: #ff6b6b;
    }
    .card-value-cyan {
        font-size: 26px;
        font-weight: 800;
        color: #4dd2ff;
    }
    .card-value-white {
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
    }
    .card-note {
        font-size: 12px;
        font-style: italic;
        color: #b3d7ff;
        margin-top: 4px;
    }
    div.stButton > button {
        background-color: #103466 !important;
        color: #ffffff !important;
        border-radius: 14px;
        font-weight: 700;
        font-size: 16px;
        padding: 12px 18px;
        border: 2px solid #66b2ff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #246bc2 !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
    }
    label, .stRadio label, .stToggle label {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# MQTT CLOUD CONNECTION (Passive Listener + User-Triggered Only)
# ============================================================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = "sems/ray/telemetry"
TOPIC_CONTROL = "sems/ray/control"
TOPIC_TOPUP = "sems/ray/topup"
TOPIC_SETTINGS = "sems/ray/settings"


@st.cache_resource
def get_shared_state():
  return {
      "telemetry": {
          "voltage": 0.00,
          "current": 0.00,
          "power": 0.00,
          "frequency": 50.0,
          "pf": 0.00,
          "apparent": 0.00,
          "reactive": 0.00,
          "phase": 5.807,
          "kwh": 0.00,
          "units": 100.00,
          "days": 24,
          "credit": 1000.00,
          "cost": 0.00,
          "sec": 0,
          "ref": 0,
          "lit": 0,
          "wh": 0,
          "ac": 0,
          "manual": 1,
      },
      "locks": {},
  }


shared_state = get_shared_state()


def lock_keys(keys, duration=3.0):
  expiry = time.time() + duration
  for k in keys:
    shared_state["locks"][k] = expiry


def on_message(client, userdata, msg):
  try:
    payload = json.loads(msg.payload.decode())
    now = time.time()
    for k, v in payload.items():
      if shared_state["locks"].get(k, 0) > now:
        continue
      shared_state["telemetry"][k] = v
  except Exception:
    pass


@st.cache_resource
def init_mqtt():
  client = mqtt.Client()
  client.on_message = on_message
  client.connect(MQTT_BROKER, MQTT_PORT, 60)
  client.subscribe(TOPIC_TELEMETRY)
  client.loop_start()
  return client


mqtt_client = init_mqtt()
data = shared_state["telemetry"]

# ============================================================
# LEFT SIDEBAR MENU
# ============================================================
with st.sidebar:
  st.markdown(
      "<div style='text-align:center; font-size: 64px;'>🏠</div>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  page = st.radio(
      "Navigation",
      [
          "🏠 Home",
          "⚡ Live Data",
          "📊 Consumption",
          "🎛️ Load Control",
          "⚙️ Settings",
          "ℹ️ About",
      ],
      label_visibility="collapsed",
  )
  st.markdown("---")
  auto_refresh = st.checkbox("Live Sync (2s)", value=True)

# ============================================================
# TOP PERSISTENT BANNER
# ============================================================
st.markdown(
    """
<div class="hmi-header">
    <div class="hmi-title">IoT SMART ENERGY MANAGEMENT SYSTEM</div>
    <div class="hmi-subtitle">Real-time Monitoring | Load Management | Usage Trends</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# PAGE 1: HOME
# ============================================================
if page == "🏠 Home":
  col_left, col_right = st.columns([1.05, 1.35])

  with col_left:
    st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)
    st.markdown("### 👆 Quick Controls")

    if st.button("🟢 Turn All ON", use_container_width=True):
      devices = ["sec", "ref", "lit", "wh", "ac"]
      lock_keys(devices, 3.0)
      for dev in devices:
        shared_state["telemetry"][dev] = 1
        mqtt_client.publish(TOPIC_CONTROL, f"{dev}:1")
      st.toast("Sent: Turn All ON")
      st.rerun()

    st.write("")

    if st.button("🔴 Turn All OFF", use_container_width=True):
      devices = ["sec", "ref", "lit", "wh", "ac"]
      lock_keys(devices, 3.0)
      for dev in devices:
        shared_state["telemetry"][dev] = 0
        mqtt_client.publish(TOPIC_CONTROL, f"{dev}:0")
      st.toast("Sent: Turn All OFF")
      st.rerun()

    st.write("")

    manual_active = data.get("manual", 1) == 1
    btn_label = (
        "🖐️ Manual Control: ON"
        if manual_active
        else "🤖 Manual Control: OFF (Auto-Shedding)"
    )
    if st.button(btn_label, use_container_width=True):
      new_manual = 0 if manual_active else 1
      lock_keys(["manual"], 3.0)
      shared_state["telemetry"]["manual"] = new_manual
      mqtt_client.publish(TOPIC_SETTINGS, f"manual:{new_manual}")
      st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

  with col_right:
    st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)
    st.markdown("### 💵 Prepaid Credit")

    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
      st.markdown(
          f"""
            <div class="dwin-subcard">
                <div class="card-label">⚡ Units</div>
                <div class="card-value-red">{data['units']:.2f}</div>
                <div class="card-note">Available kWh</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with r1_c2:
      st.markdown(
          f"""
            <div class="dwin-subcard">
                <div class="card-label">📅 Days</div>
                <div class="card-value-red">{int(data.get('days', 24))}</div>
                <div class="card-note">Estimate Remaining</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
      credit_val = data.get("credit", data["units"] * 10.0)
      st.markdown(
          f"""
            <div class="dwin-subcard">
                <div class="card-label">🪙 Credit</div>
                <div class="card-value-red">{credit_val:.2f}</div>
                <div class="card-note">Remaining Balance</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with r2_c2:
      st.markdown(
          f"""
            <div class="dwin-subcard">
                <div class="card-label">💰 Cost</div>
                <div class="card-value-red">{data['cost']:.2f}</div>
                <div class="card-note">Estimate For The Month</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE 2: LIVE DATA
# ============================================================
elif page == "⚡ Live Data":
  st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)

  kw_power = data["power"] / 1000.0
  kva_power = data.get("apparent", data["power"] * 1.05) / 1000.0
  kvar_power = data.get("reactive", data["power"] * 0.30) / 1000.0

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">🟣 Voltage</div>
            <div class="card-value-red">{data['voltage']:.2f} V</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with c2:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">🔵 Current</div>
            <div class="card-value-cyan">{data['current']:.2f} A</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with c3:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">🟢 True Power</div>
            <div class="card-value-white">{kw_power:.3f} kW</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with c4:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">〰️ Frequency</div>
            <div class="card-value-cyan">{data.get('frequency', 50):.0f} Hz</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  c5, c6, c7, c8 = st.columns(4)
  with c5:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">PF Power Factor</div>
            <div class="card-value-white">{data.get('pf', 0.95):.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with c6:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">VA Apparent Power</div>
            <div class="card-value-white">{kva_power:.2f} kVA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with c7:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">⚡ Reactive Power</div>
            <div class="card-value-red">{kvar_power:.2f} kVAr</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with c8:
    st.markdown(
        f"""
        <div class="dwin-subcard">
            <div class="card-label">Φ Phase Angle</div>
            <div class="card-value-cyan">{data.get('phase', 5.807):.3f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE 3: CONSUMPTION
# ============================================================
elif page == "📊 Consumption":
  st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)

  h_col, tab_col = st.columns([1.2, 1])
  with h_col:
    st.markdown("### 📊 Energy Consumption Trend")
  with tab_col:
    period = st.radio(
        "Period", ["Day", "Week", "Month"], horizontal=True, label_visibility="collapsed"
    )

  if period == "Day":
    df = pd.DataFrame({
        "Time": [f"{h:02d}:00" for h in range(24)],
        "Power (kW)": [
            (data["power"] / 1000.0) * (0.5 + 0.5 * (h % 5 / 5))
            for h in range(24)
        ],
    })
    fig = px.area(df, x="Time", y="Power (kW)", title="Daily Load Curve")
  elif period == "Week":
    df = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Energy (kWh)": [
            data["kwh"] * d for d in [0.12, 0.15, 0.14, 0.18, 0.16, 0.13, 0.12]
        ],
    })
    fig = px.bar(df, x="Day", y="Energy (kWh)", title="Weekly Consumption")
  else:
    df = pd.DataFrame({
        "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "Energy (kWh)": [data["kwh"] * w for w in [0.22, 0.25, 0.28, 0.25]],
    })
    fig = px.line(
        df, x="Week", y="Energy (kWh)", markers=True, title="Monthly Trend"
    )

  fig.update_layout(
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(15, 52, 105, 0.6)",
      font_color="#FFFFFF",
  )
  st.plotly_chart(fig, use_container_width=True)
  st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE 4: LOAD CONTROL (Synced cleanly with DWIN HMI status)
# ============================================================
elif page == "🎛️ Load Control":
  st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)
  st.markdown("### 🔌 Load Status...")
  st.markdown("---")

  if data.get("manual", 1) == 0:
    st.warning(
        "⚠️ **Manual Control is OFF (Tiered Auto-Shedding Active):** Air Con"
        " sheds < 100 units | Water Heater < 80 | Lighting < 40 | Fridge < 20."
    )

  loads = [
      ("🛡️ Security System", "sec"),
      ("🧊 Refrigerator", "ref"),
      ("💡 Lighting", "lit"),
      ("🚿 Water Heater", "wh"),
      ("❄️ Air Conditioner", "ac"),
  ]

  for label, key in loads:
    c_lbl, c_sw = st.columns([3, 1])
    with c_lbl:
      st.markdown(f"#### {label}")
    with c_sw:
      # Dynamic key tied to current state so DWIN changes immediately move the Streamlit toggle
      current_val = data.get(key, 0) == 1
      widget_key = f"sw_{key}_{int(current_val)}"

      def make_on_change(dev_key, prev_val):
        def _cb():
          new_state = not prev_val
          lock_keys([dev_key], 3.0)
          shared_state["telemetry"][dev_key] = 1 if new_state else 0
          mqtt_client.publish(TOPIC_CONTROL, f"{dev_key}:{1 if new_state else 0}")
        return _cb

      st.toggle(
          "ON / OFF",
          value=current_val,
          key=widget_key,
          on_change=make_on_change(key, current_val),
          label_visibility="collapsed",
      )
    st.markdown(
        "<hr style='margin: 6px 0; border-color: rgba(255,255,255,0.25);'>",
        unsafe_allow_html=True,
    )

  st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE 5: SETTINGS
# ============================================================
elif page == "⚙️ Settings":
  st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)

  s1_lbl, s1_ctrl = st.columns([2, 1])
  with s1_lbl:
    st.markdown("### Manual Control")
    st.caption(
        "ON = Manual switching enabled | OFF = Automatic tiered load shedding"
        " active"
    )
  with s1_ctrl:
    is_manual = data.get("manual", 1) == 1
    manual_key = f"manual_sw_{int(is_manual)}"

    def on_manual_change():
      new_m = not is_manual
      lock_keys(["manual"], 3.0)
      shared_state["telemetry"]["manual"] = 1 if new_m else 0
      mqtt_client.publish(TOPIC_SETTINGS, f"manual:{1 if new_m else 0}")

    st.toggle(
        "Manual Control",
        value=is_manual,
        key=manual_key,
        on_change=on_manual_change,
        label_visibility="collapsed",
    )

  st.markdown(
      "<hr style='border-color: rgba(255,255,255,0.35);'>",
      unsafe_allow_html=True,
  )

  s2_lbl, s2_ctrl = st.columns([2, 1])
  with s2_lbl:
    st.markdown("### Top-up Units")
    st.caption("Enter prepaid token units (kWh) to credit the meter")
  with s2_ctrl:
    topup_units = st.number_input(
        "Units",
        min_value=1.0,
        max_value=5000.0,
        value=10.0,
        label_visibility="collapsed",
    )
    if st.button("⌨️ Credit Units", use_container_width=True):
      mqtt_client.publish(TOPIC_TOPUP, str(topup_units))
      st.success(f"Credited {topup_units:.2f} units!")

  st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE 6: ABOUT
# ============================================================
elif page == "ℹ️ About":
  st.markdown('<div class="dwin-panel">', unsafe_allow_html=True)
  st.markdown(
      "<h3 style='text-align: center;'>Version 1.0.0</h3>",
      unsafe_allow_html=True,
  )
  st.write("")
  st.markdown("""
    <p style='font-size: 18px; line-height: 1.6;'>
    The IoT Smart Energy Management System has been designed by <b>Raymond Midzi</b> as a final-year research project in partial fulfilment of the requirements for the Bachelor of Engineering (Hons) Degree in Mechatronics with Chinhoyi University of Technology, Zimbabwe.
    </p>
    <br>
    <p style='font-size: 18px; line-height: 1.6;'>
    <b>PROJECT FOCUS:</b> Real-Time Monitoring | Energy Analytics | Predictive Management | Intelligent Load Control
    </p>
    """, unsafe_allow_html=True)
  st.markdown("</div>", unsafe_allow_html=True)

if auto_refresh:
  time.sleep(2)
  st.rerun()
