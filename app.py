from flask import Flask, request, jsonify
import joblib, json, random, datetime, csv
import numpy as np, os

app = Flask(__name__)

# Load models and intents
vect = joblib.load("models/vectorizer.joblib")
clf = joblib.load("models/classifier.joblib")
intents = json.load(open("data/intents.json", "r", encoding="utf-8"))

# Make sure logs folder exists (important on Render)
os.makedirs("logs", exist_ok=True)

# Helper: find responses for a tag
def get_responses_for_tag(tag):
    for it in intents["intents"]:
        if it["tag"] == tag:
            return it.get("responses", [])
    return []

@app.route("/chat", methods=["POST"])
def chat():
    # Try to read JSON safely
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Predict
    x = vect.transform([message])
    probs = clf.predict_proba(x)[0]
    idx = np.argmax(probs)
    tag = clf.classes_[idx]
    prob = float(probs[idx])

    if prob < 0.5:
        tag = "fallback"

    responses = get_responses_for_tag(tag)
    resp = random.choice(responses) if responses else "Sorry, I don't know that."

    # Log chat
    with open("logs/chats.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.utcnow().isoformat(), message, resp, tag, prob])

    return jsonify({"response": resp, "tag": tag, "confidence": prob})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
