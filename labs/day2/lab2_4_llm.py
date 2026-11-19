"""Lab 2.4 steps 1 + 3: one provider interface, .env secrets.

OpenAI is the course default; a local model through Ollama is
the offline backup. Both speak the same OpenAI-compatible API,
so only the settings in .env change, never the code.
Starter version: labs/day2/starter/lab2_4_llm.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")  # step 3: secrets come from .env


def _provider() -> tuple[OpenAI, str]:
    """Return a client and a model name for LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        url = os.getenv("OLLAMA_BASE_URL",
                        "http://localhost:11434/v1")
        model = os.getenv("CHAT_MODEL", "llama3")
        return OpenAI(api_key="ollama", base_url=url), model
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing: add it to .env")
    model = os.getenv("CHAT_MODEL", "gpt-4.1")
    return OpenAI(api_key=key), model


def model_name() -> str:
    return _provider()[1]


def chat(messages: list[dict], temperature: float = 0.2) -> str:
    """Send chat messages; return the answer text."""
    client, model = _provider()
    reply = client.chat.completions.create(
        model=model, messages=messages,
        temperature=temperature, timeout=120)
    return reply.choices[0].message.content or ""
