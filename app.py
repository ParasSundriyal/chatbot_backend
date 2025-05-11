from flask import Flask, request, jsonify
from flask_cors import CORS
from classifier import classify_complaint

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")
    category, reply = classify_complaint(msg)
    return jsonify({"reply": reply, "category": category})

# Only for development
if __name__ == "__main__":
    app.run(debug=True)
