from app.services.osv_client import OSVQuery, OSVClient
import asyncio

async def test():
    client = OSVClient()
    queries = [OSVQuery(package={'ecosystem': 'npm', 'name': 'express'}, version='4.18.2')]
    
    # Trace through query_batch manually
    results = {}
    uncached_queries = []
    
    for query in queries:
        print(f'Query type: {type(query)}')
        print(f'Query.package: {query.package}')
        print(f'Query.version: {query.version}')
        
        # This is line 72
        try:
            cached = client.cache.get(query.package['ecosystem'], query.package['name'], query.version)
            print(f'Cached: {cached}')
        except Exception as e:
            print(f'Cache get error: {e}')
        
        if cached is not None:
            key = f"{query.package['ecosystem']}:{query.package['name']}@{query.version}"
            results[key] = cached
        else:
            uncached_queries.append(query)
    
    print(f'Uncached queries: {len(uncached_queries)}')
    
    await client.close()

asyncio.run(test())