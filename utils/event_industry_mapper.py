import pandas as pd
import re
from tqdm import tqdm
import os
import ast
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text


def event_industry_mapper(db):
    try:
        event_df = pd.read_sql_query("SELECT * FROM event", db)

        tqdm.pandas(desc="Mapping Events")
        event_df["event_industry"] = event_df.progress_apply(
            lambda row: map_event_to_industry(
                row["event_name"], row["event_description"], row["event_url"]
            ),
            axis=1,
        )
        event_df["event_industry"] = event_df["event_industry"].apply(extract_industry)
        # created the file to avoid repeated LLM calls.
        csv_file_path = "./mapped_events.csv"
        event_df.to_csv(csv_file_path, index=False)

    except Exception as e:
        print("failed to map industry", e)


def normalize_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"[^a-z0-9& ]+", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces
    return text.strip()


def extract_industry(industry_str):
    try:
        industry_dict = ast.literal_eval(industry_str)
        return industry_dict.get("industry", "Unknown")
    except (ValueError, SyntaxError):
        return "Unknown"


def here(path):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def get_normalized_industry_list():
    db_path = str(here("../data")) + "/csv_sqldb.db"
    db_path = f"sqlite:///{db_path}"
    db = create_engine(db_path)
    with db.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        for row in result:
            print("Connection successful, query result:", row)

    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    company_df = pd.read_sql_query("SELECT * FROM company;", db)
    industry_list = company_df["company_industry"].dropna().unique().tolist()
    normalized_industries_set = set()

    for industries in industry_list:
        for industry in industries.split(","):
            normalized_industries_set.add(normalize_text(industry))

    # Apply normalization
    normalized_industries = list(normalized_industries_set)
    return normalized_industries


def map_event_to_industry(
    event_name,
    event_description,
    event_url,
):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    normalized_industries = get_normalized_industry_list()
    example_event_name = "eCommerce Expo Asia"
    example_event_description = "eCommerce Expo Asia provides a platform for businesses to discover cutting-edge solutions, forge meaningful connections, and gain valuable insights to thrive in the ever-evolving ecommerce ecosystem."
    example_event_industry = "ecommerce"
    example_event_url = "https://www.ecommerceexpoasia.com/"

    prompt = f"""
    Given the event name and event details, identify the most relevant industry from the list below, There is also an example for your reference:

    Example:
     Event Name: {example_event_name}
     Event Description: {example_event_description}
     Event Url: {example_event_url}
     Industries: {example_event_industry}

    Now, generate the result for the following event

    Event Name: {event_name}
    Event Description: {event_description}
    Event Url: {event_url}

    Industries: {', '.join(normalized_industries)}

    Return only the industry name that best matches the event.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant trained to choose from multiple industries, and mapping the most relevant industry to a particular event and output it as JSON in which there is a specific key called industry",
                },
                {"role": "user", "content": prompt},
            ],
        )
        industry = response.choices[0].message.content
        print("Selected Industry --> ", industry)
        return industry
    except Exception as e:
        print(f"General Error: {e}")
        return "Unknown"
