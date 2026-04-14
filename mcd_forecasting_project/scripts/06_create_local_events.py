from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
output_dir = BASE_DIR / "data" / "processed"

events = pd.DataFrame([
    {
        "event_id": "E001",
        "event_name": "School lunch traffic",
        "start_date": "2026-04-01",
        "end_date": "2026-04-30",
        "target_store_id": "S001",
        "event_type": "lycee_lunch",
        "traffic_uplift_pct": 0.35,
        "traffic_downlift_pct_other_store": 0.00,
        "active_hours": "11,12,13,14"
    },
    {
        "event_id": "E002",
        "event_name": "City center weaker evenings",
        "start_date": "2026-04-01",
        "end_date": "2026-04-30",
        "target_store_id": "S001",
        "event_type": "evening_downlift",
        "traffic_uplift_pct": -0.50,
        "traffic_downlift_pct_other_store": 0.00,
        "active_hours": "18,19,20,21,22"
    },
    {
        "event_id": "E003",
        "event_name": "Fete foraine city center boost",
        "start_date": "2026-04-03",
        "end_date": "2026-04-05",
        "target_store_id": "S001",
        "event_type": "fair_boost",
        "traffic_uplift_pct": 2.50,
        "traffic_downlift_pct_other_store": -0.35,
        "active_hours": "12,13,14,15,16,17,18,19,20,21"
    },
    {
        "event_id": "E004",
        "event_name": "Holiday week city center boost",
        "start_date": "2026-04-04",
        "end_date": "2026-04-08",
        "target_store_id": "S001",
        "event_type": "holiday_boost",
        "traffic_uplift_pct": 0.20,
        "traffic_downlift_pct_other_store": -0.05,
        "active_hours": "11,12,13,14,15,16,17,18"
    }
])

events.to_csv(output_dir / "local_events.csv", index=False)

print(events)
print("\nlocal_events.csv créé dans data/processed/")