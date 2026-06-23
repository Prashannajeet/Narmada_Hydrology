from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"D:\01 Project\Development\Flood Reports\parsed_18-06-26_8AM")
OUTPUT = ROOT / "data" / "floodSeason2026.json"


def read_rows(name: str) -> list[dict]:
    with (SOURCE / name).open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def numeric(value: str | None) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def normalize_numbers(rows: list[dict]) -> list[dict]:
    numeric_names = {
        "danger_or_max_water_level_m",
        "total_no_of_gates",
        "gate_opened_count",
        "opening_m",
        "discharge_cumecs",
        "discharge_cusec",
        "water_level_m",
        "filling_percent",
    }
    for row in rows:
        for key, value in list(row.items()):
            if (
                key.endswith("_m")
                or key.endswith("_mcm")
                or key.endswith("_mm")
                or key.endswith("_percent")
                or key in numeric_names
            ):
                row[key] = numeric(value)
    return rows


def main() -> None:
    payload = {
        "report": json.loads((SOURCE / "report_meta.json").read_text(encoding="utf-8")),
        "riverStations": normalize_numbers(read_rows("river_gauge_stations.csv")),
        "reservoirs": normalize_numbers(read_rows("reservoirs.csv")),
        "riverObservations": normalize_numbers(read_rows("river_water_level_observations.csv")),
        "reservoirObservations": normalize_numbers(read_rows("reservoir_status_observations.csv")),
        "gateObservations": normalize_numbers(read_rows("reservoir_gate_observations.csv")),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
