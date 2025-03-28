import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_current_traffic_data():
    """
    Generate current traffic metrics for the DDoS monitoring dashboard.
    
    Returns:
        dict: Dictionary containing current traffic statistics.
    """
    # Generate a list of random IPs
    ips = [f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}" for _ in range(50)]
    
    # Generate random request counts for IPs, making some IPs have much higher request counts
    request_counts = []
    for _ in range(50):
        if np.random.random() < 0.1:  # 10% chance of high traffic (potential DDoS)
            request_counts.append(np.random.randint(80, 500))
        else:
            request_counts.append(np.random.randint(1, 80))
    
    # Create a dictionary mapping IPs to request counts
    ip_requests = dict(zip(ips, request_counts))
    
    # Determine blocked and suspicious IPs
    blocked_ips = sum(1 for count in request_counts if count > 200)
    suspicious_ips = sum(1 for count in request_counts if 100 < count <= 200)
    
    # Generate changes from "previous period" for delta indicators
    return {
        'total_requests_per_minute': sum(request_counts),
        'unique_ips': len(ips),
        'blocked_ips': blocked_ips,
        'suspicious_ips': suspicious_ips,
        'request_change': np.random.randint(-15, 25),
        'ip_change': np.random.randint(-5, 15),
        'blocked_change': np.random.randint(-3, 10),
        'suspicious_change': np.random.randint(-8, 20),
        'ip_requests': ip_requests
    }

def get_historical_traffic_data(minutes=60):
    """
    Generate historical traffic data for the given time period.
    
    Args:
        minutes (int): Number of minutes of historical data to generate
        
    Returns:
        pd.DataFrame: DataFrame with historical traffic data
    """
    # Generate time points
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=minutes)
    time_points = pd.date_range(start=start_time, end=end_time, freq='1min')
    
    # Generate random IPs
    all_ips = [f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}" for _ in range(30)]
    
    # Create data for the historical view
    data = []
    
    # Base traffic pattern with some randomness
    base_traffic = np.sin(np.linspace(0, minutes/10, len(time_points))) * 50 + 100
    
    # Add a "spike" to simulate a potential DDoS attack
    attack_point = np.random.randint(len(time_points) // 3, len(time_points) * 2 // 3)
    attack_duration = np.random.randint(5, 15)  # attack duration in minutes
    
    for i, time_point in enumerate(time_points):
        # Add randomness to base traffic
        traffic = int(base_traffic[i] + np.random.randint(-20, 20))
        
        # Add traffic spike for DDoS simulation
        if attack_point <= i < attack_point + attack_duration:
            # Intensity increases and then decreases
            distance_from_peak = min(i - attack_point, attack_point + attack_duration - i)
            intensity_factor = 1 - (distance_from_peak / attack_duration)
            traffic += int(np.random.randint(200, 500) * intensity_factor)
        
        # Distribute traffic among random IPs
        ip_count = min(np.random.randint(5, 20), len(all_ips))
        selected_ips = np.random.choice(all_ips, ip_count, replace=False)
        
        # Normal IP distribution
        normal_ips = selected_ips[:-3] if len(selected_ips) > 3 else selected_ips
        normal_traffic = np.random.multinomial(max(traffic - 100, 0), 
                                              np.ones(len(normal_ips))/len(normal_ips)) if len(normal_ips) > 0 else []
        
        # If in attack period, give most traffic to a few IPs
        if attack_point <= i < attack_point + attack_duration and len(selected_ips) > 3:
            attack_ips = selected_ips[-3:]
            attack_traffic = np.random.multinomial(100 + np.random.randint(0, 300), 
                                                 [0.7, 0.2, 0.1])  # Attack IPs get more traffic
            
            for j, ip in enumerate(normal_ips):
                data.append({
                    'timestamp': time_point,
                    'ip': ip,
                    'requests': int(normal_traffic[j])
                })
            
            for j, ip in enumerate(attack_ips):
                data.append({
                    'timestamp': time_point,
                    'ip': ip,
                    'requests': int(attack_traffic[j])
                })
        else:
            # Normal distribution
            ip_traffic = np.random.multinomial(traffic, np.ones(ip_count)/ip_count)
            for j, ip in enumerate(selected_ips):
                data.append({
                    'timestamp': time_point,
                    'ip': ip,
                    'requests': int(ip_traffic[j])
                })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

def get_ip_status_data():
    """
    Generate data about IP statuses (blocked, whitelisted, normal).
    
    Returns:
        pd.DataFrame: DataFrame with IP status information
    """
    # Generate a list of random IPs
    ips = [f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}" for _ in range(100)]
    
    # Assign statuses
    statuses = np.random.choice(
        ["normal", "blocked", "whitelisted", "suspicious"], 
        size=100, 
        p=[0.7, 0.15, 0.1, 0.05]  # 70% normal, 15% blocked, 10% whitelisted, 5% suspicious
    )
    
    # Create request counts (blocked and suspicious IPs have higher request counts)
    request_counts = []
    for status in statuses:
        if status == "blocked":
            request_counts.append(np.random.randint(200, 500))
        elif status == "suspicious":
            request_counts.append(np.random.randint(100, 200))
        elif status == "normal":
            request_counts.append(np.random.randint(1, 100))
        else:  # whitelisted
            request_counts.append(np.random.randint(1, 300))  # can have any request count
    
    # Create DataFrame
    df = pd.DataFrame({
        "ip": ips,
        "status": statuses,
        "requests": request_counts
    })
    
    return df

def get_traffic_anomalies(minutes=60):
    """
    Generate data about traffic anomalies.
    
    Args:
        minutes (int): Number of minutes of anomaly data to generate
        
    Returns:
        pd.DataFrame: DataFrame with anomaly information
    """
    # Generate time points with some anomalies
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=minutes)
    
    # Number of anomalies to generate
    anomaly_count = max(1, minutes // 30)  # At least one anomaly, more for longer periods
    
    if np.random.random() < 0.1:  # 10% chance of no anomalies
        return pd.DataFrame(columns=["timestamp", "ip", "requests", "expected_requests", "ratio"])
    
    # Generate anomaly data
    anomalies = []
    for _ in range(anomaly_count):
        # Randomize when the anomaly occurred
        anomaly_time = start_time + timedelta(minutes=np.random.randint(0, minutes))
        
        # Generate a random IP
        ip = f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}"
        
        # Generate anomaly metrics
        expected_requests = np.random.randint(10, 50)  # Normal expected traffic
        actual_requests = expected_requests * np.random.randint(5, 20)  # 5-20x higher than expected
        ratio = actual_requests / expected_requests
        
        anomalies.append({
            "timestamp": anomaly_time,
            "ip": ip,
            "requests": actual_requests,
            "expected_requests": expected_requests,
            "ratio": ratio
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(anomalies)
    
    return df

def get_logs(start_date, end_date):
    """
    Generate system logs for the date range.
    
    Args:
        start_date: Start date for logs
        end_date: End date for logs
        
    Returns:
        pd.DataFrame: DataFrame with log entries
    """
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Calculate number of log entries (more entries for longer periods)
    days_diff = (end_datetime - start_datetime).days + 1
    log_count = days_diff * np.random.randint(20, 50)
    
    # Generate random timestamps within the date range
    timestamps = [start_datetime + timedelta(
        seconds=np.random.randint(0, int((end_datetime - start_datetime).total_seconds()))
    ) for _ in range(log_count)]
    timestamps.sort()  # Sort chronologically
    
    # Log types and messages
    log_types = np.random.choice(
        ["info", "warning", "error", "block", "unblock"],
        size=log_count,
        p=[0.5, 0.2, 0.1, 0.15, 0.05]  # 50% info, 20% warning, 10% error, 15% block, 5% unblock
    )
    
    # Generate IP addresses
    ips = [f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}" for _ in range(log_count)]
    
    # Generate log messages
    messages = []
    for i in range(log_count):
        log_type = log_types[i]
        ip = ips[i]
        
        if log_type == "info":
            messages.append(f"Normal traffic from {ip}: {np.random.randint(1, 50)} requests/min")
        elif log_type == "warning":
            messages.append(f"Unusual traffic spike from {ip}: {np.random.randint(50, 100)} requests/min")
        elif log_type == "error":
            messages.append(f"Potential DDoS attack detected from {ip}: {np.random.randint(100, 500)} requests/min")
        elif log_type == "block":
            messages.append(f"IP {ip} automatically blocked: Exceeded threshold with {np.random.randint(100, 500)} requests/min")
        else:  # unblock
            messages.append(f"IP {ip} automatically unblocked: Block duration expired")
    
    # Create DataFrame
    df = pd.DataFrame({
        "timestamp": timestamps,
        "type": log_types,
        "ip": ips,
        "message": messages
    })
    
    # Sort by timestamp descending (newest first)
    df = df.sort_values("timestamp", ascending=False)
    
    return df
