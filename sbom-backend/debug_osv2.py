import pytest
from app.services.osv_client import OSVQuery, OSVClient
import asyncio

@pytest.mark.asyncio
async def test():
    client = OSVClient()
    queries = [OSVQuery(package={'ecosystem': 'npm', 'name': 'express'}, version='4.18.2')]
    
    try:
        result = await client.query_batch(queries)
        print('Result:', result)
    except Exception as e:
        import traceback
        traceback.print_exc()
    
    await client.close()

asyncio.run(test())