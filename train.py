import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report




with open("data/intents.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

X = [] 
y = [] 

for intent in intents["intents"]:
    tag = intent["tag"]
    for pattern in intent["patterns"]:
        X.append(pattern)
        y.append(tag)


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), stop_words="english")),
    ("clf", LogisticRegression(max_iter=1000, C=3))
])


pipeline.fit(X_train, y_train)


y_pred = pipeline.predict(X_test)
print("Classification Report:\n")
print(classification_report(y_test, y_pred))


joblib.dump(pipeline.named_steps["tfidf"], "models/vectorizer.joblib")
joblib.dump(pipeline.named_steps["clf"], "models/classifier.joblib")

print("\nModel training complete! Saved in 'models/'")
