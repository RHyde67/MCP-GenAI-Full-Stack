# tools/llm_tool.py

import httpx

async def mcp_generate_llm_response(question: str, context_items: list[str]):
    """
    Temporary local LLM implementation using Ollama.
    """

    # Combine question + context however you like:
    full_prompt = question
    if context_items:
        full_prompt += "\n\nContext:\n" + "\n".join(context_items)

    payload = {
        "model": "llama3:8b",
        "prompt": full_prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json=payload
        )
        response.raise_for_status()
        data = response.json()

    # Ollama returns the generated text under "response"
    answer = data.get("response", "").strip()

    return {
        "answer": answer,
        "length": len(answer),
        "empty": answer == "",
    }