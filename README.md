# Hong Kong MTR data explorer

A Streamlit dashboard for exploring the MTR heavy-rail network, point-to-point fares and station accessibility records. A separate Transport Department series provides wider public transport context from 2014 to 2024.

## What is included

- Network size and line membership, including interchange stations
- Published fares for 96 origin and destination stations
- Average daily journeys across all Hong Kong public transport modes
- Station-level availability for 36 documented accessibility features

## Data notes

- MTR network, fare and accessibility files come from the [DATA.GOV.HK MTR dataset](https://data.gov.hk/en-data/dataset/mtr-data-routes-fares-barrier-free-facilities).
- Public transport patronage comes from Table 1.1 of the Hong Kong Transport Department's Monthly Traffic and Transport Digest.
- The accessibility file reports whether a feature is provided. It does not report live service status.
- Source snapshots are stored in this repository so the results can be reproduced.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Built by Alek Swiderski.
