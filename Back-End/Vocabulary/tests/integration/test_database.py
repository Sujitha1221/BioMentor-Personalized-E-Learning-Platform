import pytest
import json

from database import db, load_vocab_into_db

pytestmark = pytest.mark.asyncio

async def test_load_vocab_into_db():
    """Test loading vocabulary into the database."""
    # Clear existing flashcards
    await db["flashcards"].delete_many({})
    
    # Load vocabulary
    await load_vocab_into_db()
    
    # Verify flashcards were loaded
    count = await db["flashcards"].count_documents({})
    assert count > 0
    
    # Verify flashcard structure
    flashcard = await db["flashcards"].find_one()
    assert flashcard is not None
    assert "question" in flashcard
    assert "answer" in flashcard
    assert "_id" in flashcard

async def test_database_connection():
    """Test database connection and basic operations."""
    # Test insert
    test_doc = {"test": "data"}
    result = await db["test_collection"].insert_one(test_doc)
    assert result.inserted_id is not None
    
    # Test find
    doc = await db["test_collection"].find_one({"test": "data"})
    assert doc is not None
    assert doc["test"] == "data"
    
    # Test update
    await db["test_collection"].update_one(
        {"test": "data"},
        {"$set": {"test": "updated"}}
    )
    doc = await db["test_collection"].find_one({"test": "updated"})
    assert doc is not None
    
    # Test delete
    await db["test_collection"].delete_one({"test": "updated"})
    doc = await db["test_collection"].find_one({"test": "updated"})
    assert doc is None 