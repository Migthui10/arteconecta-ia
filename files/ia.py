"""ia.py - único ponto de contato com serviço externo de IA (Hugging Face).
Sem token (ou sem autorização do usuário) devolve None e o app usa o modo alternativo."""
import os


def modelo() -> str:
    return os.getenv("MODELO_HF", "Qwen/Qwen2.5-7B-Instruct")


def gerar(token, sistema: str, usuario: str, max_tokens: int = 800):
    """Devolve o texto gerado ou None (sem token, erro, limite de uso...)."""
    if not token:
        return None
    try:
        from huggingface_hub import InferenceClient

        cliente = InferenceClient(model=modelo(), token=token)
        r = cliente.chat_completion(
            messages=[{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return None
