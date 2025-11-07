# api/chat.py
from http import HTTPStatus
import json, joblib, random, csv, datetime, os
import numpy as np

# load models on cold-start (cached across warm invocations)
vect = joblib.load("models/vectorizer.joblib")
clf = joblib.load("models/classifier.joblib")
intents = json.load(open("data/intents.json","r",encoding="utf-8"))

def get_responses_for_tag(tag):
    for it in intents["intents"]:
        if it["tag"] == tag:
            return it.get("responses", [])
    return []

def handler(request):
    try:
        data = request.json or {}
    except Exception:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": json.dumps({"error":"bad json"})}

    message = (data.get("message") or "").strip()
    if not message:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": json.dumps({"error":"empty message"})}

    x = vect.transform([message])
    probs = clf.predict_proba(x)[0]
    idx = int(np.argmax(probs))
    tag = str(clf.classes_[idx])
    prob = float(probs[idx])
    if prob < 0.3:
        tag = "fallback"
    responses = get_responses_for_tag(tag)
    resp = random.choice(responses) if responses else "Sorry, I don't know that."

    # (optional) log to a file in /tmp (ephemeral) or to external store
    return {"statusCode": HTTPStatus.OK, "body": json.dumps({"response": resp, "tag": tag, "confidence": prob})}
