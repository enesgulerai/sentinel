import streamlit as st
import requests
import time
import json
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Sentinel ML | Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Deep Navy Blue Background and General Font */
    .stApp {
        background-color: #0A0E17; 
        color: #E2E8F0;
    }
    /* Button Design - Burgundy/Dark Red Tones */
    .stButton>button {
        background-color: #5E1A24; 
        color: #F8F9FA;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #8B2635;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(139, 38, 53, 0.4);
    }
    /* Design of Metric (Speed/Result) Charts */
    div[data-testid="stMetricValue"] {
        color: #F8F9FA;
    }
    div[data-testid="stMetricLabel"] {
        color: #8B949E;
    }
    /* JSON Editor Background */
    .stTextArea textarea {
        background-color: #161B22;
        color: #58A6FF;
        border: 1px solid #30363D;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/transactions")

# --- Default Test Payload ---
DEFAULT_PAYLOAD = {
    "Time": 406.0,
    "V1": -2.312226542,
    "V2": 1.951992011,
    "V3": -1.609850732,
    "V4": 3.997905588,
    "V5": -0.522187865,
    "V6": -1.426545319,
    "V7": -2.537387306,
    "V8": 1.391657248,
    "V9": -2.770089277,
    "V10": -2.772272145,
    "V11": 3.202033207,
    "V12": -2.899907388,
    "V13": -0.595221881,
    "V14": -4.289253782,
    "V15": 0.38972412,
    "V16": -1.14074718,
    "V17": -2.830055675,
    "V18": -0.016822468,
    "V19": 0.416955705,
    "V20": 0.126910559,
    "V21": 0.517232371,
    "V22": -0.035049369,
    "V23": -0.465211076,
    "V24": 0.320198199,
    "V25": 0.044519167,
    "V26": 0.177839798,
    "V27": 0.261145003,
    "V28": -0.143275875,
    "Amount": 1500.0
}

# --- UI Layout ---
col_main, col_info = st.columns([2, 1], gap="large")

with col_main:
    st.title("🛡️ Sentinel Gateway")
    st.markdown("Real-time Fraud Detection Interface. Submit a payload to test the Event-Driven Pipeline.")
    
    # Payload Editörü
    payload_str = st.text_area(
        "JSON Payload:",
        value=json.dumps(DEFAULT_PAYLOAD, indent=2),
        height=400
    )

with col_info:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("💡 **Pro Tip:** Modify the 'Amount' or 'Time' slightly to bypass the Redis Lock and hit the Redpanda stream.")
    
    if st.button("🚀 Process Transaction", use_container_width=True):
        try:
            payload_data = json.loads(payload_str)
            
            start_time = time.perf_counter()
            with st.spinner("Routing..."):
                response = requests.post(API_URL, json=payload_data)
                response_data = response.json()
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            st.subheader("Gateway Response")
            
            m1, m2 = st.columns(2)
            with m1:
                st.metric(label="Latency", value=f"{elapsed_ms:.2f} ms")
            with m2:
                source = response_data.get("source", "Unknown")
                if "Redis" in source:
                    st.metric(label="Routed To", value="Redis Cache 🛡️")
                else:
                    st.metric(label="Routed To", value="Redpanda 🛣️")

            if response.status_code == 202:
                if "Redis" in source:
                    st.warning(f"**BLOCKED:** {response_data.get('message')}")
                else:
                    st.success(f"**ACCEPTED:** {response_data.get('message')}")
            else:
                st.error(f"Error: {response_data}")
                
        except json.JSONDecodeError:
            st.error("Invalid JSON format.")
        except requests.exceptions.ConnectionError:
            st.error("Connection failed. Is Uvicorn running on 127.0.0.1:8000?")