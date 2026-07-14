from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from dashboard_data import LINE_META, load_dashboard_data


ROOT = Path(__file__).parent

st.set_page_config(
    page_title="Hong Kong MTR data explorer",
    page_icon=":material/train:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #171717;
            --muted: #606060;
            --rule: #dededb;
            --paper: #f7f7f4;
            --red: #d71920;
        }
        .stApp { background: var(--paper); color: var(--ink); }
        .block-container { max-width: 1180px; padding-top: 2.4rem; padding-bottom: 3rem; }
        [data-testid="stHeader"] { background: rgba(247, 247, 244, .94); }
        [data-testid="stToolbar"], #MainMenu, footer { display: none; }
        h1, h2, h3, p, label, button, input { font-family: Arial, "Helvetica Neue", sans-serif !important; }
        h1 { letter-spacing: -.045em; line-height: 1.02; font-size: clamp(2.5rem, 6vw, 4.8rem) !important; }
        h2 { letter-spacing: -.025em; margin-top: .4rem !important; }
        h3 { font-size: 1rem !important; letter-spacing: .01em; }
        .eyebrow { color: var(--red); font-size: .76rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
        .intro { color: var(--muted); font-size: 1.08rem; line-height: 1.6; max-width: 760px; margin: .7rem 0 1.8rem; }
        .source-note { color: var(--muted); font-size: .82rem; line-height: 1.5; }
        .section-note { color: var(--muted); max-width: 760px; margin-top: -.4rem; }
        [data-testid="stMetric"] { background: #fff; border: 1px solid var(--rule); padding: 1rem 1.05rem; min-height: 116px; }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { font-size: 2rem; letter-spacing: -.035em; }
        button[data-baseweb="tab"] { font-weight: 600; padding-left: .3rem; padding-right: 1.35rem; }
        button[data-baseweb="tab"][aria-selected="true"] { color: var(--red); }
        [data-testid="stDataFrame"] { border: 1px solid var(--rule); }
        .fare-route { border-left: 4px solid var(--red); background: #fff; padding: .9rem 1rem; margin: .4rem 0 1.1rem; }
        .facility { background: #fff; border: 1px solid var(--rule); padding: .75rem .85rem; min-height: 74px; }
        .facility strong { display: block; margin-bottom: .2rem; }
        .footer-rule { border-top: 1px solid var(--rule); margin-top: 2.3rem; padding-top: 1.1rem; }
        @media (max-width: 700px) {
            .block-container { padding: 1.3rem 1rem 2rem; }
            h1 { font-size: 2.65rem !important; }
            [data-testid="stMetric"] { min-height: 98px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def base_figure(height: int = 430) -> dict:
    return dict(
        height=height,
        margin=dict(l=8, r=16, t=26, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color="#252525"),
        hoverlabel=dict(bgcolor="#171717", font_color="white", bordercolor="#171717"),
    )


inject_styles()
data = load_dashboard_data(ROOT)

stations = data.stations
memberships = data.memberships
line_stats = data.line_stats
fares = data.fares
ridership = data.ridership
facilities = data.facilities

latest = ridership.iloc[-1]
interchange_count = int((stations["Line count"] > 1).sum())

st.markdown('<div class="eyebrow">Personal data project · Hong Kong</div>', unsafe_allow_html=True)
st.title("MTR network, fares and access")
st.markdown(
    '<div class="intro">A compact explorer built from MTR open data, with wider public transport patronage included as context. The figures below describe the source files in this project rather than live operating conditions.</div>',
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("MTR stations", f"{len(stations):,}", help="Unique station IDs in the routes and stations file.")
metric_cols[1].metric("Rail lines", f"{len(line_stats):,}", help="Heavy-rail lines in the source file; Light Rail is excluded.")
metric_cols[2].metric("Interchange stations", f"{interchange_count:,}", help="Stations associated with more than one line in the source file.")
metric_cols[3].metric(
    "Daily public transport, 2024",
    f"{latest['Daily journeys'] / 1_000_000:.2f}m",
    help="All public transport modes, not MTR alone.",
)

st.markdown("<br>", unsafe_allow_html=True)
network_tab, fares_tab, patronage_tab, access_tab = st.tabs(
    ["Network", "Fare lookup", "Transport context", "Accessibility"]
)

with network_tab:
    st.header("Network at a glance")
    st.markdown(
        '<p class="section-note">Station totals count each stop once per line. Interchanges therefore appear on every line they serve.</p>',
        unsafe_allow_html=True,
    )

    chart_col, lookup_col = st.columns([1.25, 1], gap="large")
    with chart_col:
        ordered = line_stats.sort_values("Station count")
        fig = go.Figure(
            go.Bar(
                x=ordered["Station count"],
                y=ordered["Line name"],
                orientation="h",
                marker_color=ordered["Line code"].map(lambda code: LINE_META[code][1]),
                text=ordered["Station count"],
                textposition="outside",
                hovertemplate="%{y}<br>%{x} stations<extra></extra>",
            )
        )
        fig.update_layout(**base_figure(), xaxis_title=None, yaxis_title=None, showlegend=False)
        fig.update_xaxes(showgrid=False, visible=False, range=[0, ordered["Station count"].max() + 4])
        fig.update_yaxes(showgrid=False, tickfont_size=12)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with lookup_col:
        selected_line = st.selectbox("Show stations on", ["All lines"] + line_stats["Line name"].tolist())
        if selected_line == "All lines":
            station_view = stations[["Station", "Chinese name", "Lines"]].sort_values("Station")
        else:
            code = line_stats.loc[line_stats["Line name"].eq(selected_line), "Line code"].iloc[0]
            ids = memberships.loc[memberships["Line code"].eq(code), "Station ID"]
            station_view = stations.loc[stations["Station ID"].isin(ids), ["Station", "Chinese name", "Lines"]].sort_values("Station")
        st.caption(f"{len(station_view)} stations")
        st.dataframe(station_view, hide_index=True, width="stretch", height=422)

with fares_tab:
    st.header("Point-to-point fare lookup")
    st.markdown(
        '<p class="section-note">Published fares for the selected origin and destination. A zero fare can indicate the same station or a linked station pair.</p>',
        unsafe_allow_html=True,
    )
    station_names = sorted(fares["SRC_STATION_NAME"].unique())
    left, right = st.columns(2)
    with left:
        origin = st.selectbox("From", station_names, index=station_names.index("Central"))
    with right:
        destination = st.selectbox("To", station_names, index=station_names.index("Admiralty"))

    fare = fares.loc[
        fares["SRC_STATION_NAME"].eq(origin) & fares["DEST_STATION_NAME"].eq(destination)
    ].iloc[0]
    st.markdown(
        f'<div class="fare-route"><strong>{origin}</strong> &nbsp;→&nbsp; <strong>{destination}</strong></div>',
        unsafe_allow_html=True,
    )
    fare_cols = st.columns(4)
    fare_cols[0].metric("Adult Octopus", f"HK${fare['OCT_ADT_FARE']:.1f}")
    fare_cols[1].metric("Adult single journey", f"HK${fare['SINGLE_ADT_FARE']:.1f}")
    fare_cols[2].metric("Student Octopus", f"HK${fare['OCT_STD_FARE']:.1f}")
    fare_cols[3].metric("Child Octopus", f"HK${fare['OCT_CON_CHILD_FARE']:.1f}")
    st.caption("Concession eligibility and current fare conditions should be checked with MTR before travel.")

with patronage_tab:
    st.header("Hong Kong public transport context")
    st.markdown(
        '<p class="section-note">Average daily passenger journeys across MTR, buses, minibuses, trams, ferries and taxis. This is context for the network, not an MTR ridership series.</p>',
        unsafe_allow_html=True,
    )

    pre_covid = ridership.loc[ridership["Year"].eq(2019), "Daily journeys"].iloc[0]
    low = ridership.loc[ridership["Year"].eq(2020), "Daily journeys"].iloc[0]
    context_cols = st.columns(3)
    context_cols[0].metric("2019", f"{pre_covid / 1_000_000:.2f}m", "daily journeys")
    context_cols[1].metric("2020", f"{low / 1_000_000:.2f}m", f"{(low / pre_covid - 1) * 100:.1f}% vs 2019")
    context_cols[2].metric("2024", f"{latest['Daily journeys'] / 1_000_000:.2f}m", f"{(latest['Daily journeys'] / pre_covid - 1) * 100:.1f}% vs 2019")

    fig = go.Figure(
        go.Scatter(
            x=ridership["Year"],
            y=ridership["Daily journeys"] / 1_000_000,
            mode="lines+markers",
            line=dict(color="#d71920", width=3),
            marker=dict(size=7, color="#f7f7f4", line=dict(color="#d71920", width=2)),
            fill="tozeroy",
            fillcolor="rgba(215,25,32,.07)",
            hovertemplate="%{x}<br>%{y:.2f}m journeys/day<extra></extra>",
        )
    )
    fig.add_vrect(x0=2019.65, x1=2020.35, fillcolor="#171717", opacity=.06, line_width=0)
    fig.update_layout(**base_figure(440), showlegend=False, xaxis_title=None, yaxis_title="Million journeys per day")
    fig.update_xaxes(dtick=1, showgrid=False)
    fig.update_yaxes(gridcolor="#dededb", zeroline=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with access_tab:
    st.header("Station facility lookup")
    covered_ids = set(facilities["Station ID"])
    covered = stations.loc[stations["Station ID"].isin(covered_ids)].sort_values("Station")
    st.markdown(
        f'<p class="section-note">The MTR file records whether 36 accessibility features are available at {len(covered)} of the {len(stations)} stations in this network snapshot. It does not report whether equipment is currently in service.</p>',
        unsafe_allow_html=True,
    )
    selected_station = st.selectbox("Station", covered["Station"].tolist(), index=covered["Station"].tolist().index("Admiralty"))
    station_id = covered.loc[covered["Station"].eq(selected_station), "Station ID"].iloc[0]
    station_facilities = facilities.loc[facilities["Station ID"].eq(station_id)].copy()

    category_names = station_facilities["Category"].drop_duplicates().tolist()
    selected_category = st.selectbox("Facility group", category_names)
    shown = station_facilities.loc[station_facilities["Category"].eq(selected_category)]
    available = shown.loc[shown["Available"]].sort_values("Order")

    st.caption(f"{len(available)} of {len(shown)} listed features available in this group")
    if available.empty:
        st.info("No feature in this group is marked as available in the source file.")
    else:
        grid = st.columns(3)
        for index, (_, item) in enumerate(available.iterrows()):
            location = item["Location"] if item["Location"] else "Location not specified"
            grid[index % 3].markdown(
                f'<div class="facility"><strong>{item["Facility"]}</strong><span class="source-note">{location}</span></div>',
                unsafe_allow_html=True,
            )

st.markdown(
    """
    <div class="footer-rule source-note">
    Sources: MTR open-data files for lines, fares and barrier-free facilities; Hong Kong Transport Department Table 1.1 for public transport patronage. Source files are stored with the project for reproducibility.<br>
    Built by Alek Swiderski.
    </div>
    """,
    unsafe_allow_html=True,
)
