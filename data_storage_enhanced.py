from transformers import pipeline
from pymongo import MongoClient

# Load the sentiment analysis pipeline using the CAMeLBERT-DA SA model
try:
    sa_pipeline = pipeline('text-classification', model='CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment', truncation=True)
except Exception as e:
    print(f"Error loading model: {e}")
    sa_pipeline = None  # Set to None or handle as needed

# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['almayadeen']
    collection = db['articles']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Helper function to truncate text to 512 tokens
def truncate_text(text, max_length=512):
    return text[:max_length]

# Function to analyze sentiment using CAMeLBERT-DA and return the sentiment and score
def analyze_sentiment_camelbert(full_text):
    if sa_pipeline is None:
        print("Sentiment analysis pipeline not loaded.")
        return None

    try:
        # Truncate the text to 512 tokens or less
        truncated_text = truncate_text(full_text)

        # Use the pipeline to get the sentiment analysis
        results = sa_pipeline(truncated_text)

        # Extract the label and score
        sentiment_label = results[0]['label']
        sentiment_score = results[0]['score']

        sentiment_data = {
            'sentiment': sentiment_label,
            'sentiment_score': float(sentiment_score)
        }
        return sentiment_data
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return None

# Function to fetch articles, analyze sentiment, and update MongoDB
def process_articles():
    try:
        # Fetch all articles without sentiment data
        articles = collection.find({"sentiment": {"$exists": False}})

        for article in articles:
            # Extract the full text for sentiment analysis
            full_text = article.get('full_text', '')
            if not full_text:
                print(f"No text found for article ID: {article['_id']}")
                continue

            # Analyze sentiment
            sentiment_data = analyze_sentiment_camelbert(full_text)
            if sentiment_data:
                print(f"Updating article ID {article['_id']} with sentiment: {sentiment_data}")

                # Update MongoDB with sentiment data
                collection.update_one(
                    {"_id": article['_id']},
                    {"$set": {
                        "sentiment": sentiment_data['sentiment'],
                        "sentiment_score": sentiment_data['sentiment_score']
                    }}
                )
                print(f"Successfully updated article ID {article['_id']}")
            else:
                print(f"Sentiment analysis failed for article ID {article['_id']}")
    except Exception as e:
        print(f"Error processing articles: {e}")

# Example usage: Process all articles in the collection
process_articles()
