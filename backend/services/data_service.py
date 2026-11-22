
import pandas as pd
from pathlib import Path

# Locate dataset
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "data.csv"

def load_data():

    """Load and preprocess the retail dataset."""

    # 1. Load dataset
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH, encoding="ISO-8859-1")

    print("Original Dataset Shape:", df.shape)

    # 2. Clean column names
    df.columns = df.columns.str.strip()

    # 3. Remove duplicate records
    df = df.drop_duplicates()

    # 4. Clean text columns
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["Description"] = df["Description"].fillna("Unknown").astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()

    # 5. Convert date column
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce",
        dayfirst=False
    )

    # 6. Convert numeric columns
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )

    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )

    df["CustomerID"] = pd.to_numeric(
        df["CustomerID"], errors="coerce"
    )

    # 7. Remove records with invalid essential values
    df = df.dropna(
        subset=["InvoiceDate", "Quantity", "UnitPrice"]
    )

    # 8. Remove cancelled transactions
    df = df[
        ~df["InvoiceNo"].str.upper().str.startswith("C")
    ]

    # 9. Remove invalid sales records
    df = df[
        (df["Quantity"] > 0) &
        (df["UnitPrice"] > 0)
    ]

    # 10. Calculate transaction revenue
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    # 11. Reset index
    df = df.reset_index(drop=True)

    # 12. Final dataset information
    print("\nPreprocessing Completed!")
    print("Final Dataset Shape:", df.shape)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nDuplicate Records:", df.duplicated().sum())
    print("\nDataset Information:")
    df.info()

    return df