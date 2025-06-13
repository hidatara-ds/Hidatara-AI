from flask import Flask, request, jsonify
from google.cloud import language_v1
import os

app = Flask(__name__)

# Load credentials dari environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/gcloud_key.json"

def analyze_sentiment(text):
    """Menggunakan Google Cloud Natural Language API untuk analisis sentimen."""
    client = language_v1.LanguageServiceClient()
    
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment

    return {
        "sentiment_score": sentiment.score,
        "magnitude": sentiment.magnitude
    }

@app.route("/analyze_sentiment", methods=["POST"])
def analyze_sentiment_route():
    """Endpoint untuk menerima teks dan menganalisis sentimen."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    result = analyze_sentiment(data["text"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
