import asyncio, httpx
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.security import create_access_token

async def test():
    client_db = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client_db.krishakbondhu
    admin = await db.users.find_one({'role': 'admin'})
    token = create_access_token({'sub': str(admin['_id'])})
    headers = {'Authorization': f'Bearer {token}'}
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get('http://localhost:8000/api/v1/admin/predictions?page_size=2', headers=headers)
        print('Predictions API Status:', resp.status_code)
        data = resp.json()
        for p in data.get('predictions', []):
            print('  Disease:', p.get('disease_name'), '| user_name:', p.get('user_name'), '| user_location:', p.get('user_location'))
        
        resp = await client.get('http://localhost:8000/api/v1/admin/expert-requests?page_size=2', headers=headers)
        print('\nExpert Requests API Status:', resp.status_code)
        data = resp.json()
        for r in data.get('requests', []):
            print('  Title:', r.get('title')[:40], '| user_location:', r.get('user_location'), '| expert_response:', (r.get('expert_response') or '')[:30])

asyncio.run(test())
