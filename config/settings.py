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
        # Ollama LLM runs on localhost:http://localhost:11434
        # DiSH IP for LLM: http://10.3.2.212:11434")
        # Switch manually here (no env vars needed)
        
        # Default mode
        self.LLM_MODE = "local"   # default fallback
        self.update_llm_mode(self.LLM_MODE)

        self.VDB_BASE_URL = "http://localhost:8001"



    def update_llm_mode(self, mode: str):
        self.LLM_MODE = mode.lower()

        if self.LLM_MODE == "local":
            self.LLM_BASE_URL = "http://localhost:11434"
        else:
            self.LLM_BASE_URL = "http://10.3.2.212:11434"

settings = Settings()   # global shared settings object for use in app