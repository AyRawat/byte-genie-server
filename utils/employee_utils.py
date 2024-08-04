import pandas as pd
import numpy as np


def standardize_n_employees(value):
    if pd.isna(value) or value == "":
        return 0

    value = str(value)

    # Remove unnecessary characters
    value = value.replace(" employees", "").replace(",", "")

    # Handle ranges like '11-50'
    if "-" in value:
        start, end = value.split("-")
        return int((int(start) + int(end)) / 2)

    # Handle values like '10,001+'
    elif "+" in value:
        return int(value.replace("+", ""))

    # Handle single numeric values and remove .0
    else:
        return int(float(value))
