import pandas as pd
import os
import subprocess
import sys
import re
import matplotlib.pyplot as plt
import numpy as np

#! Run this in terminal to seperate variables in file:

#! fix_csv.py File_Name --group-by-header --replace-literal-tabs --inplace

#! run this to to open the file containing the script and run it:

#! cd "c:\Users\augus\Desktop\Python\Augustinas_Mockevicius\Graph builder for lab data project" python GraphBuilder.py



def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    Raises FileNotFoundError if file doesn't exist, or ValueError if read/parse fails or file is empty.
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
    Interactive file picker: list all .csv files in folder and let user select by number.
    Returns full path to chosen file. User can enter 'cancel' or 'q' to exit.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    print(f"\nLooking for CSV files in: {folder_path}")

    # List all .csv files in the folder
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
    Prompt user to select X column (single) and Y column(s) (comma-separated, multiple allowed).
    Returns tuple: (x_col_name, [y_col_names]).
    """
    print("\nColumns detected:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    # User selects X axis column (single column only)
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

    # User selects Y axis column(s); comma-separated list for multiple columns
    while True:
        y_choice = input("Enter column number(s) for Y axis data (comma separated): ").strip()
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


def show_summary_stats(df: pd.DataFrame, numeric_cols: list):
    """
    Display summary statistics (min, max, mean, median, std) for numeric columns.
    User chooses which statistics to display via comma-separated selection (e.g., 1,3,5).
    Optionally compute linear slope(s) (y = m*x + b) between a chosen X column and one or more Y columns.
    """
    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)

    print("\nWhich statistics would you like to see?")
    print("1: Minimum")
    print("2: Maximum")
    print("3: Mean")
    print("4: Median")
    print("5: Standard deviation")
    print("6: All statistics")
    print("7: Compute slope(s) for chosen X and Y columns")
    print("\nEnter choice(s), comma-separated.")
    print("Or press Enter to skip statistics")

    choice = input("\nEnter your choice: ").strip()
    if choice == "":
        return

    stats_list = ["min", "max", "mean", "median", "std"]
    selected = []
    slope_requested = False

    # Parse comma-separated numbers
    try:
        indices = [int(x.strip()) for x in choice.split(",")]
    except ValueError:
        print("Invalid input. Could not parse numbers.")
        return

    if 6 in indices:
        selected = stats_list.copy()

    for idx in indices:
        if idx == 6:
            continue
        if idx == 7:
            slope_requested = True
            continue
        if 1 <= idx <= 5:
            stat_name = stats_list[idx - 1]
            if stat_name not in selected:
                selected.append(stat_name)
        else:
            print(f"Warning: {idx} is not a valid choice (1-7). Skipping.")

    if not selected and not slope_requested:
        print("No valid statistics selected.")
        return

    # Calculate requested statistics (min/max/mean/median/std) for each numeric column
    stats_results = {}
    for col in numeric_cols:
        try:
            # Convert to numeric and drop NaN/non-numeric values
            data = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(data) == 0:
                print(f"\n{col}: (no numeric data)")
                continue
            col_stats = {}
            if "min" in selected:
                col_stats['min'] = data.min()
            if "max" in selected:
                col_stats['max'] = data.max()
            if "mean" in selected:
                col_stats['mean'] = data.mean()
            if "median" in selected:
                col_stats['median'] = data.median()
            if "std" in selected:
                col_stats['std'] = data.std()

            # Print to console as before
            print(f"\n{col}:")
            for k, v in col_stats.items():
                label = k.capitalize()
                print(f"  {label}: {v:.6g}")

            stats_results[col] = col_stats
        except Exception as e:
            print(f"\n{col}: Could not compute statistics ({e})")

    # If slope computation requested, prompt for X and Y columns and compute
    if slope_requested:
        print("\nSLOPE COMPUTATION")
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")

        # Choose X axis
        while True:
            x_choice = input("\nEnter the column number to use as X for slope calculation (or 'c' to cancel): ").strip()
            if x_choice.lower() in ["c", "cancel"]:
                print("Slope computation cancelled.")
                return
            try:
                x_idx = int(x_choice)
                if 0 <= x_idx < len(df.columns):
                    x_col = df.columns[x_idx]
                    break
                else:
                    print(f"Please enter a number between 0 and {len(df.columns) - 1}.")
            except ValueError:
                print("That is not a valid number. Try again or enter 'c' to cancel.")

        # Choose Y axes (one or multiple)
        while True:
            y_choice = input("Enter column number(s) for Y (comma separated) or 'c' to cancel: ").strip()
            if y_choice.lower() in ["c", "cancel"]:
                print("Slope computation cancelled.")
                return
            try:
                y_indices = [int(x.strip()) for x in y_choice.split(",")]
                # Validate indices
                invalid = [i for i in y_indices if i < 0 or i >= len(df.columns)]
                if invalid:
                    print(f"Invalid indices: {invalid}. Try again.")
                    continue
                # Remove X if present in Y list
                y_indices = [i for i in y_indices if i != x_idx]
                if not y_indices:
                    print("Y columns cannot be the same as X. Choose different column(s).")
                    continue
                y_cols = [df.columns[i] for i in y_indices]
                break
            except ValueError:
                print("Could not parse that. Use numbers separated by commas.")

        # Compute linear slope (m) and intercept (b) for fitted line y = m*x + b, plus R² quality
        for ycol in y_cols:
            try:
                # Align X and Y: drop rows where either column has NaN or non-numeric value
                valid = df[[x_col, ycol]].apply(pd.to_numeric, errors="coerce").dropna()
                if valid.empty:
                    print(f"\n{ycol}: (no numeric data after alignment with X)")
                    continue
                x = valid[x_col].values
                y = valid[ycol].values
                # Fit linear polynomial: np.polyfit returns [slope, intercept] for degree=1
                slope, intercept = np.polyfit(x, y, 1)
                # Compute R² (coefficient of determination): 0=poor fit, 1=perfect fit
                y_pred = slope * x + intercept  # Predicted y values from fitted line
                ss_res = ((y - y_pred) ** 2).sum()  # Sum of squared residuals (prediction errors)
                ss_tot = ((y - y.mean()) ** 2).sum()  # Total sum of squares (data variance)
                r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else float('nan')  # R² = 1 - (residual/total)
                print(f"\n{ycol} vs {x_col}:")
                print(f"  Slope:     {slope:.6g}")
                print(f"  Intercept: {intercept:.6g}")
                if not (r2 != r2):  # check for NaN
                    print(f"  R^2:       {r2:.6g}")
            except Exception as e:
                print(f"\n{ycol}: Could not compute slope ({e})")

    # Return selected stat keys and numeric results so the caller can annotate plots
    return selected, stats_results


def filter_data(df: pd.DataFrame, x_col: str, y_cols: list) -> pd.DataFrame:
    """
    Filter data rows by a user-specified condition (e.g., column > value).
    Returns filtered DataFrame; if no filter chosen, returns full DataFrame unchanged.
    """
    print("\n" + "=" * 50)
    print("FILTER DATA (Points of Interest)")
    print("=" * 50)
    
    filter_choice = input("\nDo you want to filter data by a condition? (Y/N): ").strip().upper()
    if filter_choice != "Y":
        return df
    
    all_cols = [x_col] + y_cols
    print("\nAvailable columns:")
    for i, col in enumerate(all_cols):
        print(f"{i}: {col}")
    
    col_idx = input("\nEnter column number to filter on: ").strip()
    try:
        col_idx = int(col_idx)
        if col_idx < 0 or col_idx >= len(all_cols):
            print("Invalid column index.")
            return df
        filter_col = all_cols[col_idx]
    except ValueError:
        print("Invalid input.")
        return df
    
    print("\nFilter operators:")
    print("1: > (greater than)")
    print("2: < (less than)")
    print("3: >= (greater or equal)")
    print("4: <= (less or equal)")
    print("5: == (equal to)")
    print("6: != (not equal to)")
    
    op_choice = input("\nEnter operator (1-6): ").strip()
    op_map = {"1": ">", "2": "<", "3": ">=", "4": "<=", "5": "==", "6": "!="}
    op = op_map.get(op_choice)
    if not op:
        print("Invalid operator.")
        return df
    
    value_str = input(f"Enter value to compare {filter_col} {op} : ").strip()
    try:
        value = float(value_str)
    except ValueError:
        print("Invalid value.")
        return df
    
    # Apply the chosen comparison operator to create a boolean mask (True = rows to keep)
    col_data = pd.to_numeric(df[filter_col], errors="coerce")
    if op == ">":
        mask = col_data > value
    elif op == "<":
        mask = col_data < value
    elif op == ">=":
        mask = col_data >= value
    elif op == "<=":
        mask = col_data <= value
    elif op == "==":
        mask = col_data == value
    elif op == "!=":
        mask = col_data != value
    
    # Filter DataFrame using mask; reset_index renumbers rows starting at 0
    filtered_df = df[mask].reset_index(drop=True)
    print(f"\nFiltered: {len(filtered_df)} of {len(df)} rows match {filter_col} {op} {value}")
    return filtered_df


def plot_data(df: pd.DataFrame, x_col: str, y_cols: list):
    """
    Plot selected X and Y columns with multiple plot types (line/scatter/bar/histogram).
    Supports trend lines (linear/polynomial), dual Y-axis, and plot saving (PNG/PDF).
    """
    print(f"\nPlotting X: {x_col}")
    print(f"Plotting Y columns: {', '.join(y_cols)}")

    # User chooses plot visualization type
    print("\nPlot type options:")
    print("1: Line plot (default)")
    print("2: Scatter plot")
    print("3: Bar chart")
    print("4: Histogram")
    
    plot_choice = input("\nEnter plot type (1-4, default 1): ").strip() or "1"
    plot_type = {"1": "line", "2": "scatter", "3": "bar", "4": "histogram"}.get(plot_choice, "line")
    
    # Ask about trend line (for line/scatter only)
    trend_choice = None
    if plot_type in ["line", "scatter"]:
        trend_choice = input("Add trend line? (1=Linear, 2=Polynomial, 0=No): ").strip() or "0"
    
    # Ask about dual Y-axis (for line plots with multiple series)
    dual_axis = False
    if len(y_cols) > 1 and plot_type == "line":
        dual_choice = input("Use dual Y-axis for different scales? (Y/N): ").strip().upper()
        dual_axis = (dual_choice == "Y")
    
    # Convert X column to numeric; drop NaN values
    try:
        x = pd.to_numeric(df[x_col], errors="coerce")
    except Exception as e:
        raise ValueError(f"Could not convert X column to numeric: {e}")

    # Create figure with main axis
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = None
    
    # Color palette for each Y series
    colors = plt.cm.tab10(np.linspace(0, 1, len(y_cols)))

    # Plot each Y column
    for idx, y_col in enumerate(y_cols):
        try:
            # Convert Y to numeric; drop NaN values
            y = pd.to_numeric(df[y_col], errors="coerce")
        except Exception as e:
            print(f"Skipping column {y_col}: could not convert to numeric. Error: {e}")
            continue
        
        # Select axis: use ax2 (twin axis) for 2nd+ series if dual_axis is enabled
        current_ax = ax1
        if dual_axis and idx > 0:
            if ax2 is None:
                ax2 = ax1.twinx()  # Create second Y-axis sharing same X-axis
            current_ax = ax2

        # Plot based on type
        if plot_type == "line":
            # Line plot with markers for clarity; larger linewidth and markersize
            current_ax.plot(x, y, marker="o", markersize=6, linestyle="-", linewidth=2.5, 
                           label=y_col, color=colors[idx])
            
            # Add trend line if requested
            if trend_choice == "1":
                # Align numeric x and y values by removing rows where either is NaN
                valid_xy = pd.concat([x, y], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
                if len(valid_xy) > 1:
                    xv = valid_xy.iloc[:, 0].values
                    yv = valid_xy.iloc[:, 1].values
                    # Fit linear trend: computes slope and intercept
                    slope, intercept = np.polyfit(xv, yv, 1)
                    p = np.poly1d([slope, intercept])
                    # Generate smooth line from data min to max
                    x_trend = np.linspace(xv.min(), xv.max(), 100)
                    current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8, 
                                   color=colors[idx], label=f"{y_col} trend")
                    # Annotate slope/intercept on plot using axis coordinates (0-1 range)
                    txt = f"Slope: {slope:.3g}\nIntercept: {intercept:.3g}"
                    # Vertical offset prevents label overlap between multiple series
                    y_offset = 0.95 - (idx * 0.08)
                    current_ax.text(0.02, y_offset, txt, transform=current_ax.transAxes,
                                    color=colors[idx], fontsize=10, fontweight='bold',
                                    bbox=dict(facecolor='white', alpha=0.75, edgecolor=colors[idx], linewidth=1.5))
            elif trend_choice == "2":
                # Fit polynomial (degree 2) trend line
                z = np.polyfit(x.dropna().index, y.dropna(), 2)
                p = np.poly1d(z)
                x_trend = np.linspace(x.min(), x.max(), 100)
                current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8, 
                               color=colors[idx], label=f"{y_col} poly fit")
                
        elif plot_type == "scatter":
            # Scatter plot with transparency (alpha) to show overlapping points; larger markers with edge
            current_ax.scatter(x, y, s=80, label=y_col, alpha=0.7, color=colors[idx], edgecolors='black', linewidth=0.5)
            
            if trend_choice == "1":
                # Align and fit linear trend for scatter plot
                valid_xy = pd.concat([x, y], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
                if len(valid_xy) > 1:
                    xv = valid_xy.iloc[:, 0].values
                    yv = valid_xy.iloc[:, 1].values
                    slope, intercept = np.polyfit(xv, yv, 1)
                    p = np.poly1d([slope, intercept])
                    x_trend = np.linspace(xv.min(), xv.max(), 100)
                    current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8, 
                                   color=colors[idx], label=f"{y_col} trend")
                    txt = f"Slope: {slope:.3g}\nIntercept: {intercept:.3g}"
                    y_offset = 0.95 - (idx * 0.08)
                    current_ax.text(0.02, y_offset, txt, transform=current_ax.transAxes,
                                    color=colors[idx], fontsize=10, fontweight='bold',
                                    bbox=dict(facecolor='white', alpha=0.75, edgecolor=colors[idx], linewidth=1.5))
            elif trend_choice == "2":
                z = np.polyfit(x.dropna().index, y.dropna(), 2)
                p = np.poly1d(z)
                x_trend = np.linspace(x.min(), x.max(), 100)
                current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8, 
                               color=colors[idx], label=f"{y_col} poly fit")
                
        elif plot_type == "bar":
            # Bar chart: one bar per data point with edge colors for definition
            current_ax.bar(range(len(y)), y, label=y_col, alpha=0.75, color=colors[idx], edgecolor='black', linewidth=1.2)
            current_ax.set_xticks(range(len(y)))
            
        elif plot_type == "histogram":
            # Histogram: distribution of Y values (bins=20 intervals) with edge color
            current_ax.hist(y.dropna(), bins=20, label=y_col, alpha=0.7, color=colors[idx], edgecolor='black', linewidth=1)

    # Set axis labels and title with larger, bold fonts
    ax1.set_xlabel(x_col, fontsize=12, fontweight='bold')
    if not dual_axis:
        # Single Y-axis: label lists all Y columns
        ax1.set_ylabel(", ".join(y_cols), fontsize=12, fontweight='bold')
    else:
        # Dual Y-axis: first series uses ax1 (left), others use ax2 (right)
        ax1.set_ylabel(y_cols[0], fontsize=12, fontweight='bold', color=colors[0])
        ax1.tick_params(axis='y', labelcolor=colors[0], labelsize=10)
        if ax2:
            ax2.set_ylabel(", ".join(y_cols[1:]), fontsize=12, fontweight='bold', color=colors[1])
            ax2.tick_params(axis='y', labelcolor=colors[1], labelsize=10)
    
    # Improve title and styling
    ax1.set_title("Laboratory Data Analysis", fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.4, linestyle='--', linewidth=0.7)  # Enhanced grid: dashed lines, better visibility
    ax1.tick_params(axis='x', labelsize=10)
    
    # Enhanced legend with better positioning and frame
    legend1 = ax1.legend(loc='upper left', fontsize=10, framealpha=0.95, edgecolor='black', fancybox=True, shadow=True)
    if ax2:
        ax2.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='black', fancybox=True, shadow=True)
    
    # Add light background color for readability
    ax1.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()  # Auto-adjust spacing to avoid label cutoff
    
    # User chooses whether to save plot to disk
    save_choice = input("\nSave plot? (1=PNG, 2=PDF, 0=none): ").strip() or "0"
    if save_choice in ["1", "2"]:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ext = ".png" if save_choice == "1" else ".pdf"
        # Filename includes timestamp (YYYYMMDD_HHMMSS) to avoid overwriting
        filename = os.path.join(script_dir, f"plot_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}{ext}")
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')  # Higher DPI for quality
        print(f"Plot saved to: {filename}")
    
    plt.show()  # Display plot in window


def main():
    """
    Main workflow: load CSV, compute statistics, filter data, and generate plots.
    """
    print("=== Lab Data Graph Builder - prototype ===")

    # Folder where this script lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    separated_dir = os.path.join(script_dir, "Seperated")
    
    # If Seperated folder exists and has CSV files, use it as default; otherwise use script directory
    if os.path.isdir(separated_dir) and any(f.lower().endswith('.csv') for f in os.listdir(separated_dir)):
        default_dir = separated_dir
        print(f"\nDefault folder: {separated_dir} (preprocessed files)")
    else:
        default_dir = script_dir
        print(f"\nDefault folder: {script_dir} (original files)")

    folder_path = input(
        "\nEnter folder path containing your CSV files\n"
        f"(leave empty to use the default folder above): "
    ).strip()

    if folder_path == "":
        folder_path = default_dir

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

    # Show summary statistics
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    if numeric_cols:
        show_summary_stats(df, numeric_cols)
    
    # Choose axes and plot
    x_col, y_cols = choose_axes(df)
    
    # Filter data by points of interest
    df_filtered = filter_data(df, x_col, y_cols)
    
    # Plot the data
    plot_data(df_filtered, x_col, y_cols)

    print("\nDone.")


if __name__ == "__main__":
    main()
