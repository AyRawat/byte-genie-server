import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from utils.revenue_utils import standardize_revenue
from utils.employee_utils import standardize_n_employees
from utils.industry_utils import standardize_industry

db_user = 'postgres'
db_password = 'postgres'
db_host = 'localhost'
db_port = '5432'
db_name = 'bytegenie'


connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(connection_string)

def check_connection(engine):
    try:
        connection = engine.connect()
        print("Connection to the database was successful")
        connection.close()
    except ConnectionRefusedError as e:
        print("Connection to the database failed", e)

check_connection(engine)

events_df = pd.read_csv('./data/event_info.csv')
people_df = pd.read_csv('./data/people_info.csv')

company_df = pd.read_csv('./data/company_info.csv')
company_df = company_df.copy()



# Apply the function to the revenue column
#df['revenue'] = df['revenue'].apply(standardize_revenue)

# Save the standardized CSV
#df.to_csv('standardized_file.csv', index=False)

unique_industries = company_df['company_industry'].unique()

company_df['n_employees'] = company_df['n_employees'].apply(standardize_n_employees)
company_df['company_revenue'] = company_df['company_revenue'].apply(standardize_revenue)
#company_df['industry'] = company_df['company_industry'].apply(standardize_industry)
# Print the DataFrame to verify standardization
#company_df.to_csv('standardized_company_info.csv', index=False)

# Save the DataFrame to PostgreSQL
company_df.to_sql('company', engine, if_exists='replace', index=False)
events_df.to_sql('events', engine, if_exists='replace', index=False )
people_df.to_sql('people', engine, if_exists='replace', index=False )
print("Data saved to PostgreSQL database.")