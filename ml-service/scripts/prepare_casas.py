from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.constants import FEATURE_COLUMNS, TARGET_COLUMN
from app.synthetic_data import write_synthetic_dataset


def _find_compatible_casas_csv(casas_dir: Path) -> Path | None:
    for candidate in sorted(casas_dir.glob("*.csv")):
        try:
            dataframe = pd.read_csv(candidate, nrows=5)
        except Exception:
            continue

        expected_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN])
        if expected_columns.issubset(dataframe.columns):
            return candidate

    return None


def main() -> None:
    casas_dir = PROJECT_ROOT / "data" / "casas"
    output_path = PROJECT_ROOT / "data" / "synthetic_train.csv"
    casas_dir.mkdir(parents=True, exist_ok=True)

    compatible_csv = _find_compatible_casas_csv(casas_dir)
    if compatible_csv is not None:
        dataframe = pd.read_csv(compatible_csv)
        dataframe.to_csv(output_path, index=False)
        print(output_path)
        return

    generated_path = write_synthetic_dataset(output_path, rows=2000)
    print(generated_path)


if __name__ == "__main__":
    main()
