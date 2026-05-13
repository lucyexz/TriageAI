SYSTEM_PROMPT = """Você é um assistente especializado em triagem hospitalar.
Com base nos sintomas do paciente e no contexto médico fornecido, responda com:
1. Possíveis condições (da mais à menos provável)
2. Nível de prioridade (1-Emergência, 2-Urgente, 3-Pouco urgente, 4-Não urgente)
3. Ações iniciais recomendadas

Seja objetivo e baseie-se apenas no contexto fornecido."""


def build_prompt(symptoms: str, rag_results: list[dict]) -> list[dict]:
    context = "\n\n".join(
        f"Doença: {r['disease']}\n{r['texto_rag']}" for r in rag_results
    )
    user_msg = (
        f"Sintomas relatados: {symptoms}\n\n"
        f"Contexto médico recuperado:\n{context}\n\n"
        "Forneça a análise de triagem."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
