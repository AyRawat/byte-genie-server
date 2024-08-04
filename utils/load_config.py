import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
import shutil
from langchain_openai import ChatOpenAI
import openai

print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        self.load_directories(app_config=app_config)
        self.load_llm_configs(app_config=app_config)
        self.load_openai_models()

    def load_directories(self, app_config):
        self.stored_csv_directory = here(
            app_config["directories"]["stored_csv_directory"]
        )
        self.sqldb_directory = str(here(app_config["directories"]["sqldb_directory"]))
        self.uploaded_files_sqldb_directory = str(
            here(app_config["directories"]["uploaded_files_sqldb_directory"])
        )
        self.stored_csv_sqldb_directory = str(
            here(app_config["directories"]["stored_csv_sqldb_directory"])
        )
        self.persist_directory = app_config["directories"]["persist_directory"]

    def load_llm_configs(self, app_config):

        # self.model_name = os.getenv("gpt_deployment_name")
        self.model_name = os.environ["OPENAI_MODEL_NAME"]
        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]
        self.embedding_model_name = os.getenv("embed_deployment_name")

    def load_openai_models(self):
        openai_api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = openai_api_key
        self.openai_client = openai

        self.langchain_llm = ChatOpenAI(
            model=self.model_name,
            api_key=openai_api_key,
            temperature=self.temperature,
        )

    def remove_directory(self, directory_path: str):
        """
        Removes the specified directory.

        Parameters:
            directory_path (str): The path of the directory to be removed.

        Raises:
            OSError: If an error occurs during the directory removal process.

        Returns:
            None
        """
        if os.path.exists(directory_path):
            try:
                shutil.rmtree(directory_path)
                print(
                    f"The directory '{directory_path}' has been successfully removed."
                )
            except OSError as e:
                print(f"Error: {e}")
        else:
            print(f"The directory '{directory_path}' does not exist.")
