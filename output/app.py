from datetime import datetime, timedelta

from flask import Flask, jsonify, abort, request, logging
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]


@app.route('/top_keywords', methods=['GET'])
def top_keywords():
    pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]


    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articles_by_date', methods=['GET'])
def articles_by_date():
    pipeline = [
        {
            "$match": {
                "publication_date": {"$exists": True, "$ne": None, "$ne": ""}
            }
        },
        {
            # Convert the string date to ISODate, if it's stored as a string
            "$addFields": {
                "parsed_date": {
                    "$cond": {
                        "if": {"$type": "$publication_date"},
                        "then": {"$toDate": "$publication_date"},
                        "else": "$publication_date"
                    }
                }
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$parsed_date"}},  # Format as YYYY-MM-DD
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}  # Sort by date in ascending order
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route('/top_authors', methods=['GET'])
def top_authors():
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articles_by_word_count', methods=['GET'])
def articles_by_word_count():
    pipeline = [
        {"$group": {"_id": "$word_count", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}  # Sort by word count (ascending)
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articles_by_language', methods=['GET'])
def articles_by_language():
    pipeline = [
        {"$group": {"_id": "$language", "count": {"$sum": 1}}},  # Use "$language" instead of "$lang"
        {"$sort": {"count": -1}}  # Sort by count (descending)
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route('/articles_by_classes', methods=['GET'])
def articles_by_classes():
    pipeline = [
        # Unwind the `classes` array to deconstruct it into individual documents
        {"$unwind": "$classes"},
        # Match documents where the `mapping` is "category"
        {"$match": {"classes.mapping": "category"}},
        # Group by the `value` field within `classes` and count the occurrences
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        # Sort the results by the count in descending order
        {"$sort": {"count": -1}}
    ]

    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route('/articles_by_author/<author_name>', methods=['GET'])
def get_articles_by_author(author_name):
    # Query MongoDB for articles written by the specific author
    articles = collection.find({"author": author_name}, {"title": 1, "_id": 0})
    # Extract article titles from the query result
    article_titles = [article["title"] for article in articles]
    return jsonify(article_titles)

@app.route('/articles_by_keyword/<keyword>', methods=['GET'])
def get_articles_by_keyword(keyword):
    # Query MongoDB for articles that contain the specific keyword
    articles = collection.find({"keywords": keyword}, {"title": 1, "_id": 0})
    # Extract article titles from the query result
    article_titles = [article["title"] for article in articles]
    return jsonify(article_titles)


@app.route('/top_classes', methods=['GET'])
def get_top_classes():
    # Aggregation pipeline to group by class and count occurrences
    pipeline = [
        {"$unwind": "$classes"},  # Unwind the classes array
        {"$group": {"_id": "$classes", "count": {"$sum": 1}}},  # Group by class and count occurrences
        {"$sort": {"count": -1}},  # Sort by count in descending order
        {"$limit": 10}  # Limit to top 10 classes
    ]

    # Run the aggregation pipeline
    top_classes = list(collection.aggregate(pipeline))

    # Format the response to only include class names and counts
    response = []
    for item in top_classes:
        class_name = item['_id']  # Class name
        count = item['count']  # Number of articles
        response.append(f"{class_name} ({count} articles)")

    return jsonify(response)


@app.route('/article_details/<postid>', methods=['GET'])
def get_article_details(postid):
    # Query MongoDB for the article with the specified postid
    article = collection.find_one({"post_id": postid})

    if article is None:
        # Return a 404 error if the article is not found
        abort(404, description="Article not found")

    # Extract the required details from the article
    details = {
        "URL": article.get("url", "N/A"),
        "Title": article.get("title", "N/A"),
        "Keywords": article.get("keywords", [])
    }

    return jsonify(details)


@app.route('/articles_with_video', methods=['GET'])
def articles_with_video():
    # Find articles where video_duration is not "No video duration available"
    articles = collection.find({"video_duration": {"$ne": "No video duration available"}})

    # Format the response
    response = {}
    for article in articles:
        title = article.get("title", "No Title")
        response[title] = article

    return jsonify(response)


@app.route('/articles_by_year/<int:year>', methods=['GET'])
def articles_by_year(year):
    # Query to find articles by the publication year
    query = {"publication_date": {"$regex": f"^{year}"}}  # Assuming publication_date is in 'YYYY-MM-DD' format
    count = collection.count_documents(query)

    # Format the response
    response = {f"{year}": f"{count} articles"}

    return jsonify(response)


@app.route('/longest_articles', methods=['GET'])
def longest_articles():
    # Query to find articles and sort by word_count in descending order
    pipeline = [
        {"$match": {"word_count": {"$exists": True, "$ne": None}}},
        {"$sort": {"word_count": -1}},
        {"$limit": 10},
        {"$project": {"title": 1, "word_count": 1}}
    ]

    articles = list(collection.aggregate(pipeline))

    # Format the response
    response = {}
    for article in articles:
        title = article.get("title", "Unknown Title")
        word_count = article.get("word_count", 0)
        response[title] = f"{word_count} words"

    return jsonify(response)


@app.route('/shortest_articles', methods=['GET'])
def shortest_articles():
    # Query to find articles and sort by word_count in ascending order
    pipeline = [
        {"$match": {"word_count": {"$exists": True, "$ne": None}}},
        {"$sort": {"word_count": 1}},
        {"$limit": 10},
        {"$project": {"title": 1, "word_count": 1}}
    ]

    articles = list(collection.aggregate(pipeline))

    # Format the response
    response = {}
    for article in articles:
        title = article.get("title", "Unknown Title")
        word_count = article.get("word_count", 0)
        response[title] = f"{word_count} words"

    return jsonify(response)


@app.route('/articles_by_keyword_count', methods=['GET'])
def articles_by_keyword_count():
    # Aggregate to count articles by the number of keywords
    pipeline = [
        {"$match": {"keywords": {"$exists": True, "$ne": None}}},
        {"$addFields": {"keyword_count": {"$size": "$keywords"}}},
        {"$group": {
            "_id": "$keyword_count",
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]

    results = list(collection.aggregate(pipeline))

    # Format the response
    response = {}
    for result in results:
        keyword_count = result.get("_id", 0)
        article_count = result.get("count", 0)
        response[f"{keyword_count} keywords"] = f"{article_count} articles"

    return jsonify(response)


@app.route('/articles_with_thumbnail', methods=['GET'])
def articles_with_thumbnail():
    # Find articles that have a non-empty 'thumbnail' field
    pipeline = [
        {"$match": {"thumbnail": {"$exists": True, "$ne": ""}}},
        {"$project": {"title": 1}}  # Assuming 'title' is the field to return
    ]

    results = list(collection.aggregate(pipeline))

    # Extract titles for articles with a thumbnail
    articles_with_thumbnail = [result.get("title", "No Title") for result in results]

    # Format the response
    response = {article: "Article with Thumbnail" for article in articles_with_thumbnail}

    return jsonify(response)


@app.route('/articles_updated_after_publication', methods=['GET'])
def articles_updated_after_publication():
    # Aggregation pipeline to find articles where last_updated is after published_time
    pipeline = [
        {"$match": {
            "$expr": {
                "$gt": ["$last_updated", "$published_time"]
            }
        }},
        {"$project": {
            "title": 1,
            "last_updated": 1,
            "published_time": 1
        }}
    ]

    results = list(collection.aggregate(pipeline))

    # Extract titles for articles updated after publication
    updated_articles = [result.get("title", "No Title") for result in results]

    # Format the response
    response = {article: "Updated after publication" for article in updated_articles}

    return jsonify(response)


@app.route('/articles_by_month/<int:year>/<int:month>', methods=['GET'])
def articles_by_month(year, month):
    try:
        # Validate the input year and month
        if month < 1 or month > 12:
            return jsonify({"message": "Invalid month. Must be between 1 and 12."})

        # Set the start and end dates for the specified month
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        # Convert dates to ISO format strings
        start_date_iso = start_date.isoformat()
        end_date_iso = end_date.isoformat()

        # Print debug information
        print(f"Start date (ISO): {start_date_iso}")
        print(f"End date (ISO): {end_date_iso}")

        # Query to count the number of articles published in the specified month
        count = collection.count_documents({
            "publication_date": {"$gte": start_date_iso, "$lt": end_date_iso}
        })

        # Format the month name
        month_name = start_date.strftime("%B")

        # Construct the response
        response = {
            f"{month_name} {year}": f"({count} articles)"
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/articles_by_word_count_range/<int:min_word_count>/<int:max_word_count>', methods=['GET'])
def articles_by_word_count_range(min_word_count, max_word_count):
    try:
        # Validate the input word counts
        if min_word_count < 0 or max_word_count < min_word_count:
            return jsonify({"message": "Invalid word count range."})

        # Query to count articles within the specified word count range
        count = collection.count_documents({
            "word_count": {"$gte": min_word_count, "$lte": max_word_count}
        })

        # Construct the response
        response = {
            f"Articles between {min_word_count} and {max_word_count} words": f"({count} articles)"
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})

@app.route('/articles_with_specific_keyword_count/<int:count>', methods=['GET'])
def articles_with_specific_keyword_count(count):
        try:
            # Validate the input keyword count
            if count < 0:
                return jsonify({"message": "Invalid keyword count."})

            # Query to count articles with exactly the specified number of keywords
            keyword_count = collection.count_documents({
                "keywords": {"$size": count}
            })

            # Construct the response
            response = {
                f"Articles with exactly {count} keywords": f"({keyword_count} articles)"
            }
            return jsonify(response)

        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"})

#
# @app.route('/articles_by_specific_date/<date>', methods=['GET'])
# def articles_by_specific_date(date):
#     try:
#         # Validate and parse the input date
#         try:
#             specific_date = datetime.strptime(date, "%Y-%m-%d")
#         except ValueError:
#             return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."})
#
#         # Create a date range for the specific date
#         start_of_day = datetime.combine(specific_date, datetime.min.time())
#         end_of_day = start_of_day + timedelta(days=1)
#
#         # Query to find articles published on the specific date
#         count = collection.count_documents({
#             "publication_date": {
#                 "$gte": start_of_day,
#                 "$lt": end_of_day
#             }
#         })
#
#         # Construct the response
#         response = {
#             f"Articles published on {date}": f"({count} articles)"
#         }
#         return jsonify(response)
#
#     except Exception as e:
#         return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/articles_containing_text/<text>', methods=['GET'])
def articles_containing_text(text):
    try:
        # Escape special characters in text to avoid issues in the query
        query_text = text.replace('$', r'\$').replace('.', r'\.')

        # Query to find articles containing the specified text in their content
        articles = collection.find({
            "full_text": {
                "$regex": query_text,
                "$options": "i"  # Case-insensitive search
            }
        })

        # Extract the titles or any other desired field from the result
        result = [article["title"] for article in articles]

        # Construct the response
        response = {
            f"Articles containing '{text}'": result
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/articles_with_more_than/<int:word_count>', methods=['GET'])
def articles_with_more_than(word_count):
    try:
        # Query to count articles with more than the specified word count
        count = collection.count_documents({
            "word_count": {
                "$gt": word_count
            }
        })

        # Construct the response
        response = {
            f"Articles with more than {word_count} words": f"({count} articles)"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/articles_grouped_by_coverage', methods=['GET'])
def articles_grouped_by_coverage():
        try:
            # Aggregate the articles to group by coverage category and count the number of articles for each coverage
            pipeline = [
                {"$unwind": "$classes"},
                {"$match": {"classes.mapping": "coverage"}},
                {"$group": {
                    "_id": "$classes.value",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]

            results = list(collection.aggregate(pipeline))

            # Format the results for response
            response = {
                f"Coverage on {result['_id']}": f"({result['count']} articles)"
                for result in results
            }

            return jsonify(response)

        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/articles_last_X_hours/<int:hours>', methods=['GET'])
def articles_last_X_hours(hours):
    try:
        # Calculate the time X hours ago from now
        time_threshold = datetime.now() - timedelta(hours=hours)

        # Query for articles published within the last X hours
        results = collection.find({"publication_date": {"$gte": time_threshold.isoformat()}})

        # Format the results for response
        articles = [
            f"{article['title']} (Published within the last {hours} hours)"
            for article in results
        ]

        if not articles:
            return jsonify({"message": f"No articles found within the last {hours} hours."})

        return jsonify(articles)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/articles_by_title_length', methods=['GET'])
def articles_by_title_length():
    try:
        # Initialize a dictionary to store the count of articles by title length
        title_length_counts = {}

        # Retrieve all articles
        articles = collection.find({}, {"title": 1})

        # Process each article to calculate title length (in words)
        for article in articles:
            title = article.get("title", "")
            word_count = len(title.split())

            if word_count in title_length_counts:
                title_length_counts[word_count] += 1
            else:
                title_length_counts[word_count] = 1

        # Format the response
        response = [
            f"Titles with {word_count} words ({count} articles)"
            for word_count, count in title_length_counts.items()
        ]

        if not response:
            return jsonify({"message": "No articles found."})

        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})

@app.route('/most_updated_articles', methods=['GET'])
def most_updated_articles():
    try:
        # Assuming updates are tracked via an array of timestamps
        articles = collection.aggregate([
            {"$match": {"update_timestamps": {"$exists": True}}},
            {"$addFields": {"update_count": {"$size": "$update_timestamps"}}},
            {"$sort": {"update_count": -1}},
            {"$limit": 10}
        ])

        response = [
            f"{article.get('title', 'Unnamed Article')} (Updated {article.get('update_count', 0)} times)"
            for article in articles
        ]

        if not response:
            return jsonify({"message": "No updated articles found."})

        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})


@app.route('/recent_articles', methods=['GET'])
def recent_articles():
    try:
        # Find the 10 most recent articles by publication date
        articles = collection.find().sort("publication_date", -1).limit(10)

        response = []
        for article in articles:
            title = article.get("title", "No title")
            publication_date = article.get("publication_date")

            # Calculate relative time (e.g., "Published today", "Published yesterday")
            relative_time = calculate_relative_time(publication_date)
            response.append(f"{title} ({relative_time})")

        if not response:
            return jsonify({"message": "No recent articles found."})

        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})

def calculate_relative_time(publication_date):
    try:
        # Handle date strings with extra fractional seconds by trimming them
        if '.' in publication_date:
            publication_date = publication_date.split('.')[0]

        # Parse the cleaned publication date into a datetime object
        pub_date = datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%S")
        now = datetime.now()

        # Calculate the difference in days between now and the publication date
        days_diff = (now - pub_date).days

        if days_diff == 0:
            return "Published today"
        elif days_diff == 1:
            return "Published yesterday"
        else:
            return f"Published {days_diff} days ago"

    except ValueError as ve:
        # Handle any parsing errors
        return f"Error parsing date: {ve}"

@app.route('/articles_by_coverage/<coverage>', methods=['GET'])
def articles_by_coverage(coverage):
    try:
        # Find all articles where the coverage in the 'classes' field matches the given coverage
        articles = collection.find({"classes": {"$elemMatch": {"mapping": "coverage", "value": coverage}}})

        response = []
        for article in articles:
            title = article.get("title", "No title")
            response.append(f"Coverage on {coverage}: {title}")

        if not response:
            return jsonify({"message": f"No articles found for coverage: {coverage}."})

        return jsonify(response)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"})



if __name__ == '__main__':
    app.run(debug=True)