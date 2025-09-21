from flask import Flask, request, jsonify
import joblib, json, random, datetime, csv, os
import numpy as np

app = Flask(__name__)

# Load models and intents
vect = joblib.load("models/vectorizer.joblib")
clf = joblib.load("models/classifier.joblib")
with open("data/intents.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Helper function
def get_responses_for_tag(tag):
    for it in intents["intents"]:
        if it["tag"] == tag:
            return it.get("responses", [])
    return []

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)   # safer JSON parsing
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"response": "Please enter a valid question.", "tag": "none", "confidence": 0.0})

        # Predict intent
        x = vect.transform([message])
        probs = clf.predict_proba(x)[0]
        idx = np.argmax(probs)
        tag = clf.classes_[idx]
        prob = probs[idx]

        if prob < 0.5:
            tag = "fallback"

        responses = get_responses_for_tag(tag)
        resp = random.choice(responses) if responses else "Sorry, I don't know that."

        # Log interaction
        with open("logs/chats.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if f.tell() == 0:  # write header if file is empty
                writer.writerow(["timestamp", "message", "response", "tag", "confidence"])
            writer.writerow([datetime.datetime.utcnow().isoformat(), message, resp, tag, float(prob)])

        return jsonify({
            "response": resp,      # use "response" (matches Telegram bot expectations)
            "tag": tag,
            "confidence": float(prob)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
