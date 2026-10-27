
from pathlib import Path
import pandas as pd

# Locate the project root regardless of the terminal's current directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "datasets" / "raw"

print("Project root:", PROJECT_ROOT)
print("Dataset folder:", DATA_DIR)

if not DATA_DIR.exists():
    raise FileNotFoundError(
        f"Dataset folder not found: {DATA_DIR}\n"
        "Create datasets/raw inside the project root "
        "and place your CSV and Excel files there."
    )

files = sorted(
    p for p in DATA_DIR.iterdir()
    if p.suffix.lower() in {".csv", ".xlsx"}
    and not p.name.startswith("~$")
)

if not files:
    print("No CSV or Excel files found in:", DATA_DIR)

for path in files:
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, low_memory=False)
        else:
            df = pd.read_excel(path)

        print("\n" + "=" * 65)
        print("FILE:", path.name)
        print("SHAPE:", df.shape)
        print("COLUMNS:", df.columns.tolist())
        print("DUPLICATE ROWS:", df.duplicated().sum())

        print("\nMISSING VALUES:")
        print(df.isna().sum().sort_values(ascending=False).head(15))

        print("\nSAMPLE:")
        print(df.head(3).to_string(index=False))

    except Exception as exc:
        print(f"\nCould not read {path.name}: {exc}")
