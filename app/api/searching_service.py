from typing import Dict, List

from app.api.clients.crossref_client import CrossrefClient
from app.api.clients.openAlex_client import OpenAlexClient
from app.api.mappers.ModelParamMapper import ModelParamsMapper


async def main(query:str, params:dict[str, str], rows: int = 2) -> List[Dict]:
    openalex_results = await open_alex_search(query, params, rows)
    crossref_results = await crossref_search(query, params, rows)
    return openalex_results

async def open_alex_search(search:str, params:dict[str, object], rows: int):
    params.update({"search": search})
    params.update({"per-page": rows})
    map_params = ModelParamsMapper.map_parameters(params.copy())
    client = OpenAlexClient()
    results = await client.search_works(map_params)
    await client.close()
    return results

async def crossref_search(query:str, params:dict[str, str], rows: int):
    map_params = get_params(params.copy())
    map_params.update({"query": query})
    map_params.update({"rows": rows})
    client = CrossrefClient()
    results = await client.search_works(map_params)
    await client.close()
    return results

def get_filters(filters: Dict[str, str]):
    if filters:
        filter_parts = []
        for field, value in filters.items():
            print(f"{field}:{value}")
            filter_parts.append(f"{field}:{value}")
        return ",".join(filter_parts)

def get_params(params: dict[str, str]) -> dict[str, object]:
    return { f"query.{key}": value for key, value in params.items() }

