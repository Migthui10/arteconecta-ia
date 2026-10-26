"""estado.py - memória da sessão e 'salvar/continuar depois' por arquivo JSON.
Não há banco de dados: o progresso só persiste se o usuário baixar o arquivo."""
import json

import streamlit as st

CHAVES = {"perfil": {}, "progresso": {}, "candidaturas": [], "posts_usuario": [], "bloqueados": [], "denuncias": [], "portfolio": {}}
VERSAO = 1


def iniciar():
    for k, v in CHAVES.items():
        if k not in st.session_state:
            st.session_state[k] = json.loads(json.dumps(v))


def exportar() -> str:
    dados = {k: st.session_state[k] for k in CHAVES}
    dados["_versao"] = VERSAO
    return json.dumps(dados, ensure_ascii=False, indent=2, default=str)


def importar_callback():
    arq = st.session_state.get("upload_progresso")
    if arq is None:
        return
    try:
        dados = json.loads(arq.getvalue().decode("utf-8"))
        if not isinstance(dados, dict) or dados.get("_versao") != VERSAO:
            raise ValueError("arquivo inválido")
        for k, padrao in CHAVES.items():
            valor = dados.get(k, padrao)
            if type(valor) is not type(padrao):
                raise ValueError(f"campo {k} inválido")
            st.session_state[k] = valor
        for chave in [c for c in st.session_state if str(c).startswith("w::")]:
            del st.session_state[chave]  # força os campos a lerem os valores importados
        st.session_state["aviso_import"] = ("ok", "Progresso carregado.")
    except Exception:
        st.session_state["aviso_import"] = ("erro", "Não consegui ler esse arquivo. Use o arquivo baixado pelo botão 'Salvar meu progresso'.")


def checkbox(rotulo: str, chave: str, **kw) -> bool:
    """Caixa de marcar cujo valor fica em session_state.progresso (sobrevive a filtros e trocas de aba)."""
    k = f"w::{chave}"

    def _salvar():
        st.session_state.progresso[chave] = st.session_state[k]

    return st.checkbox(rotulo, value=st.session_state.progresso.get(chave, False), key=k, on_change=_salvar, **kw)
