"""
Hong Kong MTR Analytics Dashboard
An interactive dashboard exploring Hong Kong's MTR system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Page config
st.set_page_config(
    page_title="Hong Kong MTR Dashboard",
    page_icon="🚇",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    stations = pd.read_csv('processed_stations.csv')
    ridership = pd.read_csv('processed_ridership.csv')
    line_stats = pd.read_csv('processed_line_stats.csv')
    fares = pd.read_csv('mtr_lines_fares.csv', encoding='utf-8-sig')

    with open('summary_stats.json', 'r') as f:
        summary = json.load(f)

    return stations, ridership, line_stats, fares, summary

stations, ridership, line_stats, fares, summary = load_data()

# Header
st.title("🚇 Hong Kong MTR Analytics Dashboard")
st.markdown("*Exploring Hong Kong's Mass Transit Railway system through data*")
st.markdown("---")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Stations", f"{summary['total_stations']}")

with col2:
    st.metric("MTR Lines", f"{summary['total_lines']}")

with col3:
    st.metric("Avg Fare", f"${summary['fare_stats']['avg']:.2f}")

with col4:
    # Fix the ridership display - it's in thousands, so divide by 1000 for millions
    daily_ridership = ridership[ridership['Year'] == ridership['Year'].max()]['Daily_Ridership_Thousands'].values[0] / 1000
    st.metric("Daily Ridership (2024)", f"{daily_ridership:.1f}M")

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["📊 Network Overview", "💰 Fare Calculator", "📈 Ridership Trends", "♿ Accessibility"])

# TAB 1: Network Overview
with tab1:
    st.header("MTR Network Overview")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Stations per Line")

        # Bar chart of stations per line
        fig = px.bar(
            line_stats.sort_values('Station_Count', ascending=True),
            x='Station_Count',
            y='Line_Name',
            orientation='h',
            color='Station_Count',
            color_continuous_scale='viridis',
            labels={'Station_Count': 'Number of Stations', 'Line_Name': 'MTR Line'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Line Distribution")

        # Pie chart
        fig = px.pie(
            line_stats,
            values='Station_Count',
            names='Line_Name',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Station list
    st.subheader("All MTR Stations")

    # Group by line for display
    selected_line = st.selectbox("Filter by line:", ['All Lines'] + sorted(line_stats['Line_Name'].tolist()))

    if selected_line == 'All Lines':
        display_stations = stations.sort_values('English Name')
    else:
        line_code = line_stats[line_stats['Line_Name'] == selected_line]['Line_Code'].values[0]
        display_stations = stations[stations['Line Code'] == line_code].sort_values('English Name')

    # Display in columns
    cols = st.columns(3)
    stations_per_col = len(display_stations) // 3 + 1

    for idx, (_, station) in enumerate(display_stations.iterrows()):
        col_idx = idx % 3
        with cols[col_idx]:
            st.write(f"**{station['English Name']}** ({station['Chinese Name']})")

# TAB 2: Fare Calculator
with tab2:
    st.header("💰 MTR Fare Calculator")

    col1, col2 = st.columns(2)

    # Get station lists for dropdowns
    station_names = sorted(fares['SRC_STATION_NAME'].unique())

    with col1:
        origin = st.selectbox("Origin Station:", station_names, key='origin')

    with col2:
        destination = st.selectbox("Destination Station:", station_names, key='dest')

    if origin and destination:
        # Look up fare
        fare_row = fares[
            (fares['SRC_STATION_NAME'] == origin) &
            (fares['DEST_STATION_NAME'] == destination)
        ]

        if not fare_row.empty:
            st.success("### Fare Information")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Adult (Octopus)", f"${fare_row['OCT_ADT_FARE'].values[0]:.1f}")

            with col2:
                st.metric("Student (Octopus)", f"${fare_row['OCT_STD_FARE'].values[0]:.1f}")

            with col3:
                st.metric("Child (Octopus)", f"${fare_row['OCT_CON_CHILD_FARE'].values[0]:.1f}")

            st.info(f"**Single Journey Ticket:** ${fare_row['SINGLE_ADT_FARE'].values[0]:.1f}")
        else:
            st.warning("No direct route found between these stations.")

# TAB 3: Ridership Trends
with tab3:
    st.header("📈 Public Transport Ridership Trends")
    st.info("Note: Data shows overall public transport ridership (MTR, buses, trams, etc.)")

    # Fix ridership data - convert thousands to millions
    ridership['Daily_Ridership_Millions'] = ridership['Daily_Ridership_Thousands'] / 1000

    # Line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=ridership['Year'],
        y=ridership['Daily_Ridership_Millions'],
        mode='lines+markers',
        name='Daily Ridership',
        line=dict(color='#2E86C1', width=3),
        marker=dict(size=8)
    ))

    # Add annotation for COVID
    fig.add_annotation(
        x=2020,
        y=ridership[ridership['Year']==2020]['Daily_Ridership_Millions'].values[0],
        text="COVID-19 Impact",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#E74C3C",
        font=dict(color="#E74C3C")
    )

    fig.update_layout(
        title="Hong Kong Public Transport - Average Daily Ridership (2014-2024)",
        xaxis_title="Year",
        yaxis_title="Daily Ridership (Millions)",
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        pre_covid = ridership[ridership['Year'] == 2019]['Daily_Ridership_Millions'].values[0]
        st.metric("Pre-COVID (2019)", f"{pre_covid:.2f}M")

    with col2:
        covid_low = ridership[ridership['Year'] == 2020]['Daily_Ridership_Millions'].values[0]
        change = ((covid_low - pre_covid) / pre_covid) * 100
        st.metric("COVID Low (2020)", f"{covid_low:.2f}M", f"{change:.1f}%")

    with col3:
        latest = ridership[ridership['Year'] == 2024]['Daily_Ridership_Millions'].values[0]
        recovery = ((latest - covid_low) / (pre_covid - covid_low)) * 100
        st.metric("Latest (2024)", f"{latest:.2f}M", f"{recovery:.0f}% recovered")

# TAB 4: Accessibility
with tab4:
    st.header("♿ Accessibility Information")

    st.info(f"**{summary['total_accessibility_records']:,}** barrier-free facility records across the MTR network")

    st.markdown("""
    ### Barrier-Free Facilities

    The MTR system provides various accessibility features to assist passengers with disabilities:

    - **Elevators & Escalators**: Connect platforms to street level
    - **Tactile Guide Paths**: Help visually impaired passengers navigate
    - **Wheelchair Accessible Toilets**: Available at major stations
    - **Braille & Audio Information**: At ticket machines and platforms
    - **Wide Gates**: For wheelchair and stroller access
    - **Priority Seating**: Designated areas in every train car

    All MTR stations are designed to be barrier-free, ensuring accessibility for all passengers.
    """)

    st.success("✅ All 100+ MTR stations feature barrier-free access")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>Data Source: DATA.GOV.HK | Transport Department Hong Kong</p>
    <p>Dashboard created by Alek Swiderski | December 2024</p>
</div>
""", unsafe_allow_html=True)
