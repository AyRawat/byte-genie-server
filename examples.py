examples = [
    {
        "input": "List all companies who has employees greater than 100",
        "query": "SELECT company_name FROM company WHERE CAST(n_employees AS REAL) > 100;",
    },
    {
        "input": "Find company names who has employees greater than 100",
        "query": "SELECT company_name FROM company WHERE CAST(n_employees AS REAL) > 100;",
    },
    {
        "input": "Find events that are being attended by the companies whose revenue is above 5 Million",
        "query": """ SELECT DISTINCT e.event_name FROM event e JOIN company c ON e.event_url = c.event_url WHERE CAST(c.company_revenue AS REAL) > 5.0;""",
    },
    {
        "input": "Find companies who are attending AI events",
        "query": """
             SELECT Distinct company_name from company c JOIN event e ON c.event_url = e.event_url WHERE e.event_industry LIKE '%AI%' COLLATE NOCASE;'
        """,
    },
    {
        "input": "Find me events that companies in Pharmaceuticals sector are attending",
        "query": """ 
              Select event_name from event e JOIN company c ON e.event_url = c.event_url where c.company_industry LIKE '%Pharmaceutical%' COLLATE NOCASE;'
     """,
    },
    {
        "input": "Find me companies that are attending Oil & Gas related events over the next 12 months",
        "query": """
      SELECT company_name
FROM company
WHERE event_url IN (
    SELECT e.event_url
    FROM event AS e
    WHERE e.event_industry LIKE '%Oil & Gas%'
    AND (
        DATE(e.event_start_date) BETWEEN DATE('now') AND DATE('now', '+12 months')
        OR DATE(e.event_end_date) BETWEEN DATE('now') AND DATE('now', '+12 months')
    )
);
    """,
    },
    {
        "input": "Find sales people who are working in Tech companies",
        "query": """
       SELECT email FROM people p JOIN company c ON
       p.homepage_base_url = c.homepage_base_url where 
       p.job_title LIKE '%sales%' and 
       c.company_industry LIKE '%software%';
     """,
    },
    {
        "input": "Find sales people for companies that are attending events in Singapore in next 9 months",
        "query": """
           SELECT DISTINCT p.first_name, p.last_name
FROM people p
JOIN company c ON p.homepage_base_url = c.homepage_base_url
JOIN event e ON c.event_url = e.event_url
WHERE p.job_title LIKE '%sales%'
AND e.event_country LIKE '%Singapore%';
        """,
    },
    {
        "input": "Find the email addresses of people working for companies that are attending finance and banking events",
        "query": """
           SELECT DISTINCT p.email
FROM people p
JOIN company c ON p.homepage_base_url = c.homepage_base_url
JOIN events e ON c.event_url = e.event_url
WHERE e.event_industry LIKE '%Finance%' OR e.event_industry LIKE '%Banking%';
        """,
    },
]

from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings


def get_example_selector():
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        Chroma,
        k=2,
        input_keys=["input"],
    )
    return example_selector
