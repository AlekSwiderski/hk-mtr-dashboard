from pathlib import Path

from dashboard_data import _facility_data, _station_data
import pandas as pd


ROOT = Path(__file__).parents[1]


def test_station_data_drops_blank_rows_and_keeps_interchanges():
    stations, memberships, line_stats = _station_data(ROOT)

    assert len(stations) == 100
    assert len(line_stats) == 10
    assert memberships.shape[0] == 120
    assert not stations[["Station ID", "Station"]].isna().any().any()
    assert stations.loc[stations["Station"].eq("Admiralty"), "Line count"].iloc[0] == 4


def test_ridership_units_are_daily_journeys():
    ridership = pd.read_csv(ROOT / "public_transport_ridership.csv")

    assert ridership.loc[ridership["Year"].eq(2024), "Daily journeys"].iloc[0] == 11_698_000
    assert ridership["Daily journeys"].between(8_000_000, 14_000_000).all()


def test_facility_dictionary_maps_every_record():
    facilities = _facility_data(ROOT)

    assert len(facilities) == 3_564
    assert facilities["Facility"].nunique() == 36
    assert facilities["Category"].nunique() == 4
    assert facilities["Available"].dtype == bool


def test_fare_table_is_complete_for_96_stations():
    fares = pd.read_csv(ROOT / "mtr_lines_fares.csv", encoding="utf-8-sig")

    assert fares["SRC_STATION_NAME"].nunique() == 96
    assert len(fares) == 96 * 96
    assert not fares.isna().any().any()
