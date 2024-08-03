from utils.prepare_db_from_csv import PrepareSQLFromTabularData
from utils.load_config import LoadConfig

APPCFG = LoadConfig()

if __name__ == "__main__":
    print(__package__)
    print("Main")
    prep_sql_instance = PrepareSQLFromTabularData(APPCFG.stored_csv_directory)
    prep_sql_instance.run_pipeline()
