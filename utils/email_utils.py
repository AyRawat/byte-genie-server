from openai import OpenAI
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv(override=True)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_email(first_name, last_name, email_pattern, homepage_base_url):
    try:

        prompt = f"""
    Generate an email address based on the given pattern, there can be different type of patterns and details: 
     here are some examples for your referece
     
    Example: If a person's first_name is john, last_name is doe and the pattern is [first].[last] and URL is test.com, then the email should be john.doe@test.com
    Example 2: If a person's first_name is john, last_name is doe and the pattern is [first_initial].[last] and URL is test.com, then the email should be j.doe@test.com
    
   
    First Name: {first_name}
    Last Name: {last_name}
    Email Pattern: {email_pattern}
    Homepage Base URL: {homepage_base_url}
    
     """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can generate email from a particular pattern and concatenate it with the given url to form a valid email and output it as JSON in which there is a specific key called email",
                },
                {"role": "user", "content": prompt},
            ],
        )
        generated_email = response.choices[0].message.content.strip()
        email = json.loads(generated_email)["email"]
        print("The email -> ", email)
        return email

    except Exception as e:
        logging.error(f"Error generating email for {first_name} {last_name}: {e}")
        return None
