from typing import List
from dotenv import load_dotenv
import pandas as pd
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_openai import ChatOpenAI
import os
from operator import itemgetter

load_dotenv(override=True)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

def get_table_details():
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir,"../data/table_description.csv")
    table_description = pd.read_csv(csv_path)
    table_details = ""
    for index , row in table_description.iterrows():
        table_details  = table_details + "Table Name:" + row['Table'] + "\n" + "Table Description"+ row['Description'] + "\n\n"
        
    return table_details

class Table(BaseModel) :
    """Table in SQL database."""
    
    name: str = Field(description="Name of table in SQL database.")
    

def get_tables(tables: List[Table]) -> List[str]:
    tables = [table.name for table in tables]
    return tables

table_details = get_table_details()
table_details_prompt = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
The tables are:

{table_details}

Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""
table_chain = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt) | get_tables