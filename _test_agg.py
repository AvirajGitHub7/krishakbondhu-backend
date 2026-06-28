import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def debug():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.krishakbondhu
    
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$limit": 2},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user",
            }
        },
        {
            "$unwind": {
                "path": "$user",
                "preserveNullAndEmptyArrays": True,
            }
        },
    ]
    
    async for doc in db.prediction_history.aggregate(pipeline):
        u = doc.get('user')
        print('user joined:', u.get('name') if u else 'NONE', '| loc:', u.get('location') if u else 'NONE')

asyncio.run(debug())
