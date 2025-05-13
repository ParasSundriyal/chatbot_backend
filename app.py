from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from chatbot_state import get_user_session, reset_user_session
from classifier import classify_complaint

app = Flask(__name__)
CORS(app)



# Keywords to detect grievance intent
GRIEVANCE_KEYWORDS = {"complaint", "grievance", "problem", "defect"}
STATUS_KEYWORDS = {"status", "progress", "grievance status", "check status", "category", "assigned", "department", "track", "track grievance"}
GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.form.get("user_id") or request.json.get("user_id")
    token = request.form.get("token") or request.json.get("token")
    message = request.form.get("message") or request.json.get("message")
    message_lower = message.lower().strip() if message else ""

    session = get_user_session(user_id)
    step = session["step"]

    # Step 1: User starts with intent
    if step == "start":
        if any(keyword in message_lower for keyword in GRIEVANCE_KEYWORDS):
            session["step"] = "title"
            return jsonify({"reply": "Please provide a short title for your grievance."})

        elif any(keyword in message_lower for keyword in STATUS_KEYWORDS):
            session["step"] = "ask_search_method"
            return jsonify({"reply": "🔎 Would you like to check status by *Grievance ID* or *Title*?"})

        elif message_lower in GREETINGS:
            return jsonify({"reply": "👋 Hello! You can file a grievance or check its status. Just say 'I have a complaint' or 'Check grievance status' or you can check category and assigned to of you gravience."})
        
        else:
            return jsonify({"reply": "🤔 I'm not sure I understood that. You can say things like 'I have a problem' or 'Check grievance status'."})

    # Step 2: User chooses search method
    if step == "ask_search_method":
        if "id" in message_lower:
            session["step"] = "ask_grievance_id"
            return jsonify({"reply": "📄 Please enter your Grievance ID (e.g., GRV-20240513-1234)."})
        elif "title" in message_lower:
            session["step"] = "ask_grievance_title"
            return jsonify({"reply": "📝 Please enter the title of your grievance."})
        else:
            return jsonify({"reply": "❓ Please reply with either 'ID' or 'Title' to continue."})

    # Step 3: Search by ID
    if step == "ask_grievance_id":
        grievance_id = message.strip()
        if not token:
            return jsonify({"reply": "❌ Authentication token is missing."})

        try:
            headers = { "Authorization": f"Bearer {token}" }
            res = requests.get(f"http://localhost:8080/api/grievances/g/{grievance_id}", headers=headers)

            if res.status_code == 200:
                data = res.json()
                status = data.get("status", "Unknown")
                title = data.get("title", "N/A")
                category = data.get("category", "N/A")
                assigned_to = data.get("assignedTo", {}).get("name", "N/A")
                session["step"] = "start"
                return jsonify({
                    "reply": f"📄 **Grievance Title**: {title}\n📌 **Status**: {status}\n📌 **Category**: {category}\n👤 **Assigned To**: {assigned_to}"
                })
            else:
                session["step"] = "start"
                return jsonify({"reply": "❌ Grievance not found. Please double-check the ID and try again."})

        except Exception as e:
            session["step"] = "start"
            return jsonify({"reply": f"❌ Error fetching grievance status: {str(e)}"})

    # Step 4: Search by Title
    if step == "ask_grievance_title":
        title = message.strip()
        if not token:
            return jsonify({"reply": "❌ Authentication token is missing."})

        try:
            headers = { "Authorization": f"Bearer {token}" }
            # Assuming your backend supports title search query
            res = requests.get(f"http://localhost:8080/api/grievances/name/{title}", headers=headers)

            if res.status_code == 200:
                data = res.json()
                status = data.get("status", "Unknown")
                title = data.get("title", "N/A")
                category = data.get("category", "N/A")
                assigned_to = data.get("assignedTo", {}).get("name", "N/A")
                session["step"] = "start"
                return jsonify({
                    "reply": f"📄 **Grievance Title**: {title}\n📌 **Status**: {status}\n📌 **Category**: {category}\n👤 **Assigned To**: {assigned_to}"
                })
            else:
                session["step"] = "start"
                return jsonify({"reply": "❌ Grievance not found with that title."})

        except Exception as e:
            session["step"] = "start"
            return jsonify({"reply": f"❌ Error fetching grievance status: {str(e)}"})

    # The rest of the grievance submission flow (unchanged)...



    # Continue the existing flow if already started
    if step == "title":
        session["data"]["title"] = message
        session["step"] = "description"
        return jsonify({"reply": "Thanks! Now, please describe the issue in detail."})

    elif step == "description":
        session["data"]["description"] = message
        session["step"] = "image"
        return jsonify({"reply": "Do you have any images or evidence? If yes, please upload it. If not, type 'no'."})

    elif step == "image":
        if message and message.lower() != "no":
            session["data"]["image"] = message
        else:
            session["data"]["image"] = None

        description = session["data"].get("description")
        if not description:
            return jsonify({"reply": "⚠️ Description missing. Please start over."})

        session["data"]["category"] = classify_complaint(description)
        session["step"] = "confirm"

        summary = (
            f"**Please confirm your grievance details:**\n"
            f"Title: {session['data'].get('title', 'N/A')}\n"
            f"Description: {session['data'].get('description', 'N/A')}\n"
            f"Category: {session['data'].get('category', 'general')}\n"
            f"Image: {session['data'].get('image')}\n"
            f"Type 'confirm' to submit or 'cancel' to reset the form."
        )
        return jsonify({"reply": summary})

    elif step == "confirm":
        if message_lower == "confirm":
            if not token:
                return jsonify({"reply": "❌ Authentication token is missing."})
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                data_to_send = {
                    "title": session["data"]["title"],
                    "description": session["data"]["description"],
                    "category": session["data"]["category"],
                    "priority": session["data"].get("priority", "Medium"),
                    "photo": session["data"].get("image", None),
                }

                res = requests.post(
                    "http://localhost:8080/api/grievances/",
                    json=data_to_send,
                    headers=headers
                )

                if res.status_code == 201:
                    reset_user_session(user_id)
                    return jsonify({"reply": "✅ Your grievance has been submitted successfully!"})
                else:
                    return jsonify({"reply": f"❌ Failed to submit grievance: {res.text}"})

            except Exception as e:
                return jsonify({"reply": f"❌ Error occurred during submission: {str(e)}"})

        elif message_lower == "cancel":
            reset_user_session(user_id)
            return jsonify({"reply": "🛑 Grievance form has been reset. Start again with the title."})
        else:
            return jsonify({"reply": "⚠️ Please type 'confirm' to submit or 'cancel' to discard."})

    return jsonify({"reply": "❌ Something went wrong. Please start again."})

if __name__ == "__main__":
    app.run(debug=True)
