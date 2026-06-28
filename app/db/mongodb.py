"""
KrishakBondhu - MongoDB Connection
Async MongoDB client using Motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

# Global client and database references
_client: AsyncIOMotorClient = None
_database: AsyncIOMotorDatabase = None


async def connect_to_mongodb():
    """Initialize the MongoDB connection. Called on app startup."""
    global _client, _database
    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    _database = _client[settings.MONGODB_DB_NAME]

    # Create indexes
    await _database.users.create_index("email", unique=True)
    await _database.disease_info.create_index("disease_name", unique=True)
    await _database.posts.create_index([("created_at", -1)])
    await _database.comments.create_index("post_id")
    await _database.expert_requests.create_index([("created_at", -1)])

    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongodb_connection():
    """Close the MongoDB connection. Called on app shutdown."""
    global _client
    if _client:
        _client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance. Must be called after connect_to_mongodb()."""
    return _database
