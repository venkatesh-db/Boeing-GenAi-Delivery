"""Lab 2.4 STARTER, steps 1 + 3 — one provider interface; .env secrets.

Fill in every TODO. Solution: labs/day2/lab2_4_llm.py
"""
import os  # noqa: F401
from pathlib import Path

from dotenv import load_dotenv  # noqa: F401
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
# TODO step 3: load_dotenv(ROOT / ".env") so os.getenv sees your key.


def _provider() -> tuple[OpenAI, str]:
    """Return a client and a model name for LLM_PROVIDER."""
    # TODO step 1: read LLM_PROVIDER (default "openai").
    #   "ollama": OpenAI(api_key="ollama",
    #             base_url="http://localhost:11434/v1"), model "llama3"
    #   "openai": OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    #             model "gpt-4.1"; raise a clear error if the key is
    #             missing. Never write the key in this file.
    raise NotImplementedError("TODO step 1")


def model_name() -> str:
    return _provider()[1]


def chat(messages: list[dict], temperature: float = 0.2) -> str:
    """Send chat messages; return the answer text."""
    # TODO step 1: client.chat.completions.create(model=...,
    #   messages=messages, temperature=temperature, timeout=120)
    #   and return reply.choices[0].message.content
    raise NotImplementedError("TODO step 1")
