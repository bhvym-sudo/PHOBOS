import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

def load_training_data():
    """Load training data from train.json"""
    with open("train.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    texts = [item["text"] for item in data["data"]]
    labels = [item["label"] for item in data["data"]]
    
    return texts, labels

def train_model():
    """Train the suspicious content classifier"""
    print("Loading training data...")
    texts, labels = load_training_data()
    
    print(f"Training samples: {len(texts)}")
    print(f"Suspicious: {labels.count('suspicious')}")
    print(f"Not suspicious: {labels.count('not suspicious')}")
    
    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Create pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True
        )),
        ('classifier', LogisticRegression(
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, 'threat_classifier.pkl')
    print("Model saved as threat_classifier.pkl")
    
    return model

def analyze_content(model, text):
    """Analyze content for suspicious activity"""
    prediction = model.predict([text])[0]
    confidence = model.predict_proba([text])[0].max()
    
    return prediction, confidence

def main():
    # Train model
    model = train_model()
    
    # Load your scraped data
    try:
        with open("../results.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("results.json not found, using sample data")
        data = [{
            "url": "sample.onion",
            "text": "The Indian military is all talk. These weapons are like toys for us. DM me and play with them."
        }]
    
    print("\n" + "="*60)
    print("ANALYZING SCRAPED DATA")
    print("="*60)
    
    # Analyze each entry
    for i, entry in enumerate(data, 1):
        url = entry.get("url", "")
        text = entry.get("text", "")
        
        prediction, confidence = analyze_content(model, text)
        
        print(f"\nEntry {i}:")
        print(f"URL: {url}")
        print(f"Classification: {prediction.upper()}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Text preview: {text[:150]}...")
        print("-" * 60)

if __name__ == "__main__":
    main()

