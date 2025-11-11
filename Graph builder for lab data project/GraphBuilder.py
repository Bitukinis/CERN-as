import pandas as pd
import os


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {e}")

    if df.empty:
        raise ValueError("CSV file is empty.")

    return df


def choose_csv_file(folder_path: str) -> str:
    """
    Let the user choose a CSV file from a given folder.
    Returns the full path to the chosen CSV file.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    print(f"\nLooking for CSV files in: {folder_path}")

    # Get all .csv files in folder (case-insensitive)
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("No CSV files found in this folder.")

    print("\nCSV files found:")
    for i, fname in enumerate(csv_files):
        print(f"{i}: {fname}")

    while True:
        choice = input("\nEnter the number of the CSV you want to use: ").strip()
        try:
            idx = int(choice)
            if 0 <= idx < len(csv_files):
                chosen_file = csv_files[idx]
                break
            else:
                print(f"Please enter a number between 0 and {len(csv_files) - 1}.")
        except ValueError:
            print("That is not a valid number. Try again.")

    full_path = os.path.join(folder_path, chosen_file)
    return full_path


def main():
    print("=== Lab Data Graph Builder - prototype ===")

    # Folder where this script lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nScript directory (default folder): {script_dir}")

    folder_path = input(
        "\nEnter folder path containing your CSV files\n"
        "(leave empty to use the script folder above): "
    ).strip()

    if folder_path == "":
        folder_path = script_dir

    try:
        filepath = choose_csv_file(folder_path)
        df = load_csv(filepath)
    except Exception as e:
        print(f"\nError: {e}")
        return

    print(f"\nUsing file: {filepath}")
    print("\nFile loaded successfully.")
    print("First few rows of your data:")
    print(df.head())

    print("\nColumns detected:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    print(f"\nDataFrame shape: {df.shape}")


if __name__ == "__main__":
    main()
