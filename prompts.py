from examples import get_example_selector
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
)

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}\nSQLQuery:"),
        ("ai", "{query}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    example_selector=get_example_selector(),
    input_variables=["input", "top_k"],
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a postgresql expert.
            Given an input question, create a syntactically correct postgresql query to run. Unless otherwise specificed.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding PostgreSQL queries.
            Unless the user specifies in the question a specific number of examples to obtain, query for atmost 5 results using the LIMIT clause as per postgresql. 
            Never query for all columns from a table. You must query only the columns that are needed to answer the question. Pay attention to use only the column names you can see in {table_info}. You might have to join these tables to get the result.
            

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only.
            """,
        ),
        few_shot_prompt,
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{input}"),
    ]
)

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding postgresql query, and postgresql result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)
