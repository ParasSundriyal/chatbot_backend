# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from chatbot_state import get_user_session, reset_user_session
from classifier import classify_complaint

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    user_id = data.get("user_id", "default")
    token = data.get("token", "")  # <-- Get token from frontend


    # Initialize or get user session
    session = get_user_session(user_id)
    print("session:", session)  # Debug log
    print("message:", message)  # Debug log

    # Step-based form logic
    if session["step"] == "start":
        session["step"] = "title"
        return jsonify({"reply": "Please provide a short title for your grievance."})

    elif session["step"] == "title":
        session["data"]["title"] = message
        session["step"] = "description"
        return jsonify({"reply": "Thanks! Now, please describe the issue in detail."})

    elif session["step"] == "description":
        session["data"]["description"] = message
        session["step"] = "image"
        return jsonify({"reply": "Do you have any images or evidence? If yes, please upload it. If not, type 'no'."})

    elif session["step"] == "image":
        if message.lower() != "no":
            session["data"]["image"] = message  # Handle image as base64 or URL
        else:
            session["data"]["image"] = None

        # Ensure description is available before classifying
        description = session["data"].get("description")
        if not description:
            return jsonify({"reply": "⚠️ Description missing. Please start over."})

        # Classify and store
        session["data"]["category"] = classify_complaint(description)
        print("Classified category:", session["data"]["category"])

        session["step"] = "confirm"

        summary = (
            f"**Please confirm your grievance details:**\n"
            f"Title: {session['data'].get('title', 'N/A')}\n"
            f"Description: {session['data'].get('description', 'N/A')}\n"
            f"Category: {session['data'].get('category', 'general')}\n"
            f"Image: {session['data'].get('image') or 'None'}\n"
            f"Type 'confirm' to submit or 'cancel' to reset the form."
        )
        return jsonify({"reply": summary})


    elif session["step"] == "confirm":
        if message.lower() == "confirm":
            token = data.get("token")
            if not token:
                return jsonify({"reply": "❌ Authentication token is missing."})

            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                }

                res = requests.post(
                    "http://localhost:8080/api/grievances/create",
                    json=session["data"],  # If backend accepts JSON. Otherwise use `data=` or `files=`
                    headers=headers
                )

                if res.status_code == 201:
                    reset_user_session(user_id)
                    return jsonify({"reply": "✅ Your grievance has been submitted successfully!"})
                else:
                    return jsonify({"reply": f"❌ Failed to submit grievance: {res.text}"})

            except Exception as e:
                return jsonify({"reply": f"❌ Error occurred during submission: {str(e)}"})

    elif message.lower() == "cancel":
        reset_user_session(user_id)
        return jsonify({"reply": "🛑 Grievance form has been reset. Start again with the title."})
    else:
        return jsonify({"reply": "⚠️ Please type 'confirm' to submit or 'cancel' to discard."})


    return jsonify({"reply": "Something went wrong. Please start again."})

if __name__ == "__main__":
    app.run(debug=True)
