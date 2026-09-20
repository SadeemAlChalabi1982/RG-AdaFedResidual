import csv
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
SOURCE = PROJECT_DIR.parent / "paper2_fl_simulation" / "test_predictions.csv"
OUTPUT = PROJECT_DIR / "horizon-data.js"
STATIONS = ["Kadhimiya", "Karama", "Resafa", "Tarmyya"]


def target_name(chemical: str, horizon: int) -> str:
    return f"{chemical}_Dose_Target_t_plus_{horizon}"


with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
    source_rows = list(csv.DictReader(handle))

lookup = {
    (row["Date"], row["Station"], row["Target"]): row for row in source_rows
}
dates = sorted({row["Date"] for row in source_rows})
replay = []

for date in dates:
    horizons = []
    for horizon in (1, 2, 3):
        station_rows = []
        for station in STATIONS:
            alum = lookup[(date, station, target_name("Alum", horizon))]
            chlorine = lookup[(date, station, target_name("Chlorine", horizon))]
            station_rows.append(
                [
                    round(float(alum["RG_AdaFedResidual"]), 3),
                    round(float(alum["Actual"]), 3),
                    round(float(chlorine["RG_AdaFedResidual"]), 3),
                    round(float(chlorine["Actual"]), 3),
                ]
            )
        horizons.append(station_rows)
    replay.append([date, horizons])

OUTPUT.write_text(
    "window.horizonForecasts="
    + json.dumps(replay, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)

print(
    json.dumps(
        {
            "days": len(replay),
            "first": replay[0][0],
            "last": replay[-1][0],
            "output": str(OUTPUT),
        }
    )
)
