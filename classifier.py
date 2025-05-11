# classifier.py
def classify_complaint(text):
    text = text.lower()
    if "wifi" in text or "internet" in text:
        return "Infrastructure", "Please contact hostel IT admin."
    elif "marks" in text or "grades" in text:
        return "Academics", "Your issue is forwarded to the Exam Cell."
    elif "fees" in text or "payment" in text:
        return "Accounts", "Please reach out to the Accounts Section."
    elif "hostel" in text or "room" in text:
        return "Hostel", "The warden has been notified."
    else:
        return "General", "Thank you. The admin team will review it."
