# classifier.py
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model loaded successfully.")
except Exception as e:
    print("Error loading spaCy model:", e)
    nlp = None  # fallback to avoid crashing

CATEGORY_KEYWORDS = {
    "Infrastructure": [
        "wifi", "classroom", "ac", "fan", "electricity", "maintenance",
        "projector", "blackboard", "whiteboard", "bench", "desk", "lights",
        "leakage", "water", "lift", "elevator", "lab", "toilet", "washroom",
        "building", "construction", "noise", "cleaning", "renovation"
    ],
    "Academic": [
        "exam", "marks", "result", "assignment", "class", "teacher", "lecture",
        "syllabus", "notes", "study material", "attendance", "timetable",
        "subject", "homework", "grading", "evaluation", "doubt", "project",
        "internals", "quiz", "lab marks"
    ],
    "Administration": [
        "fees", "payment", "admission", "document", "certificate", "id card",
        "scholarship", "refund", "registration", "form", "deadline", "leave",
        "transfer", "late fine", "library card", "student record", "passport",
        "bonafide", "verification"
    ],
    "Hostel": [
        "room", "mess", "food", "warden", "water", "electricity", "cleaning",
        "maintenance", "bed", "fan", "ac", "security", "gate", "curfew",
        "laundry", "bathroom", "toilet", "roommate", "wifi", "TV", "noise",
        "guest", "visitors", "hostel id", "complaint box", "mosquito"
    ]
}


def classify_complaint(text):
    if nlp is None:
        print("Warning: spaCy NLP model not loaded. Returning 'general'.")
        return "general"
    print("text: ", text)  # Debug log
    doc = nlp(text.lower())
    category_scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for token in doc:
        for category, keywords in CATEGORY_KEYWORDS.items():
            if token.text in keywords:
                category_scores[category] += 1

    print(f"Token matches: {category_scores}")  # Debug log

    category = max(category_scores, key=category_scores.get)
    if category_scores[category] == 0:
        category = "General"
    return category
