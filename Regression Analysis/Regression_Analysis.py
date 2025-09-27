# DATA VISUALISATION DASHBOARD
import os
import csv
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np


FILTER = ["Full Date", "Year", "Month", "Day", "Day of Week"]

DATE_FORMAT_OPTIONS = {
    "1": ("%Y-%m-%d", "2025-12-13"),
    "2": ("%d-%m-%Y", "13-12-2025"),
    "3": ("%m-%d-%Y", "12-13-2025"),
    "4": ("%Y/%m/%d", "2025/12/13"),
    "5": ("%d/%m/%Y", "13/12/2025"),
    "6": ("%m/%d/%Y", "12/13/2025"),
    "7": ("%Y.%m.%d", "2025.12.13"),
    "8": ("%d.%m.%Y", "13.12.2025"),
    "9": ("%m.%d.%Y", "12.13.2025"),
    "10": ("%Y%m%d", "20251213"),
    "11": ("%d%m%Y", "13122025"),
    "12": ("%m%d%Y", "12132025"),
    "13": ("epoch", "Unix timestamp, e.g. 1694649600"),
    "14": ("custom", "Enter your own format")
}

def load_data(data_dir=None):
    if data_dir is None:
        default_dir = os.path.dirname(os.path.abspath(__file__))
        print()
        user_dir = input("Enter directory path to load data (leave blank for default): ").strip()
        data_dir = user_dir if user_dir else default_dir
    if not os.path.isdir(data_dir):
        print(f"Directory '{data_dir}' does not exist.")
        return None
    files = [f for f in os.listdir(data_dir)
             if os.path.isfile(os.path.join(data_dir, f))
             and not f.startswith('~$')
             and not f.startswith('.')]
    if not files:
        print("No files found in the folder.")
        return None
    print("\nAvailable files in the folder:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file}")
    try:
        choice = int(input("\nEnter the number of the file to load: "))
        file_name = files[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None
    file_path = os.path.join(data_dir, file_name)
    try:
        if file_name.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        elif file_name.lower().endswith('.txt'):
            # Inline delimiter detection
            with open(file_path, 'r') as f:
                sample = f.read(4096)
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = ','  # fallback default
            print(f"Auto-detected delimiter: '{delimiter}'")
            df = pd.read_csv(file_path, delimiter=delimiter)
        else:
            print("Unsupported file format. Please provide a CSV, TXT, or Excel file.")
            return None
        print()
        print(f"Data loaded successfully with {len(df):,} records and {len(df.columns):,} columns.")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def show_fields(df):
    if df is None:
        print("No data loaded.")
        return
    columns = list(df.columns)
    print("\nAvailable fields in the dataset:")
    for idx, col in enumerate(columns, 1):
        print(f"{idx}. {col}")
    return columns

def confirm_date_fields(df):
    print("\nDo you have date fields in your dataset?")
    print("1. Yes")
    print("2. No")
    print()
    choice = input("Enter 1 or 2: ").strip()
    if choice == '1':
        user_format = select_date_format()
        if user_format is None:
            print("No valid date format selected.")
            return None
        # Auto-detect date fields using selected format
        detected = []
        for col in df.columns:
            sample_value = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else None
            if user_format == "epoch":
                try:
                    val = float(sample_value)
                    dt = datetime.datetime.fromtimestamp(val)
                    detected.append(col)
                except Exception:
                    continue
            elif sample_value:
                try:
                    date_part = sample_value.split()[0] if ' ' in sample_value else sample_value
                    datetime.datetime.strptime(date_part, user_format)
                    parsed = pd.to_datetime(df[col], format=user_format, errors='coerce')
                    if parsed.notna().mean() > 0.6:
                        detected.append(col)
                except Exception:
                    continue
        if detected:
            print("\n📅 Fields detected as dates with format '{}':".format(user_format))
            for i, col in enumerate(detected, 1):
                print(f"{i}. {col}")
            return detected
        else:
            print()
            print("No fields detected as dates with the selected format.")
            return None
    elif choice == '2':
        print()
        print("Proceeding without date fields.")
        return None
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return confirm_date_fields(df)

def select_date_format():
    print("\n📅 Choose the expected date format for parsing:")
    for key, (fmt, example) in DATE_FORMAT_OPTIONS.items():
        print(f"{key}. {fmt}  → {example}")
    print()
    fmt_choice = input("Enter the number corresponding to your format: ").strip()
    if fmt_choice in DATE_FORMAT_OPTIONS:
        if DATE_FORMAT_OPTIONS[fmt_choice][0] == "custom":
            print()
            user_format = input("Enter your custom date format string (e.g. %d-%m-%Y): ").strip()
        else:
            user_format = DATE_FORMAT_OPTIONS[fmt_choice][0]
    else:
        print("Invalid format choice. Defaulting to fallback parsing.")
        user_format = None
    return user_format

def split_date_fields(df, date_field):
    """
    Filter a DataFrame by a single date field, offering options for year, year-month, day of week, etc.
    Returns the filtered DataFrame.
    """
    print("\nDate field detected. How would you like to filter?")
    print("1. Specific year (e.g. 2025)")
    print("2. Year and month (e.g. 2025-01)")
    print("3. Specific day of week (e.g. all Mondays for 2025)")
    print("4. Specific day of week for year-month (e.g. all Mondays for 2025-01)")
    print("5. No filter (use all data)")
    print()
    choice = input("Enter filter option (1-5): ").strip()
    dates = pd.to_datetime(df[date_field], errors='coerce')
    mask = pd.Series([True]*len(df))
    if choice == '1':
        year = int(input("Enter year (e.g. 2025): ").strip())
        mask = dates.dt.year == year
    elif choice == '2':
        year = int(input("Enter year (e.g. 2025): ").strip())
        month = int(input("Enter month (1-12): ").strip())
        mask = (dates.dt.year == year) & (dates.dt.month == month)
    elif choice == '3':
        year = int(input("Enter year (e.g. 2025): ").strip())
        dow = input("Enter day of week (e.g. Monday): ").strip().lower()
        dow_map = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,"friday":4,"saturday":5,"sunday":6}
        mask = (dates.dt.year == year) & (dates.dt.dayofweek == dow_map.get(dow, -1))
    elif choice == '4':
        year = int(input("Enter year (e.g. 2025): ").strip())
        month = int(input("Enter month (1-12): ").strip())
        dow = input("Enter day of week (e.g. Monday): ").strip().lower()
        dow_map = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,"friday":4,"saturday":5,"sunday":6}
        mask = (dates.dt.year == year) & (dates.dt.month == month) & (dates.dt.dayofweek == dow_map.get(dow, -1))
    # else: no filter
    filtered = df[mask]
    if filtered.empty:
        print("No data found for the selected filter.")
    return filtered


def gregression_plot(df, detected_date_fields):
        columns = list(df.columns)
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        print("\nEnter a formula/ column numbers or column names with valid expressions.")
        print()
        x_input = input("Enter formula or field for X (independent variable): ").strip()
        y_input = input("Enter formula or field for Y (dependent variable): ").strip()

        import re
        def try_eval(val, df_ctx):
            def repl(m):
                idx = int(m.group(0)) - 1
                if 0 <= idx < len(columns):
                    return f'df_ctx["{columns[idx]}"]'
                else:
                    raise ValueError(f"Column number {idx+1} out of range")
            try:
                formula_parsed = re.sub(r'\b\d+\b', repl, val)
                return eval(formula_parsed, {"df_ctx": df_ctx, "pd": pd})
            except Exception:
                pass
            if val in df_ctx.columns:
                return df_ctx[val]
            try:
                return float(val)
            except Exception:
                pass
            print(f"Could not interpret input: {val}")
            return None

        # Date filtering
        df_plot = df
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                def resolve_col(val, col_list=None):
                    if val.isdigit():
                        idx = int(val) - 1
                        if col_list is not None:
                            if 0 <= idx < len(col_list):
                                return col_list[idx]
                        else:
                            if 0 <= idx < len(columns):
                                return columns[idx]
                    return val
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                else:
                    df_plot = split_date_fields(df_plot, date_col)
        else:
            print("No date fields detected in the dataset.")

        print("\nGenerating regression plot...")
        x_vals = try_eval(x_input, df_plot)
        y_vals = try_eval(y_input, df_plot)

        if x_vals is not None and y_vals is not None:
            # Drop NA for regression
            data = pd.DataFrame({'X': x_vals, 'Y': y_vals}).dropna()
            if data.empty:
                print("No data available for regression after dropping missing values.")
                return
            x = data['X']
            y = data['Y']
            # Perform regression
            result = linregress(x, y)
            print("\n--- Regression Results ---")
            print(f"Slope: {result.slope:,.2f}")
            print(f"Intercept: {result.intercept:,.2f}")
            print(f"R-squared: {result.rvalue**2:,.2f}")
            print(f"P-value: {result.pvalue:,.2f}")
            print(f"Standard error: {result.stderr:,.2f}")
            print()
            print(f"Regression equation: Y = {result.intercept:,.2f} + {result.slope:,.2f} * X + {result.stderr:,.2f}")

            # Custom plot labels
            print("\n--- Customise your plot ---")
            plot_title = input("Enter plot title (leave blank for default): ").strip()
            x_label = input(f"Enter X-axis label (leave blank for '{x_input}'): ").strip()
            y_label = input(f"Enter Y-axis label (leave blank for '{y_input}'): ").strip()

            final_title = plot_title if plot_title else 'Linear Regression'
            final_x_label = x_label if x_label else x_input
            final_y_label = y_label if y_label else y_input

            # Plot
            plt.figure(figsize=(8, 6))
            plt.scatter(x, y, label='Data', alpha=0.7)
            plt.plot(x, result.intercept + result.slope * x, color='red', label='Regression line')
            plt.xlabel(final_x_label)
            plt.ylabel(final_y_label)
            plt.title(final_title)
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            print("Could not perform regression: invalid X or Y selection.")
    

def main():
    print()
    print("Welcome to YOUR REGRESSION DASHBOARD!")
    df = load_data()
    if df is None:
        print("Failed to load data. Exiting.")
        return
    detected_date_fields = confirm_date_fields(df)
    if df is not None:
        gregression_plot(df, detected_date_fields)

if __name__ == "__main__":
    main()
