import pandas as pd
import numpy as np

# Function to convert revenue values to millions


def standardize_revenue(revenue):
    if pd.isna(revenue) or revenue.lower() == "null":
        return np.nan
    revenue = revenue.replace("$", "").replace(",", "")
    if "billion" in revenue.lower():
        return float(revenue.replace(" billion", "")) * 1000
    elif "million" in revenue.lower():
        return float(revenue.replace(" million", ""))
    else:
        return float(revenue)
