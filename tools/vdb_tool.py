# tools/vdb_tool.py

import httpx
from config.settings import get_settings


async def call_vdb_api(query: str, top_k: int, vdb_id: str):
    """
    Calls the Vector DB API using the /query endpoint.

    Returns:
        JSON response from the VDB API.
    """
    settings = get_settings()
    url = f"{settings.VDB_BASE_URL}/query"

    payload = {
        "vdb_id": vdb_id,
        "vdb_query": {
            "query": query,
            "top_k": top_k,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def mcp_search_vector_db(query: str, top_k: int = 5, vdb_id: str = "default"):
    """
    Wrapper used by the MCP server to call the VDB.
    Normalizes output for the LLM.
    """
    raw = await call_vdb_api(query=query, top_k=top_k, vdb_id=vdb_id)

    # Expecting {"results": [...]}
    results = raw.get("results", [])

    # Standardize structure for Llama 3
    normalized = []
    for item in results:
        normalized.append({
            "chunk": item.get("chunk", ""),
            "score": float(item.get("score", 0.0)),
            "metadata": item.get("metadata", {}),
        })

    return {
        "results": normalized,
        "count": len(normalized)
    }
    