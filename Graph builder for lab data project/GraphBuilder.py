import pandas as pd
import os
import subprocess
import sys
import re
import matplotlib.pyplot as plt

#! cd "c:\Users\augus\Desktop\Python\Augustinas_Mockevicius\Graph builder for lab data project\Seperated" python GraphBuilder.py
#! THIS INTO TERMINAL, TO OPEN THE SCRIPT AND RUN IT!!!!


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
    User can enter "cancel" or "q" to exit the process.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    print(f"\nLooking for CSV files in: {folder_path}")

    # Gathers all .csv files in folder
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("No CSV files found in this folder.")

    print("\nCSV files found:")
    for i, fname in enumerate(csv_files):
        print(f"{i}: {fname}")

    while True:
        choice = input("\nEnter the number of the CSV you want to use (or 'q', 'cancel', 'quit'): ").strip().lower()

        if choice in ["cancel", "q", "quit"]:
            print("\nProcess cancelled. Exiting...")
            exit()

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


def choose_axes(df: pd.DataFrame):
    """
    Let the user choose which column is X and which column(s) are Y.
    Returns (x_column_name, [list_of_y_column_names]).
    """
    print("\nColumns detected:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    # Choose X axis
    while True:
        x_choice = input("\nEnter the column number for the X axis: ").strip()
        try:
            x_idx = int(x_choice)
            if 0 <= x_idx < len(df.columns):
                x_col = df.columns[x_idx]
                break
            else:
                print(f"Please enter a number between 0 and {len(df.columns) - 1}.")
        except ValueError:
            print("That is not a valid number. Try again.")

    # Choose Y axes (can be multiple, comma separated)
    while True:
        y_choice = input("Enter column number(s) for Y axis data (comma separated, e.g. 1,2,3): ").strip()
        try:
            indices = [int(x.strip()) for x in y_choice.split(",")]
            if not indices:
                print("You must choose at least one Y column.")
                continue

            invalid = [i for i in indices if i < 0 or i >= len(df.columns)]
            if invalid:
                print(f"Invalid indices: {invalid}. Try again.")
                continue

            # Remove duplicates, keep order
            y_indices = []
            for i in indices:
                if i not in y_indices:
                    y_indices.append(i)

            # Do not allow X column to be in Y list
            y_indices = [i for i in y_indices if i != x_idx]
            if not y_indices:
                print("Y columns cannot be the same as X. Choose a different column.")
                continue

            y_cols = [df.columns[i] for i in y_indices]
            break
        except ValueError:
            print("Could not parse that. Use numbers separated by commas.")

    return x_col, y_cols

def plot_data(df: pd.DataFrame, x_col: str, y_cols: list):
    """
    Plot selected X and Y columns.
    """
    print(f"\nPlotting X: {x_col}")
    print(f"Plotting Y columns: {', '.join(y_cols)}")

    # Extract X as numeric
    try:
        x = pd.to_numeric(df[x_col], errors="coerce")
    except Exception as e:
        raise ValueError(f"Could not convert X column to numeric: {e}")

    plt.figure(figsize=(8, 5))

    for y_col in y_cols:
        try:
            y = pd.to_numeric(df[y_col], errors="coerce")
        except Exception as e:
            print(f"Skipping column {y_col}: could not convert to numeric. Error: {e}")
            continue

        plt.plot(x, y, marker="o", linestyle="-", label=y_col)

    plt.xlabel(x_col)
    plt.ylabel("Value")
    plt.title("Lab data plot")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


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

    while True:
        try:
            filepath = choose_csv_file(folder_path)
        except Exception as e:
            print(f"\nError selecting file: {e}")
            return

        # Attempt to load the CSV. If loading fails or the file looks malformed
        # (contains literal "\\t" sequences or parses into a single column
        # with embedded whitespace), run the `fix_csv.py` helper to preprocess it
        # into a clean, comma-separated file and load that instead.
        need_fix = False
        try:
            df = load_csv(filepath)
        except Exception:
            need_fix = True

        # Inspect raw file for explicit '\\t' sequences or suspicious single-column parse
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
                raw_text = fh.read()
            if "\\t" in raw_text:
                need_fix = True
        except Exception:
            # If reading fails, prefer to attempt fix
            need_fix = True

        if not need_fix:
            # If df has only one column but entries contain whitespace, it's likely mis-parsed
            if df is not None and df.shape[1] == 1:
                sample = df.iloc[0, 0]
                if isinstance(sample, str) and re.search(r"\s+", sample):
                    need_fix = True

        if need_fix:
            print("\nFile appears malformed — running preprocessor (fix_csv.py) to clean it up...")
            fix_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix_csv.py")
            if not os.path.isfile(fix_script):
                print(f"Preprocessor not found: {fix_script}")
                return

            # Run fix_csv.py to create a separated file in Seperated/ by default
            cmd = [sys.executable, fix_script, filepath, "--replace-literal-tabs", "--group-by-header"]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Preprocessing failed: {e}")
                return

            # Load from the Seperated output file
            separated_dir = os.path.join(os.path.dirname(filepath), "Seperated")
            base = os.path.splitext(os.path.basename(filepath))[0]
            new_path = os.path.join(separated_dir, base + "_comma" + os.path.splitext(filepath)[1])
            if not os.path.isfile(new_path):
                print(f"Expected preprocessed file not found: {new_path}")
                return

            try:
                df = load_csv(new_path)
                filepath = new_path
            except Exception as e:
                print(f"Could not load preprocessed file: {e}")
                return

        print(f"\nFile selected: {filepath}")
        print("\nFirst few rows of this file:")
        print(df.head())

        print("\n" + "=" * 50)
        proceed = input("Do you want to proceed using this file? (Y/N): ").strip().upper()

        if proceed == "Y":
            print("\nProceeding with the data...")
            break
        elif proceed == "N":
            print("Let's choose a different file.\n")
        else:
            print("Please enter Y or N.\n")

    
    # Show updated columns
    print("\n" + "=" * 50)
    print("Updated columns in your data:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    print("=" * 50)

    # Choose axes and plot
    x_col, y_cols = choose_axes(df)
    plot_data(df, x_col, y_cols)

    print("\nDone.")


if __name__ == "__main__":
    main()
