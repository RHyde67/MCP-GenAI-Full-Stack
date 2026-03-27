from config.settings import get_settings
import httpx

settings = get_settings()

async def call_llm(question: str, context_items: list[str]):
    """
    Unified LLM adapter:
    - local Ollama mode (LLM_MODE=local)
    - remote OpenAI-compatible mode (LLM_MODE=remote)
    """

    # Build question + context
    context_block = "\n\n".join(context_items) if context_items else ""
    prompt = f"{question}\n\nContext:\n{context_block}"

    if settings.LLM_MODE.lower() == "local":
        return await _call_local_ollama(prompt)
    else:
        return await _call_remote_openai(prompt)


async def _call_local_ollama(full_prompt: str):
    url = f"{settings.LLM_BASE_URL}/api/generate"
    print("🔍 LOCAL LLM CALL:", url)

    payload = {
        "model": "llama3:8b",
        "prompt": full_prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(url, json=payload)
        res.raise_for_status()
        return res.json().get("response", "").strip()


async def _call_remote_openai(full_prompt: str):
    url = f"{settings.LLM_BASE_URL}/v1/chat/completions"
    print("🌐 REMOTE LLM CALL:", url)

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
        res = await client.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()