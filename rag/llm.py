import os

from ollama import Client

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")


def generate_response(messages: list[dict], model: str | None = None) -> dict:
    """Returns dict with response text and token counts from Ollama."""
    effective_model = model or LLM_MODEL
    client = Client(host=OLLAMA_HOST)
    raw = client.chat(model=effective_model, messages=messages)
    return {
        "response": raw["message"]["content"],
        "prompt_eval_count": raw.get("prompt_eval_count", 0),
        "eval_count": raw.get("eval_count", 0),
    }
