// App.js
import React, { useState } from "react";
import Gauge from "./Gauge";
import AspectTable from "./AspectTable";
import "./App.css"; // Add your styling here

const App = () => {
  const [review, setReview] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [feedback, setFeedback] = useState(0);

  const handleSubmit = async () => {
    if (!review.trim()) {
      alert("Please enter a review!");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ review }),
      });
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error("Error fetching sentiment analysis:", error);
      alert("Failed to fetch sentiment analysis. Please try again.");
    }
  };

  const submitFeedback = async () => {
    if (!feedback) {
      alert("Please select a rating before submitting feedback!");
      return;
    }
  
    try {
      const response = await fetch("http://localhost:5000/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ feedback }),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        alert("Feedback submitted successfully!");
      } else {
        alert(data.error || "Failed to submit feedback. Please try again.");
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to submit feedback. Please try again.");
    }
  };

  return (
    <div className="app">
      <h1>Aspect-Based Sentiment Analysis</h1>
      <textarea
        placeholder="Enter your review here..."
        value={review}
        onChange={(e) => setReview(e.target.value)}
        rows="5"
      ></textarea>
      <button onClick={handleSubmit}>Analyze</button>

      {analysis && (
        <div className="results">
          <h2>Overall Sentiment: {analysis.overall_sentiment}</h2>
          <Gauge
            positivePercentage={analysis.sentiment_percentages.positive_percentage}
          />
          <AspectTable analysis={analysis.analysis} />
        </div>
      )}

      <div className="feedback">
        <h3>Rate your experience:</h3>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${feedback >= star ? "selected" : ""}`}
            onClick={() => setFeedback(star)}
          >
            ★
          </span>
        ))}
        <button onClick={submitFeedback}>Submit Feedback</button>
      </div>
    </div>
  );
};

export default App;
