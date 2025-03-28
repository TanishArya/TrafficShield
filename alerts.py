import streamlit as st
from datetime import datetime

def check_alerts(traffic_data, threshold):
    """
    Check for potential DDoS alerts based on traffic data.
    
    Args:
        traffic_data (dict): Dictionary with current traffic metrics
        threshold (int): Request threshold for alerting
        
    Returns:
        list: List of alert dictionaries
    """
    alerts = []
    
    # Check for high total request rate
    if traffic_data['total_requests_per_minute'] > threshold * 3:
        alerts.append({
            'timestamp': datetime.now(),
            'type': 'critical',
            'message': f"CRITICAL: Extremely high traffic volume detected ({traffic_data['total_requests_per_minute']} requests/min)",
            'ip': 'multiple'
        })
    
    # Check for individual high-traffic IPs
    for ip, requests in traffic_data['ip_requests'].items():
        if requests > threshold:
            alerts.append({
                'timestamp': datetime.now(),
                'type': 'warning' if requests < threshold * 2 else 'critical',
                'message': f"{'WARNING' if requests < threshold * 2 else 'CRITICAL'}: High traffic from {ip} ({requests} requests/min)",
                'ip': ip
            })
    
    return alerts

def display_alerts(alerts):
    """
    Display alerts in the Streamlit UI.
    
    Args:
        alerts (list): List of alert dictionaries
    """
    if not alerts:
        return
    
    # Sort alerts by timestamp (newest first)
    sorted_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    
    # Display alert count
    st.warning(f"⚠️ {len(sorted_alerts)} active alerts")
    
    # Display alerts in an expander
    with st.expander("View Active Alerts"):
        for i, alert in enumerate(sorted_alerts):
            # Set color based on alert type
            if alert['type'] == 'critical':
                color = "#FF5630"  # red
            else:  # warning
                color = "#FFAB00"  # amber
            
            # Format timestamp
            timestamp_str = alert['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Create alert message with styling
            message = f"<div style='padding: 10px; margin-bottom: 10px; border-left: 4px solid {color};'>"
            message += f"<strong>{timestamp_str}</strong><br>"
            message += f"{alert['message']}<br>"
            message += f"IP: {alert['ip']}"
            message += "</div>"
            
            st.markdown(message, unsafe_allow_html=True)
            
            # Add dismiss button for each alert
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button(f"Dismiss", key=f"dismiss_{i}"):
                    st.session_state.alerts.remove(alert)
                    st.rerun()
