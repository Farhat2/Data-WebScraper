import stanza
from pymongo import MongoClient

# Initialize Stanza pipeline for Arabic with NER
try:
    nlp = stanza.Pipeline('ar', processors='tokenize,ner')
    print("Stanza NER model loaded successfully.")
except Exception as e:
    print(f"Error initializing Stanza: {e}")
    nlp = None

# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['almayadeen']
    collection = db['articles']
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db, collection = None, None

# Function to extract named entities using Stanza
def analyze_entities_stanza(text):
    if nlp is None:
        print("Stanza NER model not loaded.")
        return None

    try:
        # Run NER on the text
        doc = nlp(text)
        entities = {'per': [], 'loc': [], 'org': []}

        # Extract entities from Stanza NER results
        for ent in doc.ents:
            if ent.type == 'PER':  # Person entity
                entities['per'].append(ent.text)
            elif ent.type == 'LOC':  # Location entity
                entities['loc'].append(ent.text)
            elif ent.type == 'ORG':  # Organization entity
                entities['org'].append(ent.text)

        # Remove duplicates
        entities = {key: list(set(val)) for key, val in entities.items()}
        return entities
    except Exception as e:
        print(f"Error analyzing entities: {e}")
        return None

# Function to fetch articles, analyze entities, and update MongoDB
def process_articles_for_entities():
    if db is None or collection is None:
        print("MongoDB not initialized.")
        return

    try:
        # Count how many articles need entity processing, skipping the first 2900
        query = {"full_text": {"$exists": True}}
        article_count = collection.count_documents(query)  # Count total articles
        print(f"Number of articles found that need processing: {article_count}")

        # Fetch all articles that need entity processing, skipping the first 2900
        articles_to_process = collection.find(query).skip(2900).limit(7100)

        updated_count = 0  # Counter to track updated articles

        for article in articles_to_process:
            full_text = article.get('full_text', '')
            if not full_text:
                print(f"No text found for article ID: {article['_id']}")
                continue

            # Analyze named entities
            entities = analyze_entities_stanza(full_text)
            if entities:
                print(f"Updating article ID {article['_id']} with new entities: {entities}")

                # First remove the existing 'entities' field
                collection.update_one(
                    {"_id": article['_id']},
                    {"$unset": {"entities": ""}}  # Safely remove the existing entities field
                )

                # Then add the new entities
                result = collection.update_one(
                    {"_id": article['_id']},
                    {"$set": {"entities": entities}}  # Set the new entities
                )

                # Check if the update was successful
                if result.matched_count > 0:
                    updated_count += 1
                    print(f"Successfully updated article ID {article['_id']}")
                else:
                    print(f"Failed to update article ID {article['_id']}")
            else:
                print(f"Entity recognition failed for article ID {article['_id']}")

        print(f"Total articles updated: {updated_count}")

    except Exception as e:
        print(f"Error processing articles for entity recognition: {e}")

# Example usage: Process all articles in the collection
process_articles_for_entities()
