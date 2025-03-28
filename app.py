import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import datetime, timedelta
import time



from data_processor import (
    get_current_traffic_data,
    get_historical_traffic_data,
    get_ip_status_data,
    get_traffic_anomalies,
    get_logs,
)
from visualizations import (
    create_traffic_heatmap,
    create_traffic_line_chart,
    create_request_distribution_chart,
    create_anomaly_chart,
    create_ip_status_chart,
)
from alerts import check_alerts, display_alerts

# Page configuration
st.set_page_config(
    page_title="DDoS Attack Detection & Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for settings and alerts
if "alert_threshold" not in st.session_state:
    st.session_state.alert_threshold = 100
if "time_window" not in st.session_state:
    st.session_state.time_window = 60  # seconds
if "block_duration" not in st.session_state:
    st.session_state.block_duration = 60  # minutes
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Sidebar
with st.sidebar:
    st.title("DDoS Protection Dashboard")
    st.markdown("---")
    
    st.subheader("Settings")
    st.session_state.alert_threshold = st.slider(
        "Alert Threshold (requests/min)", 
        min_value=10, 
        max_value=500, 
        value=st.session_state.alert_threshold,
        step=10
    )
    
    st.session_state.time_window = st.slider(
        "Monitoring Window (seconds)", 
        min_value=10, 
        max_value=300, 
        value=st.session_state.time_window,
        step=10
    )
    
    st.session_state.block_duration = st.slider(
        "Block Duration (minutes)", 
        min_value=5, 
        max_value=240, 
        value=st.session_state.block_duration,
        step=5
    )
    
    st.session_state.dark_mode = st.toggle("Dark Mode", st.session_state.dark_mode)
    
    st.markdown("---")
    
    if st.button("Clear All Alerts"):
        st.session_state.alerts = []
        st.success("Alerts cleared")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This dashboard helps network administrators detect and monitor potential DDoS attacks 
    by analyzing traffic patterns and providing real-time alerts.
    """)

# Main content
st.title("🛡️ DDoS Attack Detection & Monitoring")

# Create tabs for different dashboard sections
tab1, tab2, tab3, tab4 = st.tabs([
    "Live Monitoring", 
    "Traffic Analysis", 
    "IP Management", 
    "Logs & History"
])

with tab1:
    st.header("Real-Time Traffic Monitoring")
    
    # Current traffic metrics
    traffic_data = get_current_traffic_data()
    
    # Layout for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Requests/min", 
            f"{traffic_data['total_requests_per_minute']:,}",
            delta=f"{traffic_data['request_change']}%"
        )
    
    with col2:
        st.metric(
            "Unique IPs", 
            traffic_data['unique_ips'],
            delta=traffic_data['ip_change']
        )
    
    with col3:
        st.metric(
            "Blocked IPs", 
            traffic_data['blocked_ips'],
            delta=traffic_data['blocked_change']
        )
    
    with col4:
        st.metric(
            "Suspicious IPs", 
            traffic_data['suspicious_ips'],
            delta=traffic_data['suspicious_change'],
            delta_color="inverse"
        )
    
    # Check for alerts
    alerts = check_alerts(traffic_data, st.session_state.alert_threshold)
    if alerts:
        for alert in alerts:
            if alert not in st.session_state.alerts:
                st.session_state.alerts.append(alert)
    
    # Display alerts
    display_alerts(st.session_state.alerts)
    
    # Print the IP requests data for debugging
    if 'ip_requests' in traffic_data:
        print("IP Requests Data:", traffic_data['ip_requests'])
    else:
        print("IP Requests Data is missing.")
    
    # Traffic visualization
    st.subheader("Current Traffic Pattern")
    historical_data = get_historical_traffic_data(minutes=30)
    if historical_data.empty:
        st.warning("No historical traffic data available.")
    else:
        traffic_chart = create_traffic_line_chart(historical_data)
        st.plotly_chart(traffic_chart, use_container_width=True)
    
    # Traffic heatmap
    st.subheader("Request Rate by IP (Heatmap)")
    if 'ip_requests' in traffic_data and traffic_data['ip_requests']:
        heatmap = create_traffic_heatmap(traffic_data['ip_requests'])
        st.plotly_chart(heatmap, use_container_width=True)
    else:
        st.warning("No IP request data available for heatmap.")

with tab2:
    st.header("Traffic Pattern Analysis")
    
    # Time range selector
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 30 minutes", "Last hour", "Last 6 hours", "Last 24 hours", "Last 7 days"]
    )
    
    time_ranges = {
        "Last 30 minutes": 30,
        "Last hour": 60,
        "Last 6 hours": 360,
        "Last 24 hours": 1440,
        "Last 7 days": 10080
    }
    
    minutes = time_ranges[time_range]
    historical_data = get_historical_traffic_data(minutes=minutes)
    
    # Traffic over time
    st.subheader("Traffic Volume Over Time")
    traffic_chart = create_traffic_line_chart(historical_data)
    st.plotly_chart(traffic_chart, use_container_width=True)
    
    # Request distribution
    st.subheader("Request Distribution by IP")
    distribution_chart = create_request_distribution_chart(historical_data)
    st.plotly_chart(distribution_chart, use_container_width=True)
    
    # Anomaly detection
    st.subheader("Traffic Anomalies")
    anomalies = get_traffic_anomalies(minutes=minutes)
    if anomalies.empty:
        st.info("No anomalies detected in the selected time range.")
    else:
        anomaly_chart = create_anomaly_chart(anomalies, historical_data)
        st.plotly_chart(anomaly_chart, use_container_width=True)
        
        # Anomaly details
        with st.expander("View Anomaly Details"):
            st.dataframe(anomalies)

with tab3:
    st.header("IP Management")
    
    # IP status overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("IP Status Overview")
        ip_status_data = get_ip_status_data()
        ip_chart = create_ip_status_chart(ip_status_data)
        st.plotly_chart(ip_chart, use_container_width=True)
    
    with col2:
        st.subheader("IP Actions")
        
        # Add to whitelist
        with st.form("whitelist_form"):
            whitelist_ip = st.text_input("Add IP to Whitelist")
            submit_whitelist = st.form_submit_button("Add to Whitelist")
            if submit_whitelist and whitelist_ip:
                st.success(f"Added {whitelist_ip} to whitelist!")
        
        # Manual block
        with st.form("block_form"):
            block_ip = st.text_input("Block IP Address")
            submit_block = st.form_submit_button("Block IP")
            if submit_block and block_ip:
                st.success(f"Blocked {block_ip}!")
    
    # IP status tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Currently Blocked IPs")
        blocked_ips = pd.DataFrame({
            "IP Address": ip_status_data[ip_status_data["status"] == "blocked"]["ip"],
            "Blocked Since": [datetime.now() - timedelta(minutes=np.random.randint(1, st.session_state.block_duration)) for _ in range(sum(ip_status_data["status"] == "blocked"))],
            "Reason": ["Exceeded threshold"] * sum(ip_status_data["status"] == "blocked"),
        })
        
        if blocked_ips.empty:
            st.info("No IPs are currently blocked.")
        else:
            blocked_ips["Time Remaining"] = [(st.session_state.block_duration - (datetime.now() - t).total_seconds() / 60) for t in blocked_ips["Blocked Since"]]
            blocked_ips["Time Remaining"] = blocked_ips["Time Remaining"].apply(lambda x: f"{int(x)} minutes")
            blocked_ips["Blocked Since"] = blocked_ips["Blocked Since"].dt.strftime("%H:%M:%S")
            st.dataframe(blocked_ips, use_container_width=True)
    
    with col2:
        st.subheader("Whitelisted IPs")
        whitelisted_ips = pd.DataFrame({
            "IP Address": ip_status_data[ip_status_data["status"] == "whitelisted"]["ip"],
            "Added On": [datetime.now() - timedelta(days=np.random.randint(1, 30)) for _ in range(sum(ip_status_data["status"] == "whitelisted"))],
            "Added By": ["Admin"] * sum(ip_status_data["status"] == "whitelisted"),
        })
        
        if whitelisted_ips.empty:
            st.info("No IPs are currently whitelisted.")
        else:
            whitelisted_ips["Added On"] = whitelisted_ips["Added On"].dt.strftime("%Y-%m-%d")
            st.dataframe(whitelisted_ips, use_container_width=True)

with tab4:
    st.header("Traffic Logs & History")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Get logs
    logs = get_logs(start_date, end_date)
    
    # Log filtering
    log_filter = st.multiselect(
        "Filter by Log Type",
        options=["info", "warning", "error", "block", "unblock"],
        default=["warning", "error", "block"]
    )
    
    filtered_logs = logs[logs["type"].isin(log_filter)]
    
    # Display logs
    st.subheader("System Logs")
    if filtered_logs.empty:
        st.info("No logs found for the selected filters.")
    else:
        # Add custom styling to logs
        def highlight_log_type(val):
            color_map = {
                "info": "blue",
                "warning": "orange",
                "error": "red",
                "block": "darkred",
                "unblock": "green"
            }
            return f"background-color: {color_map.get(val, 'white')}"
        
        st.dataframe(filtered_logs.style.applymap(
            highlight_log_type, subset=["type"]), 
            use_container_width=True
        )
    
    # Download logs
    csv = filtered_logs.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Filtered Logs",
        csv,
        "ddos_protection_logs.csv",
        "text/csv",
        key='download-logs'
    )
    
    # Attack history
    st.subheader("Attack History")
    attack_history = pd.DataFrame({
        "Date": pd.date_range(end=datetime.now(), periods=5, freq="-1D"),
        "Duration (minutes)": np.random.randint(5, 60, 5),
        "Peak Traffic (req/s)": np.random.randint(500, 5000, 5),
        "Blocked IPs": np.random.randint(5, 50, 5),
        "Attack Type": np.random.choice(["TCP Flood", "UDP Flood", "HTTP Flood", "DNS Amplification", "SYN Flood"], 5)
    })
    
    attack_history["Date"] = attack_history["Date"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(attack_history, use_container_width=True)

# Auto-refresh the data (every 30 seconds)
auto_refresh = st.empty()
with auto_refresh.container():
    refresh = st.checkbox("Auto-refresh data (every 30 seconds)", value=True)

if refresh:
    time.sleep(30)
    st.rerun()
