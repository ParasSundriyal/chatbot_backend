from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from chatbot_state import get_user_session, reset_user_session
from classifier import classify_complaint

app = Flask(__name__)
CORS(app)

# Keywords to detect grievance intent
GRIEVANCE_KEYWORDS = {"complaint", "grievance", "problem", "defect", "issue"}
STATUS_KEYWORDS = {"status", "progress", "grievance status", "check status", "category", "assigned", "department", "track", "track grievance"}
GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

# FAQ patterns and responses
FAQ_PATTERNS = [
    {
        "patterns": [
            r"how (long|much time) (will it|does it) take to (resolve|process|address) (a|my) (grievance|complaint|issue)",
            r"(grievance|complaint) (resolution|processing) (time|timeframe|timeline)",
            r"when will my (grievance|complaint|issue) be (resolved|addressed|fixed)",
            r"timeframe for (grievance|complaint) resolution"
        ],
        "response": "📆 Most grievances are resolved within 7-10 working days. Complex issues might take longer. You can always check the status of your grievance through this chatbot."
    },
    {
        "patterns": [
            r"who (will|can) (handle|address|resolve|respond to) my (grievance|complaint|issue)",
            r"(who('s| is) responsible for|which department handles) (grievances|complaints)",
            r"who (reviews|processes) (the|my) (grievances|complaints)"
        ],
        "response": "👨‍💼 Your grievance will be assigned to the appropriate department based on its category (e.g., Academic, Administrative, Infrastructure, etc.). Each department has dedicated staff to address student concerns."
    },
    {
        "patterns": [
            r"(can|how do) I (update|modify|edit|change) (my|a) (grievance|complaint)( after submitting| once submitted)",
            r"(edit|update|change|modify) (a|my) submitted (grievance|complaint)",
            r"(is it possible to|can I) make changes to (my|a) (grievance|complaint)"
        ],
        "response": "✏️ Once submitted, you cannot directly edit your grievance. However, you can contact the Student Affairs Office with your Grievance ID to provide additional information."
    },
    {
        "patterns": [
            r"(what|which) (types of|kind of) (grievances|complaints|issues) (can I|should I) (submit|file|report)",
            r"(can|should) I (submit|file|report) (a|an) (academic|hostel|infrastructure|faculty|cafeteria|library) (grievance|complaint|issue)",
            r"examples of (grievances|complaints) I can (submit|file|report)",
            r"what (grievances|complaints) (are|are not) allowed"
        ],
        "response": "📋 You can submit grievances related to academics, administration, infrastructure, faculty, hostel, cafeteria, transportation, library services, and other campus facilities. Personal disputes between students should first be addressed through the Student Counseling Center."
    },
    {
        "patterns": [
            r"(can|is it possible to) (submit|file|report) (a|an) (anonymous|unnamed) (grievance|complaint)",
            r"(do I need to|must I|should I) provide (my|personal) (name|details|information)",
            r"(anonymity|anonymous) (options|possibility|feature) for (grievances|complaints)",
            r"stay anonymous (while|when) (submitting|filing|reporting) (a|my) (grievance|complaint)"
        ],
        "response": "🔒 All grievances require user authentication for accountability. However, you can request confidentiality, and your identity won't be disclosed to parties involved except the handling administrator."
    },
    {
        "patterns": [
            r"(how|where) (can|do) I (check|view|see|track) (status|progress) of (my|a) (grievance|complaint)",
            r"(can|how to) (check|view|see|track) (grievance|complaint) status",
            r"(see|view|check) (grievance|complaint) (progress|updates)"
        ],
        "response": "🔍 You can check the status of your grievance by typing 'check status' here in the chatbot, or logging into the student portal and visiting the 'My Grievances' section."
    },
    {
        "patterns": [
            r"what (happens|should I do) if (my|the) (grievance|complaint|issue) (is not|isn't) (resolved|addressed) (in time|satisfactorily|properly)",
            r"(grievance|complaint) not (resolved|addressed|fixed) (properly|satisfactorily|in time)",
            r"unsatisfied with (grievance|complaint) (resolution|outcome|response)"
        ],
        "response": "📢 If you're not satisfied with the resolution, you can request an appeal within 7 days of receiving the resolution. Just log into the student portal and click on 'Appeal Resolution' under the specific grievance."
    },
    {
        "patterns": [
            r"(is there|do you have) (a|any) (limit|restriction|cap) on (how many|the number of) (grievances|complaints) I can (submit|file|report)",
            r"(maximum|limit of) (grievances|complaints) (allowed|per student)",
            r"(too many|multiple) (grievances|complaints)"
        ],
        "response": "🔢 There's no strict limit on the number of grievances you can submit. However, we encourage students to submit thoughtful complaints. Multiple similar grievances may be merged into one for efficient processing."
    },
    {
        "patterns": [
            r"(what are|define) the (priority levels|priorities) for (grievances|complaints)",
            r"how (is|are) (priority|priorities) (assigned|determined|decided)",
            r"(high|low|medium) priority (grievances|complaints)"
        ],
        "response": "⚠️ Grievances are classified as High, Medium, or Low priority based on urgency and impact. High priority issues (affecting health, safety, or critical academic matters) are addressed within 2-3 days. Medium priority within 5-7 days, and Low priority within 10 working days."
    },
    {
        "patterns": [
            r"(can|will) I (get|receive) (notifications|updates|alerts) (about|for|on) (my|the) (grievance|complaint) (status|progress)",
            r"(email|SMS|notification) (alerts|updates) for (grievances|complaints)",
            r"(track|follow) (grievance|complaint) updates"
        ],
        "response": "📱 Yes, you'll receive email notifications when your grievance status changes or when there's a response from the department. You can also enable SMS alerts in your profile settings."
    }
]

def check_for_faq_match(message):
    """Check if the message matches any FAQ pattern and return the appropriate response"""
    message_lower = message.lower().strip()
    
    for faq in FAQ_PATTERNS:
        for pattern in faq["patterns"]:
            if re.search(pattern, message_lower):
                return faq["response"]
    
    return None

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.form.get("user_id") or request.json.get("user_id")
    token = request.form.get("token") or request.json.get("token")
    message = request.form.get("message") or request.json.get("message")
    message_lower = message.lower().strip() if message else ""

    session = get_user_session(user_id)
    step = session["step"]
    
    # Check for FAQ match regardless of session state
    faq_response = check_for_faq_match(message)
    if faq_response and step == "start":
        return jsonify({"reply": faq_response})

    # Step 1: User starts with intent
    if step == "start":
        if any(keyword in message_lower for keyword in GRIEVANCE_KEYWORDS):
            session["step"] = "title"
            return jsonify({"reply": "Please provide a short title for your grievance."})

        elif any(keyword in message_lower for keyword in STATUS_KEYWORDS):
            session["step"] = "ask_search_method"
            return jsonify({"reply": "🔎 Would you like to check status by *Grievance ID* or *Title*?"})

        elif message_lower in GREETINGS:
            return jsonify({"reply": "👋 Hello! You can file a grievance or check its status. Just say 'I have a complaint' or 'Check grievance status' or you can check category and assigned to of your grievance."})
        
        else:
            return jsonify({"reply": "🤔 I'm not sure I understood that. You can say things like 'I have a problem' or 'Check grievance status'. Or ask me a question about the grievance system."})

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
                    "reply": f"📄 **Grievance Title**: {title}\n📌 **Status**: {status}\n📌 **Department**: {category}\n👤 **Assigned To**: {assigned_to}"
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
                    "reply": f"📄 **Grievance Title**: {title}\n📌 **Status**: {status}\n📌 **Department**: {category}\n👤 **Assigned To**: {assigned_to}"
                })
            else:
                session["step"] = "start"
                return jsonify({"reply": "❌ Grievance not found with that title."})

        except Exception as e:
            session["step"] = "start"
            return jsonify({"reply": f"❌ Error fetching grievance status: {str(e)}"})

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
                    category = session['data'].get('category', 'general')
                    return jsonify({
                        "reply": f"✅ Your grievance has been submitted successfully! It has been sent to the **{category}** department."
                    })

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