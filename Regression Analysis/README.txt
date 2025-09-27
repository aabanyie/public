REGRESSION ANALYSIS DASHBOARD
------------------------------

OVERVIEW
This script provides an interactive command-line dashboard for performing linear regression analysis 
on tabular datasets (CSV, TXT, Excel). It guides users through data loading, date field detection, 
filtering, regression calculation, and visualization, with customizable plot labels and robust error handling.

FEATURES
- Flexible Data Loading:
	- Supports CSV, TXT (auto-detects delimiter), and Excel files.
	- Interactive directory and file selection.

- Date Field Detection & Filtering:
	- Auto-detects date columns based on user-specified format.
	- Allows filtering by year, month, day of week, or combinations.

- Regression Analysis:
	- Select independent (X) and dependent (Y) variables by name or formula.
	- Calculates slope, intercept, R-squared, p-value, and standard error.
	- Displays regression equation with error term.

- Customizable Plot Labels:
	- Users can set plot title, X-axis, and Y-axis labels interactively.

- Robust Error Handling:
	- Handles missing data, invalid selections, and unsupported formats gracefully.

DEPENDENCIES
- Python 3.7+
- pandas
- numpy
- matplotlib
- scipy

Install dependencies with:
```bash
pip install pandas numpy matplotlib scipy
```

FILE STRUCTURE
- 'Regression_Analysis.py' — Main script
- 'README.txt' — Documentation

NOTES
- The script is designed for interactive use in a terminal.
- For best results, ensure your data columns are clean and properly formatted.
- Date filtering is optional but recommended for time series analysis.

License
MIT License

---
For questions, please contact aabanyie@gmail.com


