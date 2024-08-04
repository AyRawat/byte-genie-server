from langchain.tools import tool, StructuredTool
from utils.table_details import table_details
from datetime import datetime
import json


def get_table_description():
    print("The table details", json.dumps(table_details))
    return json.dumps(table_details)


def get_today_date(query: str) -> str:
    today_date_string = datetime.now().strftime("%Y-%m-%d")
    return today_date_string


def sql_agent_tools():
    tools = [
        StructuredTool.from_function(
            func=get_table_description,
            name="get_table_description",
            description="""
         Useful to get  the description about each table and the columns inside it
            
        """,
        ),
        StructuredTool.from_function(
            func=get_today_date,
            name="get_today_date",
            description="""
            Useful to get the date of today
            """,
        ),
    ]
    return tools
