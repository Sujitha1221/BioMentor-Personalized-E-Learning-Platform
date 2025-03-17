import csv
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "flashcards_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

VOCABULARY_FILE = "data/vocabulary.csv"

async def load_vocab_into_db():
    """Load vocabulary from CSV into MongoDB if not already populated."""
    collection = db["flashcards"]
    existing_count = await collection.count_documents({})
    
    if existing_count == 0:
        with open(VOCABULARY_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            
            vocab_data = [{"question": row[0], "answer": row[1]} for row in reader if len(row) >= 2]
            
            if vocab_data:
                await collection.insert_many(vocab_data)
                print(f"Inserted {len(vocab_data)} vocabulary words into MongoDB.")
