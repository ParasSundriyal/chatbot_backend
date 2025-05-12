# classifier.py
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model loaded successfully.")
except Exception as e:
    print("Error loading spaCy model:", e)
    nlp = None  # fallback to avoid crashing

CATEGORY_KEYWORDS = {
    "Infrastructure": ["wifi", "classroom", "ac", "fan", "electricity", "maintenance", "Hostel", "projector"],
    "Academic": ["exam", "marks", "result", "assignment", "class", "teacher", "lecture"],
    "Administration": ["fees", "payment", "admission", "document", "certificate", "id card"]
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
