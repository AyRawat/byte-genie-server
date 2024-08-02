import os
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from langchain.chains import create_sql_query_chain
from sqlalchemy.orm import sessionmaker
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from utils.table_details import table_chain as select_table
from prompts import final_prompt, answer_prompt
from prompts_test import full_prompt, custom_suffix
from tools.sql_agent_tools import sql_agent_tools
from constants import chat_openai_model_kwargs, langchain_chat_kwargs
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


def get_chat_openai(model_name):
    llm = ChatOpenAI(
        model_name=model_name,
        model_kwargs=chat_openai_model_kwargs**langchain_chat_kwargs,
    )
    return llm


def get_agent(memory):
    print("creating agent")
    db = SQLDatabase.from_uri(connection_string)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-1106", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_tools = sql_agent_tools()
    agent_executor = create_sql_agent(
        llm,
        toolkit=toolkit,
        prompt=full_prompt,
        verbose=True,
        agent_type="openai-tools",
        extra_tools=agent_tools,
        agent_executor_kwargs={"memory": memory, "return_intermediate_steps": True},
    )
    return agent_executor


def get_chain():
    db = SQLDatabase.from_uri(connection_string)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-1106", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    )
    generate_query = create_sql_query_chain(llm, db, final_prompt)
    execute_query = QuerySQLDataBaseTool(db=db)

    rephrase_answer = answer_prompt | llm | StrOutputParser()
    # chain = generate_query | execute_query
    print("generate Query", generate_query)

    # print("the result fo the second query", second_query)
    chain = (
        RunnablePassthrough.assign(table_names_to_use=select_table)
        | RunnablePassthrough.assign(query=generate_query).assign(
            result=itemgetter("query") | execute_query
        )
        | rephrase_answer
    )
    return chain


def create_history(messages):
    print("The messages ->", messages)
    history = ChatMessageHistory()
    for message in messages:
        if "content" not in message or message["content"] == None:
            message["content"] = "previous AI message"
        if message["role"] == "user":
            history.add_user_message(message["content"])
        else:
            history.add_ai_message(message["content"])
    return history


def create_memory(messages):
    print("The messages ->", messages)
    memory = ConversationBufferMemory(
        input_key="input",
        output_key="output",
        memory_key="chat_history",
        return_messages=True,
    )

    for message in messages:
        if "content" not in message or message["content"] == None:
            message["content"] = "previous AI message"
        if message["role"] == "user":
            memory.chat_memory.add_user_message(message["content"])
        else:
            memory.chat_memory.add_ai_message(message["content"])
    return memory


def invoke_agent(question, messages):
    try:
        print("question ", question)
        memory = create_memory(messages)
        agent = get_agent(memory)
        print("reached here Histort -> ", memory)
        response = agent.invoke({"input": question, "top_k": 3})
        print("The response from the agent", response)
        memory.chat_memory.add_user_message(question)
        memory.chat_memory.add_ai_message(response["output"])
        return response["output"]
    except Exception as e:
        print("error", e)


def invoke_chain(question, messages):
    print("Messages ->  ", messages)
    chain = get_chain()
    history = create_history(messages)
    # messages = [
    #     {"role": "user", "content": "Previous user message"},
    #     {"role": "assistant", "content": "Previous AI response"},
    # ]
    response = chain.invoke(
        {"question": question, "top_k": 3, "messages": history.messages}
    )
    # history.add_user_message(question)
    # history.add_ai_message(response)
    return response


# # Sample invocation
# messages = [
#     {"role": "user", "content": "Previous user message"},
#     {"role": "assistant", "content": "Previous AI response"}
# ]

# resp = invoke_chain("Give me the name of the companies who are attending AI events",messages)
# print(resp)
session.close()
