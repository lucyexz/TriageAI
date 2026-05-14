# LEGADO — Interface Gradio não utilizada pelo Dockerfile atual.
# O frontend em produção é frontend/server.py + frontend/index.html (porta 7860).
# Este arquivo é mantido apenas para referência histórica.
import os
import requests
import gradio as gr

API_URL = os.getenv("API_URL", "http://api:8000")


def triage(symptoms: str) -> str:
    if not symptoms.strip():
        return "Por favor, descreva os sintomas do paciente."
    try:
        resp = requests.post(
            f"{API_URL}/query",
            json={"symptoms": symptoms},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]
    except requests.exceptions.ConnectionError:
        return "Erro: API indisponível. Verifique se o serviço está rodando."
    except Exception as e:
        return f"Erro: {e}"


demo = gr.Interface(
    fn=triage,
    inputs=gr.Textbox(
        label="Sintomas do paciente",
        placeholder="Ex: febre alta, dor de cabeça intensa, rigidez na nuca...",
        lines=3,
    ),
    outputs=gr.Textbox(label="Análise de Triagem", lines=15),
    title="TriageAI — Assistente de Triagem Hospitalar",
    description="Descreva os sintomas do paciente para receber análise de triagem com condições prováveis, nível de urgência e ações recomendadas.",
    examples=[
        ["febre alta, dor de cabeça intensa e rigidez na nuca"],
        ["dor no peito, falta de ar e sudorese fria"],
        ["tosse seca persistente, febre leve e perda de olfato"],
    ],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
