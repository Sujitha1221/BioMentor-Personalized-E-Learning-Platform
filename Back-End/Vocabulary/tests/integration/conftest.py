import pytest
import sys
import asyncio
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database import db

# Mark all tests in this directory as integration tests
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration
]

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create an event loop policy for the test session."""
    return asyncio.get_event_loop_policy()

@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    """Create an event loop for the test session."""
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db(event_loop):
    """Create a test database connection."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_db = client.test_vocabulary_db
    yield test_db
    # Cleanup: Drop the test database after tests
    await client.drop_database("test_vocabulary_db")
    await client.close()

@pytest.fixture(autouse=True)
async def setup_database(test_db):
    """Set up the database for each test."""
    # Replace the global db with test_db
    global db
    db = test_db
    yield
    # Clean up collections after each test
    await db["flashcards"].delete_many({})
    await db["users"].delete_many({})
    await db["leaderboard"].delete_many({}) 