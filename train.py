# train.py
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ---------------------------
# Load intents.json
# ---------------------------
with open("data/intents.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

X = []  # training sentences
y = []  # labels

for intent in intents["intents"]:
    tag = intent["tag"]
    for pattern in intent["patterns"]:
        X.append(pattern)
        y.append(tag)

# ---------------------------
# Train/Test Split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------------------------
# Build Pipeline (Vectorizer + Classifier)
# ---------------------------
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), stop_words="english")),
    ("clf", LogisticRegression(max_iter=1000, C=3))
])

# ---------------------------
# Train the model
# ---------------------------
pipeline.fit(X_train, y_train)

# ---------------------------
# Evaluate
# ---------------------------
y_pred = pipeline.predict(X_test)
print("Classification Report:\n")
print(classification_report(y_test, y_pred))

# ---------------------------
# Save models
# ---------------------------
joblib.dump(pipeline.named_steps["tfidf"], "models/vectorizer.joblib")
joblib.dump(pipeline.named_steps["clf"], "models/classifier.joblib")

print("\n✅ Model training complete! Saved in 'models/'")
