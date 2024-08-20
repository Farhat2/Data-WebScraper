import pymongo
import json
import os

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]

# Load and insert JSON data
output_dir = 'output'  # Path to the directory containing my JSON files
for filename in os.listdir(output_dir):
    if filename.endswith(".json"):
        with open(os.path.join(output_dir, filename), encoding='utf-8') as f:
            try:
                data = json.load(f)
                collection.insert_many(data)
                print(f"Data from {filename} inserted successfully!")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {filename}: {e}")
            except Exception as e:
                print(f"An error occurred with {filename}: {e}")

print("Data insertion complete!")