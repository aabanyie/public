# DATA VISUALISATION DASHBOARD
import os
import csv
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
from scipy.stats import linregress
import numpy as np
import matplotlib.ticker as mticker


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

VIS_OPTIONS = [
        "Line plot",
        "Bar plot",
        "Pie chart",
        "Heatmap",
        "Treemap",
        "Violin plot",
    ]

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


def generate_visualisation(df, detected_date_fields=None):

    def set_xticks_labels(ax, xvals):
        n = len(xvals)
        if n > 30:
            step = max(1, n // 10)
        elif n > 15:
            step = 2
        else:
            step = 1
        tick_idx = list(range(0, n, step))
        try:
            ax.set_xticks([xvals[i] for i in tick_idx])
            ax.set_xticklabels([str(xvals[i]) for i in tick_idx], rotation=45)
        except Exception:
            pass

    # Helper: scale large numbers and return (scaled_vals, scale_label)
    def scale_numeric(vals):
        import numpy as np
        vals = pd.Series(vals)
        if not pd.api.types.is_numeric_dtype(vals):
            return vals, ''
        max_abs = np.nanmax(np.abs(vals))
        if max_abs >= 1_000_000:
            return vals / 1_000_000, "('M)"
        elif max_abs >= 1_000:
            return vals / 1_000, "('000)"
        else:
            return vals, ''

    print("\nSelect a visualisation type:")
    for idx, opt in enumerate(VIS_OPTIONS, 1):
        print(f"{idx}. {opt}")
    try:
        print()
        choice = int(input("Enter the number of the visualisation: "))
        vis_type = VIS_OPTIONS[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    print(f"\nYou selected: {vis_type}")
    columns = list(df.columns)


    def is_date_field(col):
        import warnings
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Could not infer format, so each element will be parsed individually*")
                parsed = pd.to_datetime(df[col], errors='coerce')
            return parsed.notna().mean() > 0.6
        except Exception:
            return False

    def filter_by_date(col):
        # Use split_date_fields for filtering
        return split_date_fields(df, col)

    def is_numeric_field(col):
        return pd.api.types.is_numeric_dtype(df[col])

    # Matplotlib visualisations with enhanced field evaluation
    if vis_type.startswith("Line plot"):
        # 1. Present all columns
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        # 2. Choose X and Y axis (by number or formula)
        print("\nYou can enter a formula using column numbers or column names with valid expressions.")
        print()
        x_input = input("Enter formula or field for X-axis: ").strip()
        y_input = input("Enter formula or field for Y-axis: ").strip()

        def resolve_col(val, col_list=None):
            # If col_list is provided, resolve index in that list; else use columns
            if val.isdigit():
                idx = int(val) - 1
                if col_list is not None:
                    if 0 <= idx < len(col_list):
                        return col_list[idx]
                else:
                    if 0 <= idx < len(columns):
                        return columns[idx]
            return val

        # 3. Ask for date filter (using already detected date fields from confirm_date_fields)
        if detected_date_fields is None:
            detected_date_fields = [col for col in columns if is_date_field(col)]

        df_plot = df
        date_col = None
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                    date_col = None
                else:
                    df_plot = filter_by_date(date_col)
        else:
            print("No date fields detected in the dataset.")

        # 4. Evaluate X and Y (formula or column)
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

        x_vals = try_eval(x_input, df_plot)
        y_vals = try_eval(y_input, df_plot)

        # (Remove duplicate/stray scale_numeric definition)

        # 5. Optionally name axes and graph title
        if x_vals is not None and y_vals is not None:
            print("\n--- Customise your graph ---")
            graph_title = input("Enter graph title (leave blank for default): ").strip()
            print()
            x_label = input(f"Enter X-axis label (leave blank for '{x_input}'): ").strip()
            print()
            y_label = input(f"Enter Y-axis label (leave blank for '{y_input}'): ").strip()

            # If X is categorical and Y is numeric, group by X and sum Y
            # (e.g. Product, formula)
            # Try to detect if x_vals is categorical (object or string dtype, or few unique values)
            if hasattr(x_vals, 'dtype') and (pd.api.types.is_object_dtype(x_vals) or pd.api.types.is_categorical_dtype(x_vals) or (hasattr(x_vals, 'nunique') and x_vals.nunique() < 30)):
                # Group by X and sum Y
                group_df = pd.DataFrame({'X': x_vals, 'Y': y_vals})
                grouped = group_df.groupby('X', dropna=False)['Y'].sum().reset_index()
                # If X is a date or datetime, sort chronologically
                if pd.api.types.is_datetime64_any_dtype(grouped['X']) or pd.api.types.is_timedelta64_dtype(grouped['X']):
                    grouped = grouped.sort_values('X')
                else:
                    # Try to parse as date if possible
                    try:
                        parsed_dates = pd.to_datetime(grouped['X'], errors='coerce')
                        if parsed_dates.notna().sum() > 0:
                            grouped['__parsed'] = parsed_dates
                            grouped = grouped.sort_values('__parsed').drop(columns='__parsed')
                    except Exception:
                        pass
                # Scale Y if needed
                grouped_y, y_scale = scale_numeric(grouped['Y'])
                fig, ax = plt.subplots()
                ax.plot(grouped['X'], grouped_y)
                # Auto-detect tick interval for readability
                n = len(grouped['X'])
                if n > 30:
                    step = max(1, n // 10)
                elif n > 15:
                    step = 2
                else:
                    step = 1
                tick_idx = list(range(0, n, step))
                ax.set_xticks([i for i in tick_idx])
                ax.set_xticklabels([str(grouped['X'].iloc[i]) for i in tick_idx], rotation=35, ha='right')
                ax.set_xlabel((x_label if x_label else x_input))
                ax.set_ylabel((y_label if y_label else y_input) + (f" {y_scale}" if y_scale else ""))
                # Format Y axis with commas if numeric
                if pd.api.types.is_numeric_dtype(grouped_y):
                    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
                ax.set_title(graph_title if graph_title else f"Line plot: {y_input} vs {x_input}")
                plt.tight_layout()
                plt.show()
            else:
                # If X is a date or datetime, sort chronologically
                if pd.api.types.is_datetime64_any_dtype(x_vals) or pd.api.types.is_timedelta64_dtype(x_vals):
                    sort_idx = np.argsort(x_vals)
                    x_vals = np.array(x_vals)[sort_idx]
                    y_vals = np.array(y_vals)[sort_idx]
                else:
                    # Try to parse as date if possible
                    try:
                        parsed_dates = pd.to_datetime(x_vals, errors='coerce')
                        if parsed_dates.notna().sum() > 0:
                            sort_idx = np.argsort(parsed_dates)
                            x_vals = np.array(x_vals)[sort_idx]
                            y_vals = np.array(y_vals)[sort_idx]
                    except Exception:
                        pass
                # Scale X and Y if needed
                x_scaled, x_scale = scale_numeric(x_vals)
                y_scaled, y_scale = scale_numeric(y_vals)
                fig, ax = plt.subplots()
                ax.plot(x_scaled, y_scaled)
                # Format X and Y axes with commas if numeric
                if pd.api.types.is_numeric_dtype(x_scaled):
                    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
                if pd.api.types.is_numeric_dtype(y_scaled):
                    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))
                ax.set_xlabel((x_label if x_label else x_input) + (f" {x_scale}" if x_scale else ""))
                ax.set_ylabel((y_label if y_label else y_input) + (f" {y_scale}" if y_scale else ""))
                ax.set_title(graph_title if graph_title else f"Line plot: {y_input} vs {x_input}")
                plt.tight_layout()
                plt.show()
        else:
            print("Could not plot: invalid X or Y axis selection.")

    elif vis_type.startswith("Bar plot"):
        # 1. Present all columns
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        # 2. Choose X and Y axis (by number or formula)
        print("\nYou can enter a formula using column numbers or column names with valid expressions.")
        print()
        x_input = input("Enter formula or field for X-axis: ").strip()
        y_input = input("Enter formula or field for Y-axis: ").strip()

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

        # 3. Ask for date filter (using already detected date fields from confirm_date_fields)
        if detected_date_fields is None:
            detected_date_fields = [col for col in columns if is_date_field(col)]

        df_plot = df
        date_col = None
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                    date_col = None
                else:
                    df_plot = filter_by_date(date_col)
        else:
            print("No date fields detected in the dataset.")

        # 4. Evaluate X and Y (formula or column)
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

        x_vals = try_eval(x_input, df_plot)
        y_vals = try_eval(y_input, df_plot)

        # 5. Optionally name axes and graph title
        if x_vals is not None and y_vals is not None:
            print("\n--- Customise your graph ---")
            graph_title = input("Enter graph title (leave blank for default): ").strip()
            print()
            x_label = input(f"Enter X-axis label (leave blank for '{x_input}'): ").strip()
            print()
            y_label = input(f"Enter Y-axis label (leave blank for '{y_input}'): ").strip()

            # If X is categorical and Y is numeric, group by X and sum Y
            if hasattr(x_vals, 'dtype') and (pd.api.types.is_object_dtype(x_vals) or pd.api.types.is_categorical_dtype(x_vals) or (hasattr(x_vals, 'nunique') and x_vals.nunique() < 30)):
                group_df = pd.DataFrame({'X': x_vals, 'Y': y_vals})
                grouped = group_df.groupby('X', dropna=False)['Y'].sum().reset_index()
                # If X is a date or datetime, sort chronologically
                if pd.api.types.is_datetime64_any_dtype(grouped['X']) or pd.api.types.is_timedelta64_dtype(grouped['X']):
                    grouped = grouped.sort_values('X')
                else:
                    # Try to parse as date if possible
                    try:
                        parsed_dates = pd.to_datetime(grouped['X'], errors='coerce')
                        if parsed_dates.notna().sum() > 0:
                            grouped['__parsed'] = parsed_dates
                            grouped = grouped.sort_values('__parsed').drop(columns='__parsed')
                    except Exception:
                        pass
                grouped_y, y_scale = scale_numeric(grouped['Y'])
                fig, ax = plt.subplots()
                ax.bar(grouped['X'], grouped_y)
                n = len(grouped['X'])
                if n > 30:
                    step = max(1, n // 10)
                elif n > 15:
                    step = 2
                else:
                    step = 1
                tick_idx = list(range(0, n, step))
                ax.set_xticks([i for i in tick_idx])
                ax.set_xticklabels([str(grouped['X'].iloc[i]) for i in tick_idx], rotation=35, ha='right')
                ax.set_xlabel((x_label if x_label else x_input))
                ax.set_ylabel((y_label if y_label else y_input) + (f" {y_scale}" if y_scale else ""))
                if pd.api.types.is_numeric_dtype(grouped_y):
                    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
                ax.set_title(graph_title if graph_title else f"Bar plot: {y_input} vs {x_input}")
                plt.tight_layout()
                plt.show()
            else:
                # If X is a date or datetime, sort chronologically
                if pd.api.types.is_datetime64_any_dtype(x_vals) or pd.api.types.is_timedelta64_dtype(x_vals):
                    sort_idx = np.argsort(x_vals)
                    x_vals = np.array(x_vals)[sort_idx]
                    y_vals = np.array(y_vals)[sort_idx]
                else:
                    # Try to parse as date if possible
                    try:
                        parsed_dates = pd.to_datetime(x_vals, errors='coerce')
                        if parsed_dates.notna().sum() > 0:
                            sort_idx = np.argsort(parsed_dates)
                            x_vals = np.array(x_vals)[sort_idx]
                            y_vals = np.array(y_vals)[sort_idx]
                    except Exception:
                        pass
                x_scaled, x_scale = scale_numeric(x_vals)
                y_scaled, y_scale = scale_numeric(y_vals)
                fig, ax = plt.subplots()
                ax.bar(x_scaled, y_scaled)
                if pd.api.types.is_numeric_dtype(x_scaled):
                    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
                if pd.api.types.is_numeric_dtype(y_scaled):
                    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))
                ax.set_xlabel((x_label if x_label else x_input) + (f" {x_scale}" if x_scale else ""))
                ax.set_ylabel((y_label if y_label else y_input) + (f" {y_scale}" if y_scale else ""))
                ax.set_title(graph_title if graph_title else f"Bar plot: {y_input} vs {x_input}")
                plt.tight_layout()
                plt.show()
        else:
            print("Could not plot: invalid X or Y axis selection.")

    elif vis_type.startswith("Pie chart"):

        # 1. Present all columns
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        # 2. Choose X and Y axis (by number or formula)
        print("\nYou can enter a formula using column numbers or column names with valid expressions.")
        print()
        x_input = input("Enter field to group by: ").strip()
        y_input = input("Enter formula or field for aggregation: ").strip()

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

        # 3. Ask for date filter (using already detected date fields from confirm_date_fields)
        if detected_date_fields is None:
            detected_date_fields = [col for col in columns if is_date_field(col)]

        df_plot = df
        date_col = None
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                    date_col = None
                else:
                    # Only filter the records to be considered, do not group by date field
                    df_plot = filter_by_date(date_col)
        else:
            print("No date fields detected in the dataset.")

        # 4. Evaluate X and Y (formula or column)
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

        x_vals = try_eval(x_input, df_plot)
        y_vals = try_eval(y_input, df_plot)

        # 5. Optionally name graph title
        if x_vals is not None and y_vals is not None:
            print("\n--- Customise your graph ---")
            graph_title = input("Enter graph title (leave blank for default): ").strip()

            # If X is categorical and Y is numeric, group by X and sum Y
            if hasattr(x_vals, 'dtype') and (pd.api.types.is_object_dtype(x_vals) or pd.api.types.is_categorical_dtype(x_vals) or (hasattr(x_vals, 'nunique') and x_vals.nunique() < 30)):
                group_df = pd.DataFrame({'X': x_vals, 'Y': y_vals})
                grouped = group_df.groupby('X', dropna=False)['Y'].sum().reset_index()
                # If X is a date or datetime, sort chronologically
                if pd.api.types.is_datetime64_any_dtype(grouped['X']) or pd.api.types.is_timedelta64_dtype(grouped['X']):
                    grouped = grouped.sort_values('X')
                else:
                    # Try to parse as date if possible, suppressing warning
                    import warnings
                    try:
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", message="Could not infer format, so each element will be parsed individually*")
                            parsed_dates = pd.to_datetime(grouped['X'], errors='coerce')
                        if parsed_dates.notna().sum() > 0:
                            grouped['__parsed'] = parsed_dates
                            grouped = grouped.sort_values('__parsed').drop(columns='__parsed')
                    except Exception:
                        pass
                grouped_y, y_scale = scale_numeric(grouped['Y'])
                fig, ax = plt.subplots()
                ax.pie(grouped_y, labels=grouped['X'], autopct='%1.1f%%', startangle=90, counterclock=False)
                ax.set_title(graph_title if graph_title else f"Pie chart: {y_input} by {x_input}")
                plt.tight_layout()
                plt.show()
            else:
                # If X is a date or datetime, sort chronologically
                if pd.api.types.is_datetime64_any_dtype(x_vals) or pd.api.types.is_timedelta64_dtype(x_vals):
                    sort_idx = np.argsort(x_vals)
                    x_vals = np.array(x_vals)[sort_idx]
                    y_vals = np.array(y_vals)[sort_idx]
                else:
                    # Try to parse as date if possible
                    try:
                        parsed_dates = pd.to_datetime(x_vals, errors='coerce')
                        if parsed_dates.notna().sum() > 0:
                            sort_idx = np.argsort(parsed_dates)
                            x_vals = np.array(x_vals)[sort_idx]
                            y_vals = np.array(y_vals)[sort_idx]
                    except Exception:
                        pass
                fig, ax = plt.subplots()
                ax.pie(y_vals, labels=x_vals, autopct='%1.1f%%', startangle=90, counterclock=False)
                ax.set_title(graph_title if graph_title else f"Pie chart: {y_input} by {x_input}")
                plt.tight_layout()
                plt.show()
        else:
            print("Could not plot: invalid X or Y axis selection.")

    elif vis_type.startswith("Heatmap"):
        # 1. Present all columns
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        # 2. Choose X, Y, and Value axis (by number or formula)
        print("\nYou can enter a formula using column numbers or column names with valid expressions.")
        print()
        x_input = input("Enter field for X-axis (horizontal): ").strip()
        y_input = input("Enter field for Y-axis (vertical): ").strip()
        v_input = input("Enter field for cell values (numeric): ").strip()

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

        # 3. Ask for date filter (using already detected date fields from confirm_date_fields)
        if detected_date_fields is None:
            detected_date_fields = [col for col in columns if is_date_field(col)]

        df_plot = df
        date_col = None
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                    date_col = None
                else:
                    df_plot = filter_by_date(date_col)
        else:
            print("No date fields detected in the dataset.")

        # 4. Evaluate X, Y, and Value (formula or column)
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

        x_vals = try_eval(x_input, df_plot)
        y_vals = try_eval(y_input, df_plot)
        v_vals = try_eval(v_input, df_plot)

        # 5. Optionally name axes and graph title
        if x_vals is not None and y_vals is not None and v_vals is not None:
            print("\n--- Customise your graph ---")
            graph_title = input("Enter graph title (leave blank for default): ").strip()
            print()
            x_label = input(f"Enter X-axis label (leave blank for '{x_input}'): ").strip()
            print()
            y_label = input(f"Enter Y-axis label (leave blank for '{y_input}'): ").strip()

            # Build pivot table for heatmap
            heatmap_df = pd.DataFrame({'X': x_vals, 'Y': y_vals, 'V': v_vals})
            pivot = heatmap_df.pivot_table(index='Y', columns='X', values='V', aggfunc='sum', fill_value=0)

            # Sort X and Y if they are dates, suppressing pandas format warning
            def try_sort(vals):
                import warnings
                if pd.api.types.is_datetime64_any_dtype(vals) or pd.api.types.is_timedelta64_dtype(vals):
                    return vals.sort_values()
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="Could not infer format, so each element will be parsed individually*")
                        parsed = pd.to_datetime(vals, errors='coerce')
                    if parsed.notna().sum() > 0:
                        return vals.iloc[np.argsort(parsed)]
                except Exception:
                    pass
                return vals
            pivot = pivot.loc[try_sort(pivot.index)]
            pivot = pivot[try_sort(pivot.columns)]

            fig, ax = plt.subplots(figsize=(max(8, len(pivot.columns)*0.5), max(6, len(pivot.index)*0.5)))
            sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlGnBu', ax=ax)
            ax.set_xlabel(x_label if x_label else x_input)
            ax.set_ylabel(y_label if y_label else y_input)
            ax.set_title(graph_title if graph_title else f"Heatmap: {v_input} by {y_input} vs {x_input}")
            plt.tight_layout()
            plt.show()
        else:
            print("Could not plot: invalid X, Y, or Value selection.")

    elif vis_type.startswith("Treemap"):
        # 1. Present all columns
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        # 2. Choose Category and Value axis (by number or formula)
        print("\nYou can enter a formula using column numbers or column names with valid expressions.")
        print()
        cat_input = input("Enter field for category (grouping): ").strip()
        val_input = input("Enter field for size/value (numeric): ").strip()

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

        # 3. Ask for date filter (using already detected date fields from confirm_date_fields)
        if detected_date_fields is None:
            detected_date_fields = [col for col in columns if is_date_field(col)]

        df_plot = df
        date_col = None
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                    date_col = None
                else:
                    df_plot = filter_by_date(date_col)
        else:
            print("No date fields detected in the dataset.")

        # 4. Evaluate Category and Value (formula or column)
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

        cat_vals = try_eval(cat_input, df_plot)
        val_vals = try_eval(val_input, df_plot)

        # 5. Optionally name axes and graph title
        if cat_vals is not None and val_vals is not None:
            print("\n--- Customise your graph ---")
            graph_title = input("Enter graph title (leave blank for default): ").strip()
            print()
            cat_label = input(f"Enter category label (leave blank for '{cat_input}'): ").strip()
            print()
            val_label = input(f"Enter value label (leave blank for '{val_input}'): ").strip()

            # Group by category and sum values
            group_df = pd.DataFrame({'Category': cat_vals, 'Value': val_vals})
            grouped = group_df.groupby('Category', dropna=False)['Value'].sum().reset_index()

            # Sort categories if they are dates
            import warnings
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message="Could not infer format, so each element will be parsed individually*")
                    parsed_dates = pd.to_datetime(grouped['Category'], errors='coerce')
                if parsed_dates.notna().sum() > 0:
                    grouped['__parsed'] = parsed_dates
                    grouped = grouped.sort_values('__parsed').drop(columns='__parsed')
            except Exception:
                pass

            # Scale values if needed
            grouped_val, val_scale = scale_numeric(grouped['Value'])

            fig, ax = plt.subplots(figsize=(max(8, len(grouped['Category']) * 0.4), 6))
            squarify.plot(sizes=grouped_val, label=[str(c) for c in grouped['Category']], alpha=0.8, ax=ax)
            ax.set_xlabel(cat_label if cat_label else cat_input)
            ax.set_ylabel(val_label if val_label else val_input + (f" {val_scale}" if val_scale else ""))
            ax.set_title(graph_title if graph_title else f"Treemap: {val_input} by {cat_input}")
            plt.axis('off')
            plt.tight_layout()
            plt.show()
        else:
            print("Could not plot: invalid category or value selection.")

    elif vis_type.startswith("Violin plot"):
        # 1. Present all columns
        print("\nAvailable columns:")
        for idx, col in enumerate(columns, 1):
            print(f"{idx}. {col}")

        # 2. Choose Category and Value axis (by number or formula)
        print("\nYou can enter a formula using column numbers or column names with valid expressions.")
        print()
        cat_input = input("Enter field for category (grouping): ").strip()
        val_input = input("Enter field for value (numeric): ").strip()

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

        # 3. Ask for date filter (using already detected date fields from confirm_date_fields)
        if detected_date_fields is None:
            detected_date_fields = [col for col in columns if is_date_field(col)]

        df_plot = df
        date_col = None
        if detected_date_fields:
            print()
            date_filter_choice = input("Do you want to filter by a date field? (y/n): ").strip().lower()
            if date_filter_choice == 'y':
                print("\n\U0001F4C5 Fields detected as dates:")
                for idx, col in enumerate(detected_date_fields, 1):
                    print(f"{idx}. {col}")
                print()
                date_col_input = input("Enter date field to filter by (name or number): ").strip()
                date_col = resolve_col(date_col_input, detected_date_fields)
                if date_col not in detected_date_fields:
                    print("Invalid date field. Proceeding without date filter.")
                    date_col = None
                else:
                    df_plot = filter_by_date(date_col)
        else:
            print("No date fields detected in the dataset.")

        # 4. Evaluate Category and Value (formula or column)
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

        cat_vals = try_eval(cat_input, df_plot)
        val_vals = try_eval(val_input, df_plot)

        # 5. Optionally name axes and graph title
        if cat_vals is not None and val_vals is not None:
            print("\n--- Customise your graph ---")
            graph_title = input("Enter graph title (leave blank for default): ").strip()
            print()
            cat_label = input(f"Enter category label (leave blank for '{cat_input}'): ").strip()
            print()
            val_label = input(f"Enter value label (leave blank for '{val_input}'): ").strip()

            # Prepare DataFrame for violin plot
            plot_df = pd.DataFrame({'Category': cat_vals, 'Value': val_vals})

            fig, ax = plt.subplots(figsize=(max(8, len(plot_df['Category'].unique()) * 0.5), 6))
            sns.violinplot(x='Category', y='Value', data=plot_df, ax=ax, inner='box')
            ax.set_xlabel(cat_label if cat_label else cat_input)
            ax.set_ylabel(val_label if val_label else val_input)
            ax.set_title(graph_title if graph_title else f"Violin plot: {val_input} by {cat_input}")
            plt.tight_layout()
            plt.show()
        else:
            print("Could not plot: invalid category or value selection.")

    else:
        print("\nThis visualisation type is not yet implemented.")        

def main():
    print()
    print("Welcome to YOUR ANALYTICS DASHBOARD!")
    df = load_data()
    if df is None:
        print("Failed to load data. Exiting.")
        return
    detected_date_fields = confirm_date_fields(df)
    if df is not None:
        generate_visualisation(df, detected_date_fields=detected_date_fields)

if __name__ == "__main__":
    main()
