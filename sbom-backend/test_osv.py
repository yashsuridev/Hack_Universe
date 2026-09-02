import pytest
from app.services.osv_client import OSVQuery, OSVClient
import asyncio

@pytest.mark.asyncio
async def test():
    client = OSVClient()
    # Test a single query using OSVQuery dataclass
    queries = [OSVQuery(package={'ecosystem': 'npm', 'name': 'express'}, version='4.18.2')]
    result = await client.query_batch(queries)
    print('Query result:', len(result))
    for k, v in result.items():
        print(f'  {k}: {len(v)} vulnerabilities')
        if v:
            print(f'  First vuln ID: {v[0].get("id", "N/A")}')
    
    # Close the client
    await client.close()

asyncio.run(test())