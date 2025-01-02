from flask import Flask, request, jsonify
from flask_cors import CORS
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import torch
import spacy
import re
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/analyze": {"origins": "http://localhost:3000"}})
metrics = PrometheusMetrics(app)

# Load the DistilBERT model and tokenizer
distilbert_model_path = 'newmodels/distilbert_model'
distilbert_model = DistilBertForSequenceClassification.from_pretrained(distilbert_model_path)
tokenizer = DistilBertTokenizer.from_pretrained(distilbert_model_path)

# Use spaCy for aspect extraction
nlp = spacy.load("en_core_web_sm")

# Initialize Prometheus metrics for feedback
feedback_counter = metrics.counter(
    'feedback_responses',
    'Count of feedback responses by rating',
    labels={'rating': lambda: request.json.get("rating", "unknown")}
)

feedback_summary = metrics.summary(
    'feedback_rating_summary',
    'Summary statistics for feedback ratings'
)

feedback_histogram = metrics.histogram(
    'feedback_rating_histogram',
    'Histogram of feedback ratings',
    buckets=[1, 2, 3, 4, 5]
)

feedback_counter = Counter(
    "feedback_count",
    "Count of feedback received by rating",
    ["rating"]
)

# Feedback storage (for simplicity; replace with persistent storage for production)
feedback_store = []


# Sentiment classification function
def classify_sentiment_batch(sentences):
    inputs = tokenizer(sentences, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = distilbert_model(**inputs).logits
    predictions = logits.argmax(dim=-1).tolist()
    return ["POSITIVE" if pred == 1 else "NEGATIVE" for pred in predictions]

# Split sentences for processing
def split_sentences_and_aspects(text):
    return re.split(r'(?<=[.!?])\s+| and | but | or ', text.strip())

# Aspect extraction function
def extract_aspects(sentence):
    doc = nlp(sentence)
    return [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN']]

# Adjective extraction function
def extract_adjectives(sentence):
    doc = nlp(sentence)
    return [token.text for token in doc if token.pos_ == "ADJ"]

# Overall sentiment
def overall_sentiment(sentiments):
    return "POSITIVE" if sentiments.count("POSITIVE") > sentiments.count("NEGATIVE") else "NEGATIVE"

# Sentiment percentages
def sentiment_percentage(sentiments):
    total = len(sentiments)
    positive = sentiments.count("POSITIVE")
    return {
        "positive_percentage": round((positive / total) * 100, 2) if total else 0,
        "negative_percentage": round((1 - positive / total) * 100, 2) if total else 0
    }

# Analyze endpoint
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    review = data.get("review", "")

    if not review:
        return jsonify({"error": "No review text provided"}), 400

    sentences = split_sentences_and_aspects(review)
    sentences = [s.strip() for s in sentences if s.strip()]  # Remove empty strings
    if not sentences:
        return jsonify({"error": "No valid sentences found"}), 400

    sentiments = classify_sentiment_batch(sentences)

    # Parallel aspect and adjective extraction
    with ThreadPoolExecutor() as executor:
        aspects_list = list(executor.map(extract_aspects, sentences))
        adjectives_list = list(executor.map(extract_adjectives, sentences))

    results = [
        {
            "sentence": sentence,
            "aspects": aspects,
            "sentiment": sentiment,
            "sentiment_words": adjectives
        }
        for sentence, aspects, sentiment, adjectives in zip(sentences, aspects_list, sentiments, adjectives_list)
    ]

    overall = overall_sentiment(sentiments)
    percentages = sentiment_percentage(sentiments)

    return jsonify({
        "review": review,
        "overall_sentiment": overall,
        "sentiment_percentages": percentages,
        "analysis": results
    })

# Feedback endpoint
@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    rating = data.get("feedback")

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Invalid feedback rating"}), 400

    # Record feedback
    feedback_store.append(rating)
    feedback_counter.labels(rating=str(rating)).inc()  # Increment Prometheus counter
    return jsonify({"message": "Feedback submitted successfully!"}), 200

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

