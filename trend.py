import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import json
# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['almayadeen']
    collection = db['articles']
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db, collection = None, None


# Improved function to handle various date formats, including extra zeros in microseconds
def process_publication_date(article):
    date_str = article.get('publication_date', '')
    try:
        # Handle the exact format with padded microseconds
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        try:
            # Handle cases where the microseconds might be all zeroes or missing
            if '.' in date_str:
                date_str = date_str.split('.')[0]  # Strip the fractional seconds part
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            print(f"Invalid date format for article ID {article['_id']}: {date_str}")
            return None


# Function to fetch and aggregate sentiment trends
def fetch_sentiment_trends():
    try:
        # Fetch articles that have sentiment and publication_date fields
        query = {"sentiment": {"$exists": True}, "publication_date": {"$exists": True}}
        articles = list(collection.find(query))

        # Extract relevant data
        data = []
        for article in articles:
            publication_date = process_publication_date(article)
            if publication_date:  # Only proceed if the date is valid
                sentiment = article.get('sentiment', 'neutral')
                data.append({"date": publication_date, "sentiment": sentiment})

        # Convert to DataFrame for easy manipulation
        df = pd.DataFrame(data)
        df = df.dropna()  # Drop articles with missing dates

        # Group by date and sentiment, count occurrences
        sentiment_trends = df.groupby([df['date'].dt.to_period('M'), 'sentiment']).size().unstack(fill_value=0)

        return sentiment_trends
    except Exception as e:
        print(f"Error fetching sentiment trends: {e}")
        return None


# Function to fetch and aggregate keyword trends
def fetch_keyword_trends(keyword):
    try:
        # Fetch articles that have the keyword and publication_date fields
        query = {"keywords": {"$in": [keyword]}, "publication_date": {"$exists": True}}
        articles = list(collection.find(query))

        # Extract relevant data
        data = []
        for article in articles:
            publication_date = process_publication_date(article)
            if publication_date:  # Only proceed if the date is valid
                data.append({"date": publication_date, "keyword": keyword})

        # Convert to DataFrame for easy manipulation
        df = pd.DataFrame(data)
        df = df.dropna()  # Drop articles with missing dates

        # Group by date and count occurrences of the keyword
        keyword_trends = df.groupby(df['date'].dt.to_period('M')).size()

        return keyword_trends
    except Exception as e:
        print(f"Error fetching keyword trends: {e}")
        return None


# Function to visualize sentiment trends
def visualize_sentiment_trends(sentiment_trends):
    sentiment_trends.plot(kind='line', figsize=(10, 6), title="Sentiment Trends Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Articles")
    plt.grid(True)
    plt.legend(title="Sentiment")
    plt.tight_layout()
    plt.show()


# Function to visualize keyword trends
def visualize_keyword_trends(keyword_trends, keyword):
    keyword_trends.plot(kind='bar', figsize=(10, 6), title=f"Trend of '{keyword}' Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Mentions")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Main function to handle trend analysis
def analyze_trends():
    # Fetch sentiment trends
    sentiment_trends = fetch_sentiment_trends()
    if sentiment_trends is not None:
        print("Sentiment Trends Data:")
        print(sentiment_trends)
        visualize_sentiment_trends(sentiment_trends)

    # Fetch keyword trends for a specific keyword
    keyword = "غزة"  # Example keyword
    keyword_trends = fetch_keyword_trends(keyword)
    if keyword_trends is not None:
        print(f"Keyword Trends Data for '{keyword}':")
        print(keyword_trends)
        visualize_keyword_trends(keyword_trends, keyword)




# Run the trend analysis
analyze_trends()
