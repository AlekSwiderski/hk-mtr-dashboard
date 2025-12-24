"""
Hong Kong MTR Dashboard - Data Processor
Processes and prepares all MTR data for visualization
"""

import pandas as pd
import numpy as np
import json
import sys

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("PROCESSING HONG KONG MTR DATA")
print("=" * 70)

# 1. Process Station Data
print("\n1. Processing Station Data...")
stations_raw = pd.read_csv('mtr_lines_and_stations.csv', encoding='utf-8-sig')

# Get unique stations (remove duplicates from up/down tracks)
stations = stations_raw[['Station ID', 'Station Code', 'Chinese Name', 'English Name', 'Line Code']].drop_duplicates('Station ID')
print(f"   ✓ {len(stations)} unique stations loaded")

# Count stations per line
stations_per_line = stations_raw.groupby('Line Code')['Station ID'].nunique().sort_values(ascending=False)
print(f"   ✓ {len(stations_per_line)} MTR lines identified")

# Create line name mapping
line_names = {
    'AEL': 'Airport Express',
    'TCL': 'Tung Chung Line',
    'TKL': 'Tseung Kwan O Line',
    'EAL': 'East Rail Line',
    'TML': 'Tuen Ma Line',
    'TWL': 'Tsuen Wan Line',
    'ISL': 'Island Line',
    'KTL': 'Kwun Tong Line',
    'SIL': 'South Island Line',
    'DRL': 'Disneyland Resort Line'
}

# 2. Process Fare Data
print("\n2. Processing Fare Data...")
fares = pd.read_csv('mtr_lines_fares.csv', encoding='utf-8-sig')
print(f"   ✓ {len(fares):,} fare combinations loaded")

# Calculate fare statistics
fare_stats = {
    'min': fares['OCT_ADT_FARE'].min(),
    'max': fares['OCT_ADT_FARE'].max(),
    'avg': fares['OCT_ADT_FARE'].mean(),
    'median': fares['OCT_ADT_FARE'].median()
}
print(f"   ✓ Fare range: ${fare_stats['min']:.1f} - ${fare_stats['max']:.1f}")
print(f"   ✓ Average fare: ${fare_stats['avg']:.2f}")

# 3. Process Accessibility Data
print("\n3. Processing Accessibility Data...")
accessibility = pd.read_csv('barrier_free_facilities.csv', encoding='utf-8-sig')
print(f"   ✓ {len(accessibility):,} accessibility records loaded")

# Count facilities per station
facilities_per_station = accessibility.groupby('Station_No').size().sort_values(ascending=False)
print(f"   ✓ Top 5 most accessible stations:")
for station_no, count in facilities_per_station.head(5).items():
    print(f"     - Station {station_no}: {count} facilities")

# 4. Process Historical Transport Data
print("\n4. Processing Historical Transport Data...")
transport_data = pd.read_excel('table11.xls', header=None)

# Extract yearly ridership data (rows 13-24 have 2014-2024 data)
years = []
ridership = []
for i in range(13, 24):
    year = transport_data.iloc[i, 2]
    daily_ridership = transport_data.iloc[i, 4]
    if pd.notna(year) and pd.notna(daily_ridership):
        years.append(int(year))
        ridership.append(int(daily_ridership))

ridership_df = pd.DataFrame({
    'Year': years,
    'Daily_Ridership_Thousands': ridership
})
ridership_df['Daily_Ridership_Millions'] = ridership_df['Daily_Ridership_Thousands'] / 1000

print(f"   ✓ Historical data: {len(ridership_df)} years")
print(f"   ✓ 2024 average daily ridership: {ridership_df[ridership_df['Year']==2024]['Daily_Ridership_Millions'].values[0]:.2f}M")
print(f"   ✓ COVID impact (2020): {ridership_df[ridership_df['Year']==2020]['Daily_Ridership_Millions'].values[0]:.2f}M")

# 5. Save processed data
print("\n5. Saving processed data...")
stations.to_csv('processed_stations.csv', index=False, encoding='utf-8-sig')
ridership_df.to_csv('processed_ridership.csv', index=False)

# Save line stats
line_stats_df = pd.DataFrame({
    'Line_Code': stations_per_line.index,
    'Line_Name': [line_names.get(code, code) for code in stations_per_line.index],
    'Station_Count': stations_per_line.values
})
line_stats_df.to_csv('processed_line_stats.csv', index=False)

# Save summary stats as JSON
summary = {
    'total_stations': len(stations),
    'total_lines': len(stations_per_line),
    'total_fare_combinations': len(fares),
    'fare_stats': fare_stats,
    'total_accessibility_records': len(accessibility),
    'years_of_data': len(ridership_df),
    'latest_year': int(ridership_df['Year'].max()),
    'latest_ridership_millions': float(ridership_df[ridership_df['Year']==ridership_df['Year'].max()]['Daily_Ridership_Millions'].values[0])
}

with open('summary_stats.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("   ✓ Processed data saved")

print("\n" + "=" * 70)
print("DATA PROCESSING COMPLETE!")
print("=" * 70)
print(f"\nFiles created:")
print("  - processed_stations.csv")
print("  - processed_ridership.csv")
print("  - processed_line_stats.csv")
print("  - summary_stats.json")
print("\nReady for dashboard creation!")
