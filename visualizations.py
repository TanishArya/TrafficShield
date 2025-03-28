import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt

def create_traffic_line_chart(df):
    """
    Create a line chart of traffic volume over time.
    
    Args:
        df (pd.DataFrame): DataFrame with traffic data including 'timestamp' and 'requests'
        
    Returns:
        plotly.graph_objects.Figure: Line chart figure
    """
    # Aggregate requests by timestamp
    traffic_by_time = df.groupby('timestamp')['requests'].sum().reset_index()
    
    # Create line chart
    fig = px.line(
        traffic_by_time, 
        x='timestamp', 
        y='requests',
        title='Traffic Volume Over Time',
        labels={'timestamp': 'Time', 'requests': 'Requests per Minute'},
    )
    
    # Add threshold line
    fig.add_hline(
        y=200, 
        line_dash="dash", 
        line_color="#FF5630",
        annotation_text="Alert Threshold",
        annotation_position="bottom right"
    )
    
    # Style the chart
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Requests per Minute",
        hovermode="x unified",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0.02)',
    )
    
    # Add range selector
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5m", step="minute", stepmode="backward"),
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=30, label="30m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def create_traffic_heatmap(data):
    """
    Create a heatmap showing request counts by IP.
    
    Args:
        data (dict): Dictionary mapping IP addresses to request counts.
        
    Returns:
        plotly.graph_objects.Figure: Heatmap figure.
    """
    if not isinstance(data, dict):
        raise TypeError("Expected a dictionary for IP requests data.")
    
    # Convert the dictionary to a format suitable for heatmap
    ip_addresses = list(data.keys())
    request_counts = list(data.values())
    
    # Create a heatmap using the request counts
    fig = go.Figure(data=go.Heatmap(
        z=[request_counts],
        x=ip_addresses,
        y=['Requests'],
        colorscale='Viridis'
    ))
    
    # Style the heatmap
    fig.update_layout(
        title='Request Rate by IP',
        xaxis_title='IP Address',
        yaxis_title='Requests',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='rgba(0,0,0,0.02)',
    )
    
    return fig

def create_request_distribution_chart(df):
    """
    Create a chart showing request distribution across IPs.
    
    Args:
        df (pd.DataFrame): DataFrame with traffic data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Aggregate requests by IP
    requests_by_ip = df.groupby('ip')['requests'].sum().reset_index()
    
    # Sort by request count descending
    requests_by_ip = requests_by_ip.sort_values('requests', ascending=False)
    
    # Take top 15 IPs
    top_ips = requests_by_ip.head(15)
    
    # Create a function to determine color based on request count
    def get_color(count):
        if count > 200:
            return "#FF5630"  # red
        elif count > 100:
            return "#FFAB00"  # amber
        else:
            return "#36B37E"  # green
    
    # Apply color function
    top_ips['color'] = top_ips['requests'].apply(get_color)
    
    # Create bar chart
    fig = px.bar(
        top_ips,
        x='ip',
        y='requests',
        title='Top 15 IPs by Request Count',
        color='requests',
        color_continuous_scale=[(0, "#36B37E"), (0.5, "#FFAB00"), (1, "#FF5630")],
        labels={'ip': 'IP Address', 'requests': 'Total Requests'}
    )
    
    # Style the chart
    fig.update_layout(
        xaxis_title="IP Address",
        yaxis_title="Total Requests",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='rgba(0,0,0,0.02)',
    )
    
    # Add threshold line
    fig.add_hline(
        y=200, 
        line_dash="dash", 
        line_color="#FF5630",
        annotation_text="Alert Threshold",
        annotation_position="bottom right"
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_anomaly_chart(anomalies_df, traffic_df):
    """
    Create a chart highlighting traffic anomalies.
    
    Args:
        anomalies_df (pd.DataFrame): DataFrame with anomaly data
        traffic_df (pd.DataFrame): DataFrame with general traffic data
        
    Returns:
        plotly.graph_objects.Figure: Line chart with anomalies highlighted
    """
    # Aggregate traffic by timestamp
    traffic_by_time = traffic_df.groupby('timestamp')['requests'].sum().reset_index()
    
    # Create base line chart
    fig = px.line(
        traffic_by_time, 
        x='timestamp', 
        y='requests',
        title='Traffic Anomalies',
        labels={'timestamp': 'Time', 'requests': 'Requests per Minute'},
    )
    
    # Add scatter points for anomalies
    for _, anomaly in anomalies_df.iterrows():
        # Find the closest timestamp in traffic data
        closest_time_idx = (traffic_by_time['timestamp'] - anomaly['timestamp']).abs().idxmin()
        closest_time = traffic_by_time.loc[closest_time_idx, 'timestamp']
        
        # Add marker for the anomaly
        fig.add_trace(go.Scatter(
            x=[closest_time],
            y=[traffic_by_time.loc[closest_time_idx, 'requests']],
            mode='markers',
            marker=dict(
                color='#FF5630',
                size=15,
                line=dict(width=2, color='#FF5630')
            ),
            name=f"Anomaly: {anomaly['ip']}",
            text=f"IP: {anomaly['ip']}<br>Requests: {anomaly['requests']}<br>Expected: {anomaly['expected_requests']}<br>Ratio: {anomaly['ratio']:.1f}x",
            hoverinfo="text",
            showlegend=False
        ))
    
    # Style the chart
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Requests per Minute",
        hovermode="closest",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='rgba(0,0,0,0.02)',
    )
    
    # Add range selector
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5m", step="minute", stepmode="backward"),
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=30, label="30m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def create_ip_status_chart(df):
    """
    Create a chart showing IP status distribution.
    
    Args:
        df (pd.DataFrame): DataFrame with IP status data
        
    Returns:
        plotly.graph_objects.Figure: Pie or bar chart figure
    """
    # Count IPs by status
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    # Map status to colors
    color_map = {
        'normal': '#36B37E',  # green
        'blocked': '#FF5630',  # red
        'whitelisted': '#0052CC',  # blue
        'suspicious': '#FFAB00'  # amber
    }
    
    colors = [color_map[status] for status in status_counts['status']]
    
    # Create pie chart
    fig = px.pie(
        status_counts, 
        values='count', 
        names='status',
        title='IP Status Distribution',
        color='status',
        color_discrete_map=color_map
    )
    
    # Style the chart
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Improve text visibility
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

# Example usage of the fig object
fig = go.Figure()

fig.update_layout(
    xaxis=dict(
        ticklabeloverflow='hide past domain',
        ticklabelposition='outside',
        ticklabelstep=1,
        ticklen=5,
        tickmode='auto',
        tickprefix='',
        ticks='outside',
        ticksuffix='',
        ticktext=['A', 'B', 'C'],
        ticktextsrc='source',
        tickvals=[1, 2, 3],
        tickvalssrc='source',
        tickwidth=2,
        title=dict(
            text='Axis Title',
            font=dict(
                family='Arial, sans-serif',
                size=12,
                color='black'
            ),
            standoff=15
        )
    )
)

fig.show()
