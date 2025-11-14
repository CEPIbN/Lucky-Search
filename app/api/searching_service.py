from app.api.clients.crossref_client import CrossrefClient


async def main(query : str):
    client = CrossrefClient()
    results = await client.search_works(query)
    for r in results:
        print(r)
    await client.close()