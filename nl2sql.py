import os
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from langchain.chains import create_sql_query_chain
from sqlalchemy.orm import sessionmaker
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from utils.table_details import table_chain as select_table
from prompts import final_prompt, answer_prompt, validation_prompt

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Set the environment variable for OpenAI API key if needed
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# Database credentials
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT", 5432)  # Default port for PostgreSQL

# Create the connection string for PostgreSQL
connection_string = (
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Initialize the SQLAlchemy engine
engine = create_engine(connection_string)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Initialize the SQLDatabase object


def get_chain():
    print("Creating chain")
    db = SQLDatabase.from_uri(connection_string)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-1106", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    )
    generate_query = create_sql_query_chain(llm, db, final_prompt)
    validate_query = validation_prompt | llm | StrOutputParser()
    execute_query = QuerySQLDataBaseTool(db=db)

    rephrase_answer = answer_prompt | llm | StrOutputParser()
    # chain = generate_query | execute_query
    print("generate Query", generate_query)

    # print("the result fo the second query", second_query)
    chain = (
        RunnablePassthrough.assign(table_names_to_use=select_table)
        | RunnablePassthrough.assign(query=generate_query).assign(
            result=itemgetter("query") | validate_query | execute_query
        )
        | rephrase_answer
    )
    return chain


def create_history(messages):
    history = ChatMessageHistory()
    for message in messages:
        if message["role"] == "user":
            history.add_user_message(message["content"])
        else:
            history.add_ai_message(message["content"])
    return history


def invoke_chain(question, messages):
    print("question ", question)
    chain = get_chain()
    history = create_history(messages)
    response = chain.invoke(
        {"question": question, "top_k": 3, "messages": history.messages}
    )
    history.add_user_message(question)
    history.add_ai_message(response)
    return response


# # Sample invocation
# messages = [
#     {"role": "user", "content": "Previous user message"},
#     {"role": "assistant", "content": "Previous AI response"}
# ]

# resp = invoke_chain("Give me the name of the companies who are attending AI events",messages)
# print(resp)
session.close()
