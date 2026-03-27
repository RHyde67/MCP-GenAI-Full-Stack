from config.settings import settings
import httpx

async def mcp_generate_llm_response(question: str, context_items: list[str]):
    """
    Unified LLM adapter inside the MCP tool system.
    Chooses between:
    - LOCAL Ollama (LLM_MODE=local)
    - REMOTE OpenAI-compatible Llama (LLM_MODE=remote)
    """

    # Build question + retrieved context
    context_block = "\n\n".join(context_items) if context_items else ""
    full_prompt = f"{question}\n\nContext:\n{context_block}"

    # Choose correct backend
    if settings.LLM_MODE.lower() == "local":
        return await _call_local_ollama(full_prompt)
    else:
        return await _call_remote_openai(full_prompt)


async def _call_local_ollama(full_prompt: str):
    url = f"{settings.LLM_BASE_URL}/api/generate"
    print("🔍 LLM MODE=LOCAL →", url)

    payload = {
        "model": "llama3:8b",
        "prompt": full_prompt,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        json_data = response.json()

    answer = json_data.get("response", "").strip()
    return {
        "answer": answer,
        "length": len(answer),
        "empty": answer == "",
    }


async def _call_remote_openai(full_prompt: str):
    url = f"{settings.LLM_BASE_URL}/v1/chat/completions"
    print("🌐 LLM MODE=REMOTE →", url)

    payload = {
        "model": "llama3.1:8b",
        "messages": [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": full_prompt},
        ],
        "temperature": 0.2,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        json_data = response.json()

    answer = json_data["choices"][0]["message"]["content"].strip()
    return {
        "answer": answer,
        "length": len(answer),
        "empty": answer == "",
    }