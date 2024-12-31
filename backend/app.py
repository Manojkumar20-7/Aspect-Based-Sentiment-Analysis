from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer, BertForSequenceClassification, RobertaForSequenceClassification, AlbertForSequenceClassification
import torch
import spacy
import re
import json
from prometheus_client import Counter, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, supports_credentials=True)  # Allow cross-origin requests

# Initialize Prometheus metrics exporter
metrics = PrometheusMetrics(app)


# Load the saved DistilBERT model and tokenizer
distilbert_model_path = 'newmodels/distilbert_model'
distilbert_model = DistilBertForSequenceClassification.from_pretrained(distilbert_model_path)
tokenizer = DistilBertTokenizer.from_pretrained(distilbert_model_path)

# Load spaCy model for aspect extraction
nlp = spacy.load("en_core_web_sm")

feedback_data = []

# Prometheus metrics
feedback_received = Counter('feedback_received', 'Total number of feedback submissions')
correct_feedback = Counter('correct_feedback', 'Total number of correct feedback submissions')
incorrect_feedback = Counter('incorrect_feedback', 'Total number of incorrect feedback submissions')


# Sentiment classification function
def classify_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = distilbert_model(**inputs)
    logits = outputs.logits
    predictions = logits.argmax(dim=-1)
    sentiment = "POSITIVE" if predictions.item() == 1 else "NEGATIVE"
    return sentiment

# Aspect extraction function
def extract_aspects(text):
    doc = nlp(text)
    aspects = []
    for np in doc.noun_chunks:
        aspects.append(np.text.lower())
    return aspects

# Split text into sentences based on conjunctions and full stops
def split_sentences_and_aspects(text):
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+| and | but | or ', text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]

# Function to get overall review sentiment based on majority rule
def overall_sentiment(sentiments):
    positive_count = sentiments.count("POSITIVE")
    negative_count = sentiments.count("NEGATIVE")
    # Majority rule: if more POSITIVE sentences, overall sentiment is POSITIVE, else NEGATIVE
    if positive_count > negative_count:
        return "POSITIVE"
    elif negative_count>positive_count:
        return "NEGATIVE"
    else:
        return "NEUTRAL"
    
def sentiment_percentage(sentiments):
    total_sentences = len(sentiments)
    if total_sentences == 0:
        return {"positive_percentage": 0, "negative_percentage": 0}

    positive_count = sentiments.count("POSITIVE")
    negative_count = sentiments.count("NEGATIVE")
    
    positive_percentage = (positive_count / total_sentences) * 100
    negative_percentage = (negative_count / total_sentences) * 100
    
    return {
        "positive_percentage": round(positive_percentage, 2),
        "negative_percentage": round(negative_percentage, 2)
    }

# Define the endpoint for aspect-based sentiment analysis
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    review = data.get("review", "")

    if not review:
        return jsonify({"error": "No review text provided"}), 400

    # Split sentences
    sentences = split_sentences_and_aspects(review)

    results = []
    sentiments = []  # List to hold individual sentence sentiments for overall sentiment calculation
    for sentence in sentences:
        aspects = extract_aspects(sentence)
        sentence_sentiment = classify_sentiment(sentence)
        sentiments.append(sentence_sentiment)

        results.append({
            "sentence": sentence,
            "aspects": list(set(aspects)),  # Remove duplicates from aspects
            "sentiment": sentence_sentiment
        })
    # Calculate overall review sentiment
    overall_review_sentiment = overall_sentiment(sentiments)
    # Calculate sentiment percentages
    sentiment_percentages = sentiment_percentage(sentiments)


    return jsonify({
        "review": review,
        "overall_sentiment": overall_review_sentiment,  # Add overall sentiment
        "sentiment_percentages": sentiment_percentages,
        "analysis": results
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    review = data.get("review")
    correct = data.get("correct", True)

    if review is None:
        return jsonify({"error": "No review provided for feedback"}), 400

    # Save feedback to in-memory data structure
    feedback_data.append({
        "review": review,
        "correct": correct
    })

    # Increment Prometheus counters based on feedback correctness
    feedback_received.inc()  # Increment total feedback count
    if correct:
        correct_feedback.inc()  # Increment correct feedback count
    else:
        incorrect_feedback.inc()  # Increment incorrect feedback count

    # Optionally, save feedback to a file or database for later processing
    with open("feedback.json", "a") as f:
        json.dump({
            "review": review,
            "correct": correct
        }, f)
        f.write("\n")

    return jsonify({"message": "Feedback submitted successfully"}), 200

# Function to retrieve feedback data (optional, for monitoring)
@app.route("/feedback_data", methods=["GET"])
def get_feedback():
    return jsonify(feedback_data)

# Prometheus metrics endpoint
@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(debug=True)
