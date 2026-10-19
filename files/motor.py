"""
motor.py - cérebro do ArteConecta IA (busca + resposta com fontes).

Como funciona (RAG simplificado):
1. Carrega a base de conhecimento (dados/base_conhecimento.json).
2. Quando o usuário pergunta, busca os trechos mais parecidos (TF-IDF).
3. Se houver um token do Hugging Face, um modelo de IA aberto escreve a
   resposta usando SÓ esses trechos. Sem token, mostra os trechos direto.
   Nos dois casos a FONTE é sempre citada.
"""
import json
import os
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PASTA = Path(__file__).parent / "dados"
LIMITE_MINIMO = 0.08  # abaixo disso, o bot admite que não sabe

STOP = [
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na",
    "nos", "nas", "por", "para", "pra", "com", "sem", "e", "ou", "que", "como", "qual",
    "quais", "quando", "onde", "eu", "meu", "minha", "se", "sou", "ser", "ter", "posso",
    "preciso", "quero", "ao", "aos", "e", "eh", "isso", "esse", "essa", "mais", "ja",
]


def sem_acento(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


class Motor:
    def __init__(self):
        self.docs = json.loads((PASTA / "base_conhecimento.json").read_text(encoding="utf-8"))
        textos = [sem_acento(d["titulo"] + " " + d["texto"]) for d in self.docs]
        self.vetorizador = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), sublinear_tf=True)
        self.matriz = self.vetorizador.fit_transform(textos)

    def buscar(self, pergunta: str, k: int = 3):
        q = self.vetorizador.transform([sem_acento(pergunta)])
        notas = cosine_similarity(q, self.matriz).ravel()
        ordem = notas.argsort()[::-1][:k]
        return [(self.docs[i], float(notas[i])) for i in ordem if notas[i] >= LIMITE_MINIMO]

    def responder(self, pergunta: str, token_hf: str | None = None):
        """Devolve (texto_da_resposta, lista_de_fontes, usou_ia)."""
        achados = self.buscar(pergunta)
        if not achados:
            return (
                "Não encontrei isso na minha base de documentos oficiais. "
                "Para não te passar informação errada, procure a Secretaria de Cultura "
                "da sua cidade ou o Sebrae. Você também pode reformular a pergunta "
                "ou sugerir esse tema na aba Comunidade.",
                [],
                False,
            )
        fontes = []
        for d, _ in achados:
            if d["fonte"] not in fontes:
                fontes.append(d["fonte"])

        if token_hf:
            texto = self._gerar_com_ia(pergunta, achados, token_hf)
            if texto:
                return texto, fontes, True

        # Plano B (sem IA): mostra os trechos encontrados
        partes = [f"**{d['titulo']}**\n\n{d['texto']}" for d, _ in achados[:2]]
        return "\n\n---\n\n".join(partes), fontes, False

    def _gerar_com_ia(self, pergunta, achados, token):
        try:
            from huggingface_hub import InferenceClient

            modelo = os.getenv("MODELO_HF", "Qwen/Qwen2.5-7B-Instruct")
            contexto = "\n\n".join(f"[{d['fonte']}] {d['texto']}" for d, _ in achados)
            sistema = (
                "Você é o ArteConecta IA, assistente para artistas independentes do Brasil. "
                "Responda em português simples, curto e acolhedor. Use APENAS o contexto "
                "fornecido. Se o contexto não responder, diga que não sabe e sugira procurar "
                "a Secretaria de Cultura. Nunca invente datas, valores ou leis. "
                "Lembre que a pessoa deve confirmar prazos e regras na fonte oficial."
            )
            cliente = InferenceClient(model=modelo, token=token)
            r = cliente.chat_completion(
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"},
                ],
                max_tokens=500,
                temperature=0.2,
            )
            return r.choices[0].message.content.strip()
        except Exception:
            return None  # qualquer falha -> cai no plano B


def carregar_editais() -> pd.DataFrame:
    df = pd.read_csv(PASTA / "editais.csv")
    df["prazo"] = pd.to_datetime(df["prazo"]).dt.date
    df["situacao"] = df["prazo"].apply(lambda d: "Aberto" if d >= date.today() else "Encerrado")
    return df


def filtrar_editais(df, estado="Todos", area="Todas", so_abertos=True):
    if estado != "Todos":
        df = df[df["estado"].isin([estado, "Nacional"])]
    if area != "Todas":
        df = df[df["area"].isin([area, "Todas as áreas"])]
    if so_abertos:
        df = df[df["situacao"] == "Aberto"]
    return df.sort_values("prazo")
