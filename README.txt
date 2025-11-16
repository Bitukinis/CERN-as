# Graph Builder - Lab Data Analysis Tool

A Python script to visualize and analyze laboratory data from CSV files. Generates customizable charts with trend lines, statistics, and multiple plot types.

---

## How to Start

1. Open terminal in the script folder, for example:
   ```
   cd "c:\Users\augus\Desktop\Python\Name_Surname\Graph builder for lab data project"
   ```

2. Run the script:
   ```
   python GraphBuilder.py
   ```

3. Follow the interactive prompts to load your data and create visualizations.

---

## Step-by-Step Usage

### 1. **Choose CSV File**
   - Enter the folder path (or leave blank for default)
   - Select a CSV file by number from the list
   - View preview of first few rows

### 2. **View Statistics** (Optional)
   - Choose statistics to display: Min, Max, Mean, Median, Std Dev
   - Optionally compute linear slopes between X and Y columns
   - Results show in console

### 3. **Select Axes**
   - Choose ONE column for X-axis
   - Choose ONE or MORE columns for Y-axis (comma-separated)
   - Data must be numeric (or convertible to numeric)

### 4. **Filter Data** (Optional)
   - Set conditions to filter rows (e.g., `column > 100`)
   - Keep only rows matching your criteria
   - Or skip filtering to use all data

### 5. **Create Plot**
   - **Plot Type**: Line, Scatter, Bar, or Histogram
   - **Trend Line** (Line/Scatter only): Linear or Polynomial fit
   - **Dual Y-Axis** (Multi-series only): Different scales for each series
   - **Legend**: Default position, custom position, custom labels, or hide
   - **Chart Title**: Enter custom title or use default

### 6. **Save Plot** (Optional)
   - Choose format: PNG (raster) or PDF (vector)
   - File saved with timestamp to avoid overwriting
   - Location: Same folder as script

---

## Features

### Numeric String Parsing
Handles various data formats automatically:
- **Percentages**: `95%` → 0.95
- **Currency**: `$1,000`, `€500.50`
- **Scientific notation**: `1e-5`, `1E5`
- **Thousands separators**: `1,000.5` → 1000.5
- **Regular numbers**: `42`, `3.14`

### Chart Customization
- **Multiple plot types**: Line, Scatter, Bar, Histogram
- **Trend analysis**: Linear or polynomial trend lines with R² values
- **Legend control**: Position, custom labels, show/hide
- **Custom titles**: Label your charts for clarity
- **Professional styling**: Grid, colors, bold fonts, semi-transparent backgrounds

### Data Analysis
- Summary statistics for all numeric columns
- Linear regression with slope, intercept, and R² coefficient
- Row filtering by conditions
- Missing value handling

---

## About Fix_CSV.py

If your CSV file is malformed (uses tabs instead of commas, or incorrect delimiters), GraphBuilder automatically calls **Fix_CSV.py** to clean it.

### What It Does
- Converts tab-separated data to comma-separated
- Groups columns properly
- Saves cleaned file to `Seperated/` folder
- Names output: `filename_comma.csv`

### To start, in terminal write
```
python fix_csv.py [filename] --replace-literal-tabs --group-by-header
```

## Example Workflow

```
1. Run: python GraphBuilder.py
2. Load: Data.ex.csv
3. Stats: View mean, max, compute slope
4. Filter: Keep only rows where Voltage > 0.5
5. Plot: Line chart with linear trend
6. Legend: Custom position (lower right), custom labels
7. Title: "Voltage-Current Analysis"
8. Save: PNG format
``` 
