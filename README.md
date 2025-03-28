# DDoS Attack Detection & Monitoring Dashboard

A web-based dashboard for real-time monitoring, visualization, and analysis of network traffic to detect and respond to potential DDoS attacks.

![DDoS Dashboard](https://img.shields.io/badge/DDoS-Dashboard-0052CC)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B)
![Python](https://img.shields.io/badge/Python-3.11-blue)

## 🛡️ Overview

This dashboard helps network administrators detect and monitor potential DDoS attacks by analyzing traffic patterns and providing real-time alerts. The system visualizes traffic data, identifies anomalies, and facilitates IP management for protection against distributed denial-of-service attacks.

## 📊 Key Features

### Real-Time Monitoring
- Live traffic metrics including total requests per minute, unique IPs, blocked IPs, and suspicious IPs
- Visual representation of current traffic patterns
- Request rate heatmap by IP address

### Traffic Analysis
- Historical traffic data visualization with customizable time ranges
- Request distribution analysis by IP
- Anomaly detection with detailed insights

### IP Management
- IP status overview (normal, blocked, whitelisted, suspicious)
- Ability to whitelist trusted IPs
- Manual IP blocking capability
- View currently blocked and whitelisted IPs

### Logs & History
- Comprehensive system logs with filtering capabilities
- Historical record of attack events
- Downloadable logs for further analysis

## 🔍 DDoS Protection Features

1. **Request Rate Monitoring**: Continuously tracks the number of requests made by each IP address within a specified time window.

2. **Traffic Anomaly Detection**: Identifies abnormal traffic patterns based on predefined thresholds.

3. **IP Blacklisting and Blocking**: Automatically blocks IP addresses that exhibit DDoS-like behavior by exceeding request thresholds.

4. **IP Whitelisting**: Allows trusted IPs to bypass rate limiting and blocking mechanisms.

5. **Rate Limiting**: Restricts the number of requests an IP can make within a short time period.

6. **Traffic Logging**: Logs the timestamps and IPs of incoming requests for monitoring and analysis.

7. **Real-Time Alerts**: Sends real-time alerts when potential DDoS attacks are detected.

8. **Automatic Unblocking**: Automatically unblocks IP addresses after a certain period or once traffic returns to normal.

9. **Customizable Thresholds**: Allows customization of request thresholds and time windows for detecting attacks.

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Streamlit
- pandas
- numpy
- plotly
- altair

These dependencies are listed in `dependencies.txt`.

### Running the Dashboard

To start the dashboard:

```bash
streamlit run app.py --server.port 5000
```

## 🎨 Theme & Styling

The dashboard uses a custom theme with the following colors:
- Primary: #0052CC (deep blue)
- Secondary: #FF5630 (alert red)
- Background: #FAFBFC (light grey)
- Text: #172B4D (dark blue)
- Success: #36B37E (green)
- Warning: #FFAB00 (amber)

## 📄 License

This project is for demonstration purposes and is not licensed for production use without proper authorization.

## 🔒 Security Note

In a production environment, this dashboard should be integrated with actual network monitoring tools, firewalls, and traffic analysis systems. The current implementation uses simulated data for demonstration purposes.