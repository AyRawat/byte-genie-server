from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from nl2sql import invoke_chain

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

@app.route('/')
@cross_origin
def hello():
    return 'Welcome'

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    print(data)
    
    question = data.get('question')
    messages = data.get('history')
    print(question);
    if not question:
        return jsonify({"error": "Missing 'question' "}), 400
    if not messages:
        messages = [
             {"role": "user", "content": "Previous user message"},
             {"role": "assistant", "content": "Previous AI response"}
         ]
    try:
        response = invoke_chain(question, messages)
        print("the response", response)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500