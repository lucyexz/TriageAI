import time
from ollama import Client

OLLAMA_HOST = "http://ollama:11434"
EMBED_MODEL = "nomic-embed-text"


def get_client(host: str = OLLAMA_HOST) -> Client:
    return Client(host=host)


def generate_embeddings(
    texts: list[str],
    client: Client,
    model: str = EMBED_MODEL,
    batch_size: int = 200,
    retry_attempts: int = 3,
) -> list[list[float]]:
    all_embeddings = []
    total = len(texts)

    for i in range(0, total, batch_size):
        batch = texts[i : i + batch_size]

        for attempt in range(retry_attempts):
            try:
                resp = client.embed(model=model, input=batch)
                all_embeddings.extend(resp["embeddings"])
                break
            except Exception as e:
                if attempt == retry_attempts - 1:
                    raise RuntimeError(
                        f"Falha ao gerar embeddings após {retry_attempts} tentativas: {e}"
                    ) from e
                time.sleep(2**attempt)

        print(f"[Embeddings] {min(i + batch_size, total)}/{total} gerados")

    return all_embeddings
