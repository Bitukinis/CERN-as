import pandas as pd
import os

def load_csv(filepath: str = r"c:\Users\augus\Desktop\Python\Augustinas_Mockevicius\Graph builder for lab data project\Data.ex.csv") -> pd.DataFrame:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {e}")

    if df.empty:
        raise ValueError("CSV file is empty.")

    return df


def main():
    print("=== Lab Data Graph Builder - prototype ===")
    # Directly use the default path to Data.ex.csv
    filepath = r"c:\Users\augus\Desktop\Python\Augustinas_Mockevicius\Graph builder for lab data project\Data.ex.csv"

    try:
        df = load_csv(filepath)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\nFile loaded successfully.")
    print("First few rows of your data:")
    print(df.head())

    print("\nColumns detected:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    # Test: print shape of DataFrame
    print(f"\nDataFrame shape: {df.shape}")


if __name__ == "__main__":
    main()
