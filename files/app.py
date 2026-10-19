"""
ArteConecta IA - protótipo (interface Streamlit)
Rodar localmente:  streamlit run app.py
"""
import os
from datetime import date

import pandas as pd
import streamlit as st

from motor import Motor, carregar_editais, filtrar_editais

st.set_page_config(page_title="ArteConecta IA", page_icon="🎨", layout="centered")

st.markdown(
    """
    <style>
      .stApp { background-color: #faf7ff; }
      h1, h2, h3 { color: #4b2a8a; }
      .stButton>button { border-radius: 20px; border: 1px solid #4b2a8a; color: #4b2a8a; }
      .fonte { font-size: 0.85rem; color: #6b5a8a; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_motor():
    return Motor()


motor = get_motor()
editais = carregar_editais()


def pegar_token():
    try:
        return st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")
    except Exception:
        return os.getenv("HF_TOKEN")


token = pegar_token()

# ---------- Barra lateral: perfil do usuário ----------
with st.sidebar:
    st.header("Seu perfil")
    area = st.selectbox(
        "Área artística",
        ["Todas", "Música", "Artes visuais", "Teatro e dança", "Artesanato", "Audiovisual", "Literatura", "Cultura popular"],
    )
    estados = ["Todos"] + sorted(e for e in editais["estado"].unique() if e != "Nacional")
    estado = st.selectbox("Estado", estados)
    st.selectbox("Você é", ["Artista profissional", "Amador", "Estudante", "Educador(a)"])
    st.divider()
    st.caption("IA ativa ✅" if token else "Modo sem IA generativa (respostas direto das fontes).")

st.title("🎨 ArteConecta IA")
st.caption("Direitos, editais e oportunidades para artistas independentes.")
st.warning(
    "Protótipo de demonstração. Os editais listados são **exemplos fictícios**. "
    "Sempre confirme prazos e regras na fonte oficial.",
    icon="⚠️",
)

aba_chat, aba_editais, aba_aprender, aba_comunidade = st.tabs(
    ["💬 Pergunte", "📢 Editais", "📚 Aprender", "🤝 Comunidade"]
)

# ---------- Aba 1: Chatbot ----------
with aba_chat:
    if "msgs" not in st.session_state:
        st.session_state.msgs = [
            {"role": "assistant", "texto": "Oi! Sou o ArteConecta. Pergunte sobre direitos culturais, MEI, editais ou direitos autorais.", "fontes": []}
        ]

    st.write("**Perguntas rápidas:**")
    c1, c2 = st.columns(2)
    atalhos = {
        "Como virar MEI sendo artista?": c1,
        "O que é a Lei Paulo Gustavo?": c2,
        "Como me inscrever em um edital?": c1,
        "Posso tocar na rua sem autorização?": c2,
    }
    pergunta = None
    for texto, coluna in atalhos.items():
        if coluna.button(texto, use_container_width=True):
            pergunta = texto

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["texto"])
            if m["fontes"]:
                st.markdown("<div class='fonte'>Fonte: " + " | ".join(m["fontes"]) + "</div>", unsafe_allow_html=True)

    digitada = st.chat_input("Escreva sua dúvida...")
    pergunta = digitada or pergunta

    if pergunta:
        st.session_state.msgs.append({"role": "user", "texto": pergunta, "fontes": []})
        with st.spinner("Buscando nas fontes..."):
            resposta, fontes, _ = motor.responder(pergunta, token)
        st.session_state.msgs.append({"role": "assistant", "texto": resposta, "fontes": fontes})
        st.rerun()

# ---------- Aba 2: Editais ----------
with aba_editais:
    st.subheader("Oportunidades para você")
    so_abertos = st.checkbox("Mostrar só editais abertos", value=True)
    lista = filtrar_editais(editais, estado, area, so_abertos)
    if lista.empty:
        st.info("Nenhum edital encontrado com esses filtros. Tente mudar a área ou o estado.")
    else:
        for _, e in lista.iterrows():
            dias = (e["prazo"] - date.today()).days
            with st.container(border=True):
                st.markdown(f"**{e['nome']}**")
                st.write(f"🎭 {e['area']}  •  📍 {e['estado']} - {e['cidade']}  •  💰 {e['valor']}")
                if dias >= 0:
                    st.write(f"⏰ Inscrições até **{e['prazo'].strftime('%d/%m/%Y')}** (faltam {dias} dias)")
                else:
                    st.write(f"❌ Encerrado em {e['prazo'].strftime('%d/%m/%Y')}")
                st.link_button("Ver edital", e["link"])

# ---------- Aba 3: Aprender ----------
with aba_aprender:
    st.subheader("Guias em linguagem simples")
    for d in motor.docs:
        with st.expander(d["titulo"]):
            st.write(d["texto"])
            st.caption(f"Fonte: {d['fonte']}")

# ---------- Aba 4: Comunidade ----------
with aba_comunidade:
    st.subheader("Ajude a manter a plataforma viva")
    st.write("Conhece um edital, feira ou curso? Cadastre aqui. (No protótipo, as sugestões ficam só nesta sessão; baixe a lista para enviar à equipe.)")
    if "sugestoes" not in st.session_state:
        st.session_state.sugestoes = []
    with st.form("sugestao", clear_on_submit=True):
        nome = st.text_input("Nome da oportunidade")
        col_a, col_b = st.columns(2)
        s_area = col_a.text_input("Área artística")
        s_cidade = col_b.text_input("Cidade/Estado")
        prazo = st.date_input("Prazo de inscrição")
        link = st.text_input("Link oficial")
        if st.form_submit_button("Enviar sugestão") and nome:
            st.session_state.sugestoes.append(
                {"nome": nome, "area": s_area, "local": s_cidade, "prazo": prazo, "link": link}
            )
            st.success("Obrigado! Sua sugestão foi registrada.")
    if st.session_state.sugestoes:
        df_s = pd.DataFrame(st.session_state.sugestoes)
        st.dataframe(df_s, use_container_width=True)
        st.download_button("Baixar sugestões (CSV)", df_s.to_csv(index=False).encode("utf-8"), "sugestoes.csv", "text/csv")

st.divider()
st.caption("ArteConecta IA • Código aberto • Seus dados não são armazenados neste protótipo.")
