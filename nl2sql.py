import os, sys
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from utils.load_config import LoadConfig
from utils.table_details import table_chain as select_table
from prompts import full_prompt
from tools.sql_agent_tools import sql_agent_tools
from dotenv import load_dotenv


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Load environment variables from .env file
load_dotenv(override=True)

# Set the environment variable for OpenAI API key if needed
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# Initialize the SQLDatabase object
APPCFG = LoadConfig()
db_path = APPCFG.stored_csv_sqldb_directory
db_path = f"sqlite:///{db_path}"
engine = create_engine(db_path)
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    if tables:
        print("Connection successful. Tables in the database:", tables)
    else:
        print("Connection successful, but no tables found.")
Session = sessionmaker(bind=engine)
session = Session()


def get_agent(memory):
    print("creating agent")
    db = SQLDatabase(engine=engine)
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
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
        response = agent.invoke({"input": question, "top_k": 3})
        memory.chat_memory.add_user_message(question)
        memory.chat_memory.add_ai_message(response["output"])
        return response["output"]
    except Exception as e:
        print("error", e)


session.close()
