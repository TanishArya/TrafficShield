"""
This file contains utility functions for generating mock data for development purposes.
In a production environment, this would be replaced with real data from network interfaces,
firewalls, and other monitoring systems.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_ip_addresses(count=100):
    """
    Generate a list of random IP addresses.
    
    Args:
        count (int): Number of IP addresses to generate
        
    Returns:
        list: List of IP addresses
    """
    ips = []
    for _ in range(count):
        ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
        ips.append(ip)
    return ips

def generate_traffic_pattern(duration_hours=24, interval_minutes=5, attack_probability=0.2):
    """
    Generate a traffic pattern with optional DDoS attack simulation.
    
    Args:
        duration_hours (int): Duration of the traffic pattern in hours
        interval_minutes (int): Interval between data points in minutes
        attack_probability (float): Probability of simulating a DDoS attack
        
    Returns:
        pd.DataFrame: DataFrame with the generated traffic pattern
    """
    # Calculate number of data points
    num_points = (duration_hours * 60) // interval_minutes
    
    # Generate timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=duration_hours)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=num_points)
    
    # Generate base traffic with daily pattern
    # Traffic is higher during business hours and lower at night
    hour_of_day = np.array([t.hour for t in timestamps])
    day_factor = np.sin(np.pi * (hour_of_day - 6) / 12) * 0.5 + 0.5  # Higher between 6am and 6pm
    day_factor[hour_of_day < 6] = 0.2  # Low traffic between midnight and 6am
    day_factor[hour_of_day > 18] = 0.3  # Low-medium traffic between 6pm and midnight
    
    # Base traffic with random variations
    base_traffic = 100 + 50 * day_factor + np.random.normal(0, 10, num_points)
    base_traffic = np.maximum(base_traffic, 20)  # Ensure minimum traffic
    
    # Decide whether to simulate an attack
    simulate_attack = random.random() < attack_probability
    
    if simulate_attack:
        # Choose a random point for the attack
        attack_start = random.randint(num_points // 4, num_points * 3 // 4)
        attack_duration = random.randint(5, 20)  # Duration in number of data points
        attack_end = min(attack_start + attack_duration, num_points)
        
        # Generate attack traffic pattern
        attack_intensity = random.randint(3, 10)  # How many times the normal traffic
        attack_pattern = np.zeros(num_points)
        
        # Ramp up phase
        ramp_up = min(3, attack_duration // 3)
        for i in range(ramp_up):
            attack_pattern[attack_start + i] = (i + 1) / ramp_up * attack_intensity
        
        # Sustained attack phase
        attack_pattern[attack_start + ramp_up:attack_end - ramp_up] = attack_intensity
        
        # Ramp down phase
        for i in range(ramp_up):
            idx = attack_end - ramp_up + i
            if idx < num_points:
                attack_pattern[idx] = (ramp_up - i) / ramp_up * attack_intensity
        
        # Add attack traffic to base traffic
        traffic = base_traffic * (1 + attack_pattern)
    else:
        traffic = base_traffic
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'requests': np.round(traffic).astype(int)
    })
    
    return df

def generate_ip_traffic_distribution(total_requests, num_ips=30, attack_ip=None):
    """
    Generate a distribution of traffic across different IPs.
    
    Args:
        total_requests (int): Total number of requests to distribute
        num_ips (int): Number of IPs in the distribution
        attack_ip (str, optional): IP to assign most traffic to (for attack simulation)
        
    Returns:
        dict: Dictionary mapping IPs to request counts
    """
    # Generate IPs
    ips = generate_ip_addresses(num_ips)
    
    if attack_ip:
        # Add attack IP if provided
        ips.append(attack_ip)
        
        # Assign 60-80% of traffic to attack IP
        attack_traffic_ratio = random.uniform(0.6, 0.8)
        attack_traffic = int(total_requests * attack_traffic_ratio)
        normal_traffic = total_requests - attack_traffic
        
        # Distribute remaining traffic randomly among other IPs
        normal_distribution = np.random.exponential(1, len(ips) - 1)
        normal_distribution = normal_distribution / normal_distribution.sum() * normal_traffic
        
        # Create distribution dictionary
        ip_traffic = {ip: max(1, int(traffic)) for ip, traffic in zip(ips[:-1], normal_distribution)}
        ip_traffic[attack_ip] = max(1, attack_traffic)
    else:
        # For normal traffic, use Zipf distribution (few IPs get most traffic)
        distribution = np.random.zipf(1.6, len(ips))
        distribution = distribution / distribution.sum() * total_requests
        
        # Create distribution dictionary
        ip_traffic = {ip: max(1, int(traffic)) for ip, traffic in zip(ips, distribution)}
    
    return ip_traffic

def generate_ddos_simulation():
    """
    Generate a complete DDoS attack simulation dataset.
    
    Returns:
        tuple: (traffic_pattern, ip_distributions, alerts)
    """
    # Generate overall traffic pattern
    traffic_pattern = generate_traffic_pattern(duration_hours=24, attack_probability=0.8)
    
    # Generate IP distributions for each timestamp
    ip_distributions = {}
    alerts = []
    
    # Identify potential attack periods
    is_attack = traffic_pattern['requests'] > 300  # Simple threshold for demonstration
    
    # Generate attack IPs if there's an attack
    attack_ips = generate_ip_addresses(3) if is_attack.any() else []
    
    for i, row in traffic_pattern.iterrows():
        timestamp = row['timestamp']
        requests = row['requests']
        
        # Check if this is part of an attack period
        if is_attack[i]:
            # Rotate between attack IPs for variety
            attack_ip = attack_ips[i % len(attack_ips)]
            
            # Generate distribution with attack IP getting most traffic
            ip_distributions[timestamp] = generate_ip_traffic_distribution(
                requests, 
                num_ips=25,
                attack_ip=attack_ip
            )
            
            # Generate alert if this is the start of an attack
            if i == 0 or not is_attack[i-1]:
                alerts.append({
                    'timestamp': timestamp,
                    'type': 'critical',
                    'message': f"Potential DDoS attack detected: {requests} requests/min",
                    'ip': attack_ip
                })
        else:
            # Normal traffic distribution
            ip_distributions[timestamp] = generate_ip_traffic_distribution(
                requests, 
                num_ips=20
            )
    
    return traffic_pattern, ip_distributions, alerts

# Example usage
if __name__ == "__main__":
    traffic, distributions, alerts = generate_ddos_simulation()
    print(f"Generated {len(traffic)} traffic data points")
    print(f"Generated {len(alerts)} alerts")
    print(f"Sample traffic pattern:\n{traffic.head()}")
    sample_timestamp = traffic['timestamp'].iloc[0]
    print(f"Sample IP distribution at {sample_timestamp}:\n{distributions[sample_timestamp]}")
