from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = Path(r"C:\Users\zacha\OneDrive\Desktop\RFL Tracker\data\output\measurements.csv")
TARGET_CSV = PROJECT_ROOT / "data" / "seed_measurements.csv"


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"Source CSV not found: {SOURCE_CSV}")

    TARGET_CSV.parent.mkdir(parents=True, exist_ok=True)

    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as source_handle:
        reader = csv.DictReader(source_handle)
        rows = []
        for row in reader:
            entry_date = (row.get("EntryDate") or "").strip()
            weight = (row.get("WeightLbs") or "").strip()
            waist = (row.get("WaistIn") or "").strip()
            notes = (row.get("Notes") or "").strip()
            if not entry_date or not weight or not waist:
                continue
            rows.append(
                {
                    "entry_date": entry_date,
                    "weight_lbs": weight,
                    "waist_in": waist,
                    "notes": notes,
                }
            )

    with TARGET_CSV.open("w", encoding="utf-8", newline="") as target_handle:
        writer = csv.DictWriter(target_handle, fieldnames=["entry_date", "weight_lbs", "waist_in", "notes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Seed rows written: {len(rows)}")
    print(f"Seed file: {TARGET_CSV}")


if __name__ == "__main__":
    main()
