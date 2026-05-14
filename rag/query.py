import os
import sys

from embeddings.generate import generate_embeddings, get_client
from embeddings.indexing import connect, search
from rag.llm import generate_response
from rag.prompt import build_prompt

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
TOP_K = int(os.getenv("TOP_K", "5"))
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")


def _translate_to_english(symptoms: str, client) -> str:
    response = client.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a medical translator. Translate the given medical symptoms from Portuguese to English. Return only the translated text, no explanations.",
            },
            {"role": "user", "content": symptoms},
        ],
    )
    return response["message"]["content"].strip()


def run_rag(symptoms: str) -> str:
    connect(host=MILVUS_HOST, port=MILVUS_PORT)
    client = get_client(host=OLLAMA_HOST)
    symptoms_en = _translate_to_english(symptoms, client)
    embeddings = generate_embeddings([symptoms_en], client, batch_size=1)
    results = search(embeddings[0], top_k=TOP_K)
    messages = build_prompt(symptoms, results)
    return generate_response(messages)


if __name__ == "__main__":
    symptoms = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Sintomas: ")
    print("\n=== ANÁLISE DE TRIAGEM ===\n")
    print(run_rag(symptoms))
