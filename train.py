import json, random
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import joblib

# load intents
with open("data/intents.json","r",encoding="utf-8") as f:
    intents = json.load(f)

rows = []
for intent in intents["intents"]:
    tag = intent["tag"]
    for p in intent.get("patterns",[]):
        rows.append((p, tag))
df = pd.DataFrame(rows, columns=["text","tag"])

# simple pipeline
vect = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
clf = LogisticRegression(max_iter=1000)

X = vect.fit_transform(df["text"])
clf.fit(X, df["tag"])

joblib.dump(vect, "models/vectorizer.joblib")
joblib.dump(clf, "models/classifier.joblib")
print("Saved vectorizer and classifier.")
