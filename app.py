from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from nl2sql import invoke_agent
import logging

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
@cross_origin
def hello():
    return "Welcome"


@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    print(data)

    question = data.get("question")
    messages = data.get("history")
    print(question)
    if not question:
        return jsonify({"error": "Missing 'question' "}), 400
    if not messages:
        messages = [
            {"role": "user", "content": "Previous user message"},
            {"role": "assistant", "content": "Previous AI response"},
        ]
    try:
        response = invoke_agent(question, messages)
        print("the response", response)
        logger.info(f"Question: {question}, Response: {response}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(ssl_context=("cert.pem", "key.pem"))
