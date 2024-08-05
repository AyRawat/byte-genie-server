import pandas as pd
from sqlalchemy import text

from email_utils import generate_email
from employee_utils import standardize_n_employees
from revenue_utils import standardize_revenue
from event_industry_mapper import event_industry_mapper


def normalize_events(db):
    try:
        event_industry_mapper(db)
        mapped_events_csv = pd.read_csv("./mapped_events.csv")
        mapped_events_csv.to_sql("event", db, if_exists="replace", index=False)
    except Exception as e:
        print("Failed to Execute ", e)


def normalize_company(db):
    company_df = pd.read_sql_query("SELECT * FROM company;", db)
    company_df["n_employees"] = company_df["n_employees"].apply(standardize_n_employees)
    company_df["company_revenue"] = company_df["company_revenue"].apply(
        standardize_revenue
    )
    company_df.to_sql("company", db, if_exists="replace", index=False)


def normalize_people(db):
    people_df = pd.read_sql_query("SELECT * FROM people;", db)

    people_df["email"] = people_df.apply(
        lambda row: generate_email(
            row["first_name"],
            row["last_name"],
            row["email_pattern"],
            row["homepage_base_url"],
        ),
        axis=1,
    )

    people_df.to_sql("people", db, if_exists="replace", index=False)

    return people_df


def normalize_tables(db):
    try:
        normalize_company(db)
        normalize_people(db)
        normalize_events(db)
        normalize_events(db)

    except Exception as e:
        print("Failed Normalizing", e)


# def normalize_events(db):
