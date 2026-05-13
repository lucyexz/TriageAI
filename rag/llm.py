import os

from ollama import Client

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")


def generate_response(messages: list[dict]) -> str:
    client = Client(host=OLLAMA_HOST)
    response = client.chat(model=LLM_MODEL, messages=messages)
    return response["message"]["content"]
