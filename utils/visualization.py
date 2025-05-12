import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_spark_meter(level):
    """Create a custom spark meter visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=level,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Spark Meter"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkred"},
            'bar': {'color': "#F4436C"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#B4B4B4",
            'steps': [
                {'range': [0, 30], 'color': '#0C7489'},
                {'range': [30, 70], 'color': '#533278'},
                {'range': [70, 100], 'color': '#F4436C'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': level
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        font={'color': "#333333", 'family': "Arial"}
    )
    
    return fig

def create_category_completion_chart(category_stats):
    """Create a bar chart showing completion by category"""
    if not category_stats:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(category_stats)
    
    # Create horizontal bar chart
    fig = px.bar(
        df,
        y="category",
        x="percentage",
        orientation='h',
        labels={"percentage": "Completion (%)", "category": "Category"},
        color="percentage",
        color_continuous_scale=["#0C7489", "#533278", "#B4B4B4", "#F4436C"],
        range_color=[0, 100],
        text=df.apply(lambda row: f"{int(row['completed'])}/{int(row['total'])}", axis=1)
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        font={'color': "#333333", 'family': "Arial"},
        showlegend=False,
        coloraxis_showscale=False
    )
    
    fig.update_traces(textposition='inside')
    
    return fig

def create_streak_calendar(streak_days=None):
    """Create a calendar heatmap showing activity streak"""
    # Generate example data if none provided
    if streak_days is None:
        # Use user streak from session state
        streak = st.session_state.user_progress["streak"]
        streak_days = []
        
        # If there's a streak, add days
        if streak > 0:
            today = datetime.now().date()
            for i in range(streak):
                streak_days.append(today - timedelta(days=i))
    
    # Create date range for the past 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Create dataframe with activity counts
    df = pd.DataFrame({"date": date_range})
    df["completed"] = df["date"].apply(lambda x: 1 if x.date() in streak_days else 0)
    df["weekday"] = df["date"].dt.day_name().str[:3]
    df["day"] = df["date"].dt.day
    df["week"] = df["date"].dt.isocalendar().week
    
    # Create heatmap
    fig = px.imshow(
        df.pivot_table(index="weekday", columns="day", values="completed", aggfunc="sum"),
        color_continuous_scale=["#F8F8F8", "#F4436C"],
        labels=dict(x="Day of Month", y="Day of Week", color="Activity"),
        range_color=[0, 1]
    )
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=30, b=10),
        font={'color': "#333333", 'family': "Arial"},
        coloraxis_showscale=False
    )
    
    return fig

def display_badges(badges):
    """Display user earned badges in a visually appealing grid"""
    if not badges:
        st.info("Complete challenges to earn badges!")
        return
    
    # Create 3 columns for badges
    cols = st.columns(3)
    
    # Badge emoji mapping
    badge_emojis = {
        "First Spark": "✨",
        "Flame Starter": "🔥",
        "Burning Bright": "🌟",
        "Inferno": "💥",
        "3 Day Streak": "🔄",
        "1 Week Connection": "📅",
        "2 Week Devotion": "💪",
        "Monthly Passion": "🏆"
    }
    
    # Display badges in columns
    for i, badge in enumerate(badges):
        col_idx = i % 3
        emoji = badge_emojis.get(badge, "🏅")
        cols[col_idx].markdown(f"""
        <div style='text-align: center; padding: 10px; margin: 5px; border-radius: 10px; background-color: #f0f0f0; border: 2px solid #533278;'>
            <div style='font-size: 24px;'>{emoji}</div>
            <div style='font-weight: bold; color: #533278;'>{badge}</div>
        </div>
        """, unsafe_allow_html=True)
