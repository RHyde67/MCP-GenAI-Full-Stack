# config/settings.py

import os
from functools import lru_cache

class Settings:
    """
    Holds configuration for the MCP server.
    """

    def __init__(self):
        # LOCAL DEVELOPMENT SETTINGS
        #
        # Ollama LLM runs on localhost:11434
        self.LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")

        # Local test VDB (Chroma or mock)
        self.VDB_BASE_URL = os.getenv("VDB_BASE_URL", "http://localhost:8001")

@lru_cache()
def get_settings() -> Settings:
    return Settings()