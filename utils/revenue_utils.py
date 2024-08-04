import pandas as pd
import numpy as np

# Function to convert revenue values to millions


def standardize_revenue(revenue):
    print("the value of revenue", revenue)
    if pd.isna(revenue) or revenue == "null" or revenue == "0.0":
        return 0.0
    revenue = str(revenue)
    revenue = revenue.replace("$", "").replace(",", "")
    if "billion" in revenue.lower():
        return float(revenue.replace(" billion", "")) * 1000
    elif "million" in revenue.lower():
        return float(revenue.replace(" million", ""))
    else:
        return float(revenue)
