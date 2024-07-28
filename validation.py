from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

system = """Double check the user's postgresql query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only."""


def validate_sql_query(llm, prompt):
    # prompt = ChatPromptTemplate.from_messages(
    #     [("system", system), ("human", "{query}")]
    # ).partial(dialect=db.dialect)
    validation_chain = prompt | llm | StrOutputParser()
    return validation_chain
