import random

def classify_complaint(text):
    text = text.lower().strip()

    if any(word in text for word in ["wifi", "internet", "network", "lan"]):
        responses = [
            "We've noted the internet issue. Our IT team has been notified.",
            "Network problems can be frustrating — the hostel IT admin will look into it shortly.",
            "Your internet-related complaint is forwarded to the technical department."
        ]
        return "Infrastructure", random.choice(responses)

    elif any(word in text for word in ["marks", "grades", "results", "exam result"]):
        responses = [
            "We understand your concern regarding marks. The Exam Cell will review it.",
            "Exam-related issues are important. We've forwarded your query to the concerned department.",
            "Thank you for reporting the marks issue. It'll be handled by the Examination Office."
        ]
        return "Academics", random.choice(responses)

    elif any(word in text for word in ["fees", "payment", "transaction", "receipt"]):
        responses = [
            "The Accounts Section has been notified about your fee-related query.",
            "We're checking into the payment issue. Please expect a response from the Accounts Department.",
            "Thank you. The Accounts team will assist you with the payment concern."
        ]
        return "Accounts", random.choice(responses)

    elif any(word in text for word in ["id card", "identity card", "id lost", "lost id"]):
        responses = [
            "Sorry to hear that! Please visit the admin office for ID reissuance.",
            "ID card issues are common — the admin has been alerted.",
            "We’ve reported your lost ID to the administration. You’ll be contacted soon."
        ]
        return "Administration", random.choice(responses)

    elif any(word in text for word in ["hostel", "room", "mess", "bed", "fan", "ac", "light"]):
        responses = [
            "Thanks for letting us know. The hostel warden has been notified.",
            "Room and hostel complaints are routed to the Warden. They’ll look into it.",
            "Your hostel-related issue has been logged. Maintenance will be done if needed."
        ]
        return "Hostel", random.choice(responses)

    elif any(word in text for word in ["library", "book", "reading room"]):
        responses = [
            "Library services matter — the librarian has been informed.",
            "We’ve sent your concern to the Library Department.",
            "The issue has been shared with library staff. Expect a response soon."
        ]
        return "Library", random.choice(responses)

    elif any(word in text for word in ["canteen", "food", "meal", "hygiene"]):
        responses = [
            "Hygiene and food quality are important. The Canteen Committee is notified.",
            "Thanks for your feedback on meals. The concern is forwarded to the canteen in-charge.",
            "We value your input. Canteen-related issues are under review."
        ]
        return "Canteen", random.choice(responses)

    elif any(word in text for word in ["faculty", "teacher", "professor", "class", "lecture"]):
        responses = [
            "We’ve shared your academic concern with the Academic Coordinator.",
            "Faculty-related complaints are sensitive. The department is reviewing it.",
            "Thanks. Your classroom-related issue is being looked into."
        ]
        return "Academic Staff", random.choice(responses)

    elif any(word in text for word in ["bus", "transport", "shuttle"]):
        responses = [
            "Transport-related issues are logged with the coordinator.",
            "Thanks. Your complaint has been sent to the Transport Department.",
            "We’ve notified the transportation staff. Expect resolution soon."
        ]
        return "Transport", random.choice(responses)

    elif any(word in text for word in ["clean", "dust", "sanitation", "dirty", "toilet"]):
        responses = [
            "Cleanliness matters. Maintenance has been informed.",
            "Thanks for raising this. Sanitation issues are now logged.",
            "Your report on hygiene has reached the facilities team."
        ]
        return "Maintenance", random.choice(responses)

    elif any(word in text for word in ["ragging", "harassment", "bully", "abuse"]):
        responses = [
            "This is a serious matter. The Disciplinary Committee is alerted.",
            "Thank you for bringing this up. Action will be taken as per policy.",
            "We take such reports seriously. The anti-ragging cell is notified."
        ]
        return "Disciplinary Committee", random.choice(responses)

    elif any(word in text for word in ["event", "fest", "registration", "club", "activity"]):
        responses = [
            "Your event query is sent to Student Affairs.",
            "Thanks. Student activity issues are handled by the events office.",
            "We’ve forwarded this to the student engagement team."
        ]
        return "Student Affairs", random.choice(responses)

    else:
        responses = [
            "Thank you for reaching out. The admin team will review your concern.",
            "We've received your message. Someone will follow up shortly.",
            "Your query has been noted. It will be addressed soon."
        ]
        return "General", random.choice(responses)
