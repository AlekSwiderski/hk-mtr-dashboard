from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st


LINE_META = {
    "AEL": ("Airport Express", "#00888a"),
    "TCL": ("Tung Chung Line", "#f7943e"),
    "TKL": ("Tseung Kwan O Line", "#7d499d"),
    "EAL": ("East Rail Line", "#5eb6e4"),
    "TML": ("Tuen Ma Line", "#9a3820"),
    "TWL": ("Tsuen Wan Line", "#e2231a"),
    "ISL": ("Island Line", "#0071ce"),
    "KTL": ("Kwun Tong Line", "#00a040"),
    "SIL": ("South Island Line", "#b5bd00"),
    "DRL": ("Disneyland Resort Line", "#ef74aa"),
}


@dataclass(frozen=True)
class DashboardData:
    stations: pd.DataFrame
    memberships: pd.DataFrame
    line_stats: pd.DataFrame
    fares: pd.DataFrame
    ridership: pd.DataFrame
    facilities: pd.DataFrame


def _station_data(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(root / "mtr_lines_and_stations.csv", encoding="utf-8-sig")
    raw = raw.dropna(subset=["Station ID", "English Name", "Line Code"]).copy()
    raw["Station ID"] = raw["Station ID"].astype(int)

    memberships = (
        raw[["Station ID", "Line Code"]]
        .drop_duplicates()
        .rename(columns={"Line Code": "Line code"})
    )
    names = (
        raw[["Station ID", "Station Code", "English Name", "Chinese Name"]]
        .drop_duplicates("Station ID")
        .rename(
            columns={
                "Station Code": "Station code",
                "English Name": "Station",
                "Chinese Name": "Chinese name",
            }
        )
    )
    line_lists = (
        memberships.groupby("Station ID")["Line code"]
        .agg(lambda codes: ", ".join(LINE_META[code][0] for code in sorted(codes)))
        .rename("Lines")
    )
    line_counts = memberships.groupby("Station ID").size().rename("Line count")
    stations = names.merge(line_lists, on="Station ID").merge(line_counts, on="Station ID")

    line_stats = (
        memberships.groupby("Line code")["Station ID"]
        .nunique()
        .rename("Station count")
        .reset_index()
    )
    line_stats["Line name"] = line_stats["Line code"].map(lambda code: LINE_META[code][0])
    line_stats = line_stats.sort_values("Station count", ascending=False).reset_index(drop=True)
    return stations, memberships, line_stats


def _facility_data(root: Path) -> pd.DataFrame:
    records = pd.read_csv(root / "barrier_free_facilities.csv", encoding="utf-8-sig")
    categories = pd.read_csv(root / "barrier_free_facility_category.csv", encoding="utf-8-sig")
    merged = records.merge(categories, left_on="Key", right_on="Item_Code", validate="many_to_one")
    merged["Station_No"] = merged["Station_No"].astype(int)
    merged["Available"] = merged["Value"].eq("Y")
    merged["Location"] = merged["AJTextEn"].fillna("").str.strip()
    return merged.rename(
        columns={
            "Station_No": "Station ID",
            "Category_En": "Category",
            "Facility_En": "Facility",
            "Sorting_Order": "Order",
        }
    )[["Station ID", "Category", "Facility", "Available", "Location", "Order"]]


@st.cache_data(show_spinner=False)
def load_dashboard_data(root: Path) -> DashboardData:
    stations, memberships, line_stats = _station_data(root)
    fares = pd.read_csv(root / "mtr_lines_fares.csv", encoding="utf-8-sig")
    ridership = pd.read_csv(root / "public_transport_ridership.csv")
    facilities = _facility_data(root)
    return DashboardData(stations, memberships, line_stats, fares, ridership, facilities)
