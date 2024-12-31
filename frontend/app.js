function analyzeReview() {
    const reviewText = document.getElementById("reviewText").value.trim();
    if (!reviewText) {
        alert("Please enter a review.");
        return;
    }

    // Show the loading message
    document.getElementById("loadingMessage").style.display = "block";
    document.getElementById("resultContainer").style.display = "none";
    document.getElementById("feedback-section").classList.add("hidden");

    // Make the POST request to analyze the review
    fetch('http://localhost:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review: reviewText })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to analyze review');
        }
        return response.json();
    })
    .then(data => {
        // Handle the successful response
        document.getElementById("loadingMessage").style.display = "none";
        document.getElementById("resultContainer").style.display = "block";

        document.getElementById("overallSentiment").textContent = data.overall_sentiment;
        document.getElementById("positivePercentage").textContent = data.sentiment_percentages.positive_percentage;
        document.getElementById("negativePercentage").textContent = data.sentiment_percentages.negative_percentage;

        const tableBody = document.getElementById("analysisTable").querySelector("tbody");
        tableBody.innerHTML = '';  // Clear previous analysis results

        data.analysis.forEach(result => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${result.sentence}</td>
                <td>${result.aspects.join(", ")}</td>
                <td>${result.sentiment}</td>
            `;
            tableBody.appendChild(row);
        });

        // Show feedback section
        document.getElementById("feedback-section").classList.remove("hidden");
    })
    .catch(error => {
        console.error("Error analyzing review:", error);
        alert("An error occurred. Please try again later.");
    });
}