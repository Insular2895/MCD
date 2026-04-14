from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
output_dir = BASE_DIR / "data" / "processed"

start_date = "2026-04-01"
end_date = "2026-04-30"

dates = pd.date_range(start=start_date, end=end_date, freq="D")
hours = list(range(10, 24))  # 10h à 23h inclus

rows = []

for date in dates:
    for hour in hours:
        day_of_week = date.day_name()  # Monday, Tuesday, ...
        is_weekend = 1 if date.weekday() >= 5 else 0
        is_wednesday = 1 if date.weekday() == 2 else 0

        # Vacances scolaires simulées
        is_school_holiday = 1 if pd.Timestamp("2026-04-04") <= date <= pd.Timestamp("2026-04-20") else 0

        # Fête foraine / foire de Pâques
        is_fair_period = 1 if pd.Timestamp("2026-04-04") <= date <= pd.Timestamp("2026-04-08") else 0

        # Week-end spécial très fort
        is_fair_peak_weekend = 1 if date in [
            pd.Timestamp("2026-04-04"),
            pd.Timestamp("2026-04-05")
        ] else 0

        rows.append({
            "date": date.date(),
            "hour": hour,
            "datetime_hour": pd.Timestamp(date.date()) + pd.Timedelta(hours=hour),
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "is_wednesday": is_wednesday,
            "is_school_holiday": is_school_holiday,
            "is_fair_period": is_fair_period,
            "is_fair_peak_weekend": is_fair_peak_weekend
        })

calendar_hourly = pd.DataFrame(rows)

calendar_hourly.to_csv(output_dir / "calendar_hourly.csv", index=False)

print(calendar_hourly.head())
print("\nNombre de lignes :", len(calendar_hourly))
print("\ncalendar_hourly.csv créé dans data/processed/")