"""
ArteConecta IA - interface (Streamlit)
Rodar localmente:  streamlit run app.py
A lógica fica nos módulos: oportunidades, plano, caminho, tradutor, portfolio, comunidade, motor, ia.
"""
import json
import os
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

import caminho as cm
import comunidade as co
import estado
import oportunidades as op
import plano as pl
import portfolio as pf
import tema
import tradutor as tr
from motor import Motor

st.set_page_config(page_title="ArteConecta IA", page_icon="🎨", layout="centered")

tema.aplicar()
tema.reiniciar_contagem()

estado.iniciar()
ss = st.session_state
HOJE = date.today()
ICONES = {"Verificada": "✅", "Desatualizada": "⏳", "Pendente de confirmação": "❓", "Exemplo fictício": "🧪"}


@st.cache_resource
def get_motor():
    return Motor()


@st.cache_data
def get_oportunidades(dia):
    return op.carregar(dia)


def pegar_token():
    try:
        t = st.secrets.get("HF_TOKEN")
    except Exception:
        t = None
    return t or os.getenv("HF_TOKEN")


motor = get_motor()
OPORTUNIDADES = get_oportunidades(HOJE)
TOKEN = pegar_token()
TOKEN_IA = TOKEN if (TOKEN and ss.get("consentimento_ia")) else None


def _i(lista, valor, padrao=0):
    return lista.index(valor) if valor in lista else padrao


def todos_posts():
    return co.EXEMPLOS + ss.posts_usuario


# ---------- callbacks ----------
def _marcar(chave):
    ss.progresso[chave] = True
    ss[f"w::{chave}"] = True


def _preparar(oid):
    if oid not in ss.candidaturas:
        ss.candidaturas.append(oid)


def _remover(oid):
    if oid in ss.candidaturas:
        ss.candidaturas.remove(oid)


def _editar_perfil():
    ss.editando_perfil = True


def _exemplo_edital():
    with open(os.path.join(os.path.dirname(__file__), "dados", "edital_exemplo.txt"), encoding="utf-8") as f:
        ss["tr_texto"] = f.read()


def _denunciar(pid, chave_motivo):
    ss.denuncias.append({"post": pid, "motivo": ss.get(chave_motivo, "Outro"), "data": str(HOJE)})
    ss["aviso_com"] = "Denúncia registrada. Neste protótipo ela fica salva só na sua sessão (use 'Baixar denúncias')."


def _bloquear(autor):
    if autor not in ss.bloqueados:
        ss.bloqueados.append(autor)


def _salvar_texto(chave, k):
    ss.portfolio[chave] = ss[k]


# ---------- barra lateral ----------
with st.sidebar:
    st.header("Configurações")
    if TOKEN:
        st.checkbox(
            "Permitir IA externa (Hugging Face)",
            key="consentimento_ia",
            help="Se marcado, os textos que você digitar nas ferramentas de IA (Tradutor, Portfólio, Pergunte) serão enviados ao serviço Hugging Face para gerar a resposta.",
        )
        st.caption("IA ativada ✅" if TOKEN_IA else "IA desligada: as ferramentas usam o modo sem IA.")
    else:
        st.caption("IA não configurada. Tudo funciona no modo sem IA (veja o README para ativar).")
    st.divider()
    st.subheader("Salvar e continuar depois")
    st.caption("O app não guarda seus dados. Baixe o arquivo para retomar depois.")
    st.download_button("⬇️ Salvar meu progresso", estado.exportar(), "arteconecta-progresso.json", "application/json")
    st.file_uploader("Carregar progresso salvo", type="json", key="upload_progresso", on_change=estado.importar_callback)
    if ss.get("aviso_import"):
        tipo_av, msg_av = ss.pop("aviso_import")
        (st.success if tipo_av == "ok" else st.error)(msg_av)
    st.divider()
    with st.expander("O que funciona de verdade?"):
        st.markdown(
            "- **Funciona sem configurar:** perfil, plano, filtros do Radar, compatibilidade, checklist, Tradutor (modo trechos), "
            "Portfólio (modo organizado + HTML), guias, perguntas por busca nos guias.\n"
            "- **Precisa de IA externa:** resumo em linguagem simples, reescrita do portfólio.\n"
            "- **Ainda é protótipo:** oportunidades são **exemplos fictícios**; comunidade só na sua sessão; sem mapa e sem contas."
        )

tema.cabecalho()
st.warning("Protótipo de demonstração. As oportunidades são **exemplos fictícios**. Sempre confirme prazos e regras na fonte oficial.", icon="⚠️")


# ---------- INÍCIO ----------
def formulario_perfil():
    p = ss.perfil
    st.info("Pedimos só o necessário para sugerir seus próximos passos. Seus dados ficam apenas nesta sessão (ou no arquivo que você baixar).")
    with st.form("form_perfil"):
        apelido = st.text_input("Como podemos te chamar? (nome ou nome artístico)", value=p.get("apelido", ""), key="w::p_apelido")
        area = st.selectbox("Área artística", op.AREAS, index=_i(op.AREAS, p.get("area")), key="w::p_area")
        c1, c2 = st.columns(2)
        uf = c1.selectbox("Estado", op.ESTADOS, index=_i(op.ESTADOS, p.get("estado", "SP")), key="w::p_uf")
        cidade = c2.text_input("Cidade", value=p.get("cidade", ""), key="w::p_cidade")
        nivel = st.selectbox("Nível de experiência", op.NIVEIS, index=_i(op.NIVEIS, p.get("nivel")), key="w::p_nivel")
        objetivo = st.selectbox("Objetivo principal agora", pl.OBJETIVOS, index=_i(pl.OBJETIVOS, p.get("objetivo")), key="w::p_obj")
        dif = st.multiselect("Principais dificuldades (pode marcar várias)", pl.DIFICULDADES, default=[d for d in p.get("dificuldades", []) if d in pl.DIFICULDADES], key="w::p_dif")
        tipos = st.multiselect("Tipos de oportunidade que você procura", op.TIPOS, default=[t for t in p.get("tipos", []) if t in op.TIPOS], key="w::p_tipos")
        ok = st.form_submit_button("Salvar e ver meu painel")
    if ok:
        if not apelido.strip():
            st.error("Escreva como podemos te chamar para continuar.")
        else:
            ss.perfil = dict(apelido=apelido.strip(), area=area, estado=uf, cidade=cidade.strip(), nivel=nivel, objetivo=objetivo, dificuldades=dif, tipos=tipos)
            ss.editando_perfil = False
            st.rerun()


def cartao_resumo(o, c):
    with tema.cartao():
        st.markdown(f"**{o['nome']}**")
        prazo = o["prazo"].strftime("%d/%m/%Y") if o["prazo"] else "não informado"
        st.caption(f"{ICONES[o['estado_info']]} {o['estado_info']} • Prazo: {prazo} • Compatibilidade {c['nivel']} ({c['pontos']}%)")
        st.caption("Veja os detalhes e o checklist na aba 📡 Radar.")


def painel():
    p = ss.perfil
    tarefas = pl.gerar_plano(p)
    feitas = sum(1 for t in tarefas if ss.progresso.get(f"tar:{t['id']}"))
    with tema.cartao():
        st.markdown(f"### Olá, {p['apelido']}!")
        st.caption(f"{p['area']} • {p.get('cidade') or 'cidade não informada'}/{p['estado']} • nível {p['nivel']}")
        st.progress(feitas / len(tarefas) if tarefas else 0.0, text=f"Plano: {feitas} de {len(tarefas)} tarefas concluídas")
        st.button("Editar perfil", on_click=_editar_perfil)

    st.subheader("🎯 Seu próximo passo")
    pend = [t for t in tarefas if not ss.progresso.get(f"tar:{t['id']}")]
    with tema.cartao():
        if pend:
            t = pend[0]
            st.markdown(f"**{t['titulo']}**")
            st.write(t["descricao"])
            st.caption(f"Por que para você: {t['porque']} • Onde: {t['onde']}")
            st.button("Marcar como concluída", key=f"ini_done_{t['id']}", on_click=_marcar, args=(f"tar:{t['id']}",))
        else:
            st.success("Você concluiu todas as tarefas do plano. Veja novas oportunidades no Radar.")

    st.subheader("📡 Oportunidades compatíveis")
    for o, c in op.recomendadas(OPORTUNIDADES, p, 3, HOJE):
        cartao_resumo(o, c)

    st.subheader("📝 Candidaturas em preparação")
    if not ss.candidaturas:
        st.caption("Nenhuma ainda. No Radar, toque em “Preparar candidatura” em uma oportunidade.")
    for oid in ss.candidaturas:
        o = next((x for x in OPORTUNIDADES if x["id"] == oid), None)
        if o:
            feitos, total = cm.progresso(oid, cm.gerar_checklist(o), ss.progresso)
            with tema.cartao():
                st.markdown(f"**{o['nome']}**")
                st.progress(feitos / total, text=f"{feitos} de {total} etapas")

    st.subheader("🤝 Sugestões de colaboração")
    sug = co.recomendar(todos_posts(), p, ss.bloqueados)
    if not sug:
        st.caption("Nenhuma sugestão agora. Veja a aba 🤝 Comunidade.")
    for post, _, motivos in sug:
        with tema.cartao():
            st.markdown(f"**{post['titulo']}**" + (" 🧪 exemplo fictício" if post.get("exemplo") else ""))
            st.caption(" ".join(motivos))


def aba_inicio():
    st.markdown("## Seu talento merece uma oportunidade.")
    st.markdown("#### Vamos encontrar o próximo passo?")
    if not ss.perfil or ss.get("editando_perfil"):
        formulario_perfil()
    else:
        painel()


# ---------- PRIMEIRO PASSO ----------
def aba_primeiro_passo():
    st.subheader("🧭 Meu primeiro passo")
    if not ss.perfil:
        st.info("Preencha seu perfil na aba 🏠 Início para receber um plano.")
        return
    st.caption("Este plano é montado por regras, a partir das suas respostas, e muda se você mudar o perfil. Não garante resultados.")
    for t in pl.gerar_plano(ss.perfil):
        with tema.cartao():
            estado.checkbox(t["titulo"], f"tar:{t['id']}")
            st.write(t["descricao"])
            st.caption(f"Por que para você: {t['porque']}")
            st.caption(f"Onde: {t['onde']}")


# ---------- RADAR ----------
def checklist(o):
    itens = cm.gerar_checklist(o)
    feitos, total = cm.progresso(o["id"], itens, ss.progresso)
    st.progress(feitos / total, text=f"{feitos} de {total} etapas")
    for it in itens:
        estado.checkbox(it["texto"], f"chk:{o['id']}:{it['id']}")
        st.caption(f"{it['tipo']} • {it['detalhe']}")
    st.caption("Concluir o checklist não garante elegibilidade, aprovação ou contratação.")
    st.button("Remover das minhas candidaturas", key=f"rad_rem_{o['id']}", on_click=_remover, args=(o["id"],))


def cartao(o, c=None):
    with tema.cartao():
        st.markdown(f"**{o['nome']}**")
        st.caption(f"{ICONES[o['estado_info']]} Informação: {o['estado_info']} • {o['tipo']} • {o['organizacao']}")
        st.write(o["descricao"])
        if o["prazo"]:
            dias = (o["prazo"] - HOJE).days
            st.write(f"⏰ Prazo: **{o['prazo'].strftime('%d/%m/%Y')}**" + (f" (faltam {dias} dias)" if dias >= 0 else " (encerrado)"))
        else:
            st.write("⏰ Prazo: não informado")
        local = o["modalidade"] + (f" • {o['cidade']}/{o['estado']}" if o["modalidade"] != "Online" and o["cidade"] else f" • {o['estado']}")
        st.write(f"📍 {local}")
        st.write(f"💰 {o['beneficio'] or 'Benefício não informado'} • Remuneração: {o['remuneracao']} • Gratuito: {o['gratuito']} • Nível: {o['nivel']}")
        st.write(f"👤 Quem pode participar: {o['elegibilidade'] or 'não informado'}")
        if o["documentos_lista"]:
            st.write("📎 Documentos exigidos:\n" + "\n".join(f"- {d}" for d in o["documentos_lista"]))
        ver = o["ultima_verificacao"].strftime("%d/%m/%Y") if o["ultima_verificacao"] else "nunca"
        st.caption(f"Última verificação: {ver} • Fonte: {o['fonte']}")
        st.caption(f"ℹ️ {o['disponibilidade']}")
        st.link_button("Abrir página oficial", o["link"])
        if c:
            st.markdown(f"🎯 Compatibilidade com seu perfil: **{c['nivel']} ({c['pontos']}%)**")
            with st.expander("Por que recomendamos e o que conferir"):
                for m in c["motivos"]:
                    st.write(f"✔ {m}")
                for m in c["conferir"]:
                    st.write(f"⚠ Conferir: {m}")
        if o["id"] in ss.candidaturas:
            with st.expander("✅ Caminho até a oportunidade", expanded=True):
                checklist(o)
        elif o["situacao_prazo"] != "Encerrada":
            st.button("Preparar candidatura", key=f"rad_prep_{o['id']}", on_click=_preparar, args=(o["id"],))


def aba_radar():
    st.subheader("📡 Radar de oportunidades")
    p = ss.perfil
    with st.expander("🔎 Filtros", expanded=False):
        c1, c2 = st.columns(2)
        area = c1.selectbox("Área artística", ["Todas"] + op.AREAS, index=_i(op.AREAS, p.get("area"), -1) + 1, key="f_area")
        uf = c2.selectbox("Estado", ["Todos"] + op.ESTADOS, index=_i(op.ESTADOS, p.get("estado"), -1) + 1, key="f_uf")
        c3, c4 = st.columns(2)
        mod = c3.selectbox("Modalidade", ["Todas"] + op.MODALIDADES, key="f_mod")
        tipo = c4.selectbox("Tipo", ["Todos"] + op.TIPOS, key="f_tipo")
        c5, c6 = st.columns(2)
        nivel = c5.selectbox("Nível de experiência", ["Todos"] + op.NIVEIS, key="f_nivel")
        prazos = {"Qualquer prazo": None, "Até 15 dias": 15, "Até 30 dias": 30, "Até 90 dias": 90}
        prazo = c6.selectbox("Prazo de inscrição", list(prazos), key="f_prazo")
        gratis = st.checkbox("Só gratuitas", key="f_gratis")
        pagas = st.checkbox("Só com remuneração", key="f_pagas")
        abertas = st.checkbox("Esconder encerradas", value=True, key="f_abertas")
    lista = op.filtrar(OPORTUNIDADES, area, uf, mod, gratis, pagas, tipo, nivel, prazos[prazo], abertas, HOJE)
    st.caption(f"{len(lista)} oportunidades encontradas. Todas as que aparecem aqui são exemplos fictícios.")
    if p:
        pares = sorted(((o, op.compatibilidade(o, p, HOJE)) for o in lista), key=lambda x: -x[1]["pontos"])
    else:
        st.info("Preencha seu perfil na aba 🏠 Início para ver a compatibilidade.")
        pares = [(o, None) for o in lista]
    if not pares:
        st.info("Nenhuma oportunidade com esses filtros. Tente mudar a área, o estado ou o prazo.")
    for o, c in pares:
        cartao(o, c)


# ---------- TRADUTOR ----------
def aba_tradutor():
    st.subheader("📄 Tradutor de editais")
    st.caption("Cole o texto de um edital ou envie um PDF. A ferramenta organiza o que o documento diz, com a página de cada trecho.")
    modo = st.radio("Como você quer enviar?", ["Colar o texto", "Enviar arquivo (PDF ou TXT)"], horizontal=True, key="tr_modo")
    texto = None
    if modo == "Colar o texto":
        texto = st.text_area("Texto do edital", height=220, key="tr_texto")
        st.caption("Para citar páginas, escreva [[PÁGINA 1]] antes do texto de cada página.")
        st.button("Usar edital de exemplo (fictício)", on_click=_exemplo_edital)
    else:
        arq = st.file_uploader("Arquivo do edital", type=["pdf", "txt"], key="tr_arquivo")
        if arq:
            try:
                texto = tr.extrair_pdf(arq) if arq.name.lower().endswith(".pdf") else arq.getvalue().decode("utf-8", errors="replace")
            except ValueError as e:
                st.error(str(e))
            except Exception:
                st.error("Não consegui abrir este arquivo. Tente colar o texto.")
    link = st.text_input("Link do edital original (opcional)", key="tr_link")
    if st.button("Analisar edital", type="primary"):
        if not texto or len(texto.strip()) < 100:
            st.warning("Cole ou envie um texto de edital com mais conteúdo.")
        else:
            ss.analise = tr.analisar(texto, TOKEN_IA)
            ss.analise_link = link.strip()
            ss.analise_perg = None
    a = ss.get("analise")
    if not a:
        return
    if not a["trechos"]:
        st.error("Não encontrei texto para analisar.")
        return
    st.warning("Esta é uma ajuda de leitura. Não substitui o edital oficial e não garante aprovação.")
    if ss.get("analise_link", "").startswith(("http://", "https://")):
        st.link_button("Abrir edital original", ss["analise_link"])
    if a["resumo_ia"]:
        st.markdown("### Resumo em linguagem simples")
        st.markdown(a["resumo_ia"])
        st.caption("🤖 Texto gerado por IA a partir dos trechos abaixo (interpretação). Os trechos originais são os fatos. Em caso de diferença, vale o documento.")
    elif TOKEN and not ss.get("consentimento_ia"):
        st.info("Modo sem IA. Para um resumo em linguagem simples, autorize a IA na barra lateral (☰) e analise de novo.")
    elif TOKEN:
        st.info("A IA não respondeu agora. Mostrando os trechos do documento, sem reescrita.")
    else:
        st.info("Modo sem IA (IA não configurada): abaixo estão os trechos do documento organizados por tema, sem reescrita.")
    if a["datas"] or a["valores"]:
        st.markdown("### Datas e valores encontrados")
        for d in a["datas"]:
            st.write(f"📅 **{d['data']}** ({tr._pg(d['pagina'])}): …{tr.esc_md(d['contexto'])}…")
        for v, pg in a["valores"]:
            st.write(f"💰 **{v}** ({tr._pg(pg)})")
    st.markdown("### O que o documento diz, por tema")
    for tema, lista in a["topicos"].items():
        with st.expander(tema):
            if not lista:
                st.write("Não encontrei trechos sobre este tema no texto analisado.")
            for t in lista:
                st.markdown("> " + tr.esc_md(t["texto"]))
                st.caption(f"Trecho original • {tr._pg(t['pagina'])}")
    st.markdown("### ✅ Tarefas para preparar sua candidatura")
    for i, t in enumerate(a["tarefas"]):
        st.checkbox(t, key=f"ed_{i}")
    st.markdown("### Pergunte ao documento")
    perg = st.text_input("Sua pergunta sobre este edital", key="tr_perg")
    if st.button("Buscar no edital") and perg.strip():
        ss.analise_perg = (perg, *tr.perguntar(a["trechos"], perg, TOKEN_IA))
    if ss.get("analise_perg"):
        _, resp, achados = ss.analise_perg
        if not achados:
            st.info("Não encontrei isso no texto analisado. Releia o edital oficial ou pergunte à organização.")
        else:
            if resp:
                st.markdown(resp)
                st.caption("🤖 Resposta de IA baseada nos trechos abaixo.")
            for t in achados:
                st.markdown("> " + tr.esc_md(t["texto"]))
                st.caption(f"Trecho original • {tr._pg(t['pagina'])}")


# ---------- PORTFÓLIO ----------
def aba_portfolio():
    st.subheader("🖼️ Portfólio de bolso")
    st.caption("Você informa os fatos; a ferramenta organiza e melhora a escrita. Ela não cria prêmios, clientes, experiências ou projetos. Revise tudo antes de usar.")
    d0 = ss.portfolio.get("dados", {})
    p = ss.perfil
    with st.form("form_portfolio"):
        nome = st.text_input("Nome artístico (ou seu nome)", value=d0.get("nome", p.get("apelido", "")), key="w::pfm_nome")
        area = st.selectbox("Área de atuação", op.AREAS, index=_i(op.AREAS, d0.get("area", p.get("area"))), key="w::pfm_area")
        cidade = st.text_input("Cidade do portfólio", value=d0.get("cidade", p.get("cidade", "")), key="w::pfm_cidade")
        bio = st.text_area("Sobre você (escreva do seu jeito, 2 a 5 frases)", value=d0.get("biografia", ""), key="w::pfm_bio")
        habil = st.text_input("Habilidades (separe por vírgula)", value=d0.get("habilidades", ""), key="w::pfm_habil")
        proj = st.text_area("Obras e projetos (um por linha)", value=d0.get("projetos", ""), key="w::pfm_proj")
        exp = st.text_area("Experiências reais (apresentações, exposições, cursos; uma por linha)", value=d0.get("experiencias", ""), key="w::pfm_exp")
        links = st.text_area("Links de trabalhos publicados (um por linha)", value=d0.get("links", ""), key="w::pfm_links")
        contato = st.text_input("Contato profissional (opcional)", value=d0.get("contato", ""), key="w::pfm_contato")
        gerar = st.form_submit_button("Gerar meu portfólio")
    if gerar:
        dados = dict(nome=nome, area=area, cidade=cidade, biografia=bio, habilidades=habil, projetos=proj, experiencias=exp, links=links, contato=contato)
        r = pf.montar(dados, TOKEN_IA)
        ss.portfolio = {"dados": dados, "apresentacao": r["apresentacao"], "biografia": r["biografia"], "avisos": r["avisos"], "usou_ia": r["usou_ia"]}
        ss["w::pf_ap"], ss["w::pf_bio"] = r["apresentacao"], r["biografia"]
    if not ss.portfolio.get("dados"):
        return
    pt = ss.portfolio
    for aviso in pt.get("avisos", []):
        st.warning(aviso)
    if pt.get("usou_ia"):
        st.caption("🤖 Textos reescritos por IA a partir dos seus dados. Edite abaixo o que for necessário.")
    else:
        st.caption("Modo sem IA: seus textos foram organizados, sem reescrita. Você pode editar abaixo.")
    st.text_area("Apresentação curta (editável)", value=pt.get("apresentacao", ""), key="w::pf_ap", on_change=_salvar_texto, args=("apresentacao", "w::pf_ap"))
    st.text_area("Biografia (editável)", value=pt.get("biografia", ""), key="w::pf_bio", on_change=_salvar_texto, args=("biografia", "w::pf_bio"))
    st.markdown("**Estrutura do seu portfólio**")
    for nome_s, ok in pf.estrutura(pt["dados"]):
        st.write(("✅ " if ok else "⬜ ") + nome_s + (" (preenchido)" if ok else " (faltando)"))
    tema = st.selectbox("Modelo visual", list(pf.TEMAS), key="pf_tema")
    html_final = pf.gerar_html(pt["dados"], pt.get("apresentacao", ""), pt.get("biografia", ""), tema)
    st.download_button("⬇️ Baixar portfólio (HTML)", html_final, "meu-portfolio.html", "text/html")
    st.caption("Para PDF: abra o arquivo baixado no navegador e use Ctrl+P ▸ Salvar como PDF. Compartilhar por link ainda não está disponível neste protótipo.")
    components.html(html_final, height=480, scrolling=True)


# ---------- APRENDER ----------
def aba_aprender():
    st.subheader("📚 Aprenda para crescer")
    st.info("Conteúdo educativo. Em temas jurídicos, tributários ou administrativos, confira a fonte oficial: a regra pode depender da sua situação.")
    temas = sorted({d["tema"] for d in motor.docs})
    c1, c2 = st.columns(2)
    tema = c1.selectbox("Tema", ["Todos"] + temas, key="ap_tema")
    nivel = c2.selectbox("Nível do conteúdo", ["Todos", "Iniciante", "Intermediário"], key="ap_nivel")
    docs = [d for d in motor.docs if (tema == "Todos" or d["tema"] == tema) and (nivel == "Todos" or d["nivel"] == nivel)]
    if not docs:
        st.info("Nenhum guia com esses filtros.")
    for d in sorted(docs, key=lambda x: (x["tema"], x["nivel"])):
        with st.expander(f"{d['titulo']} • {d['nivel']}"):
            st.write(d["texto"])
            st.caption(f"{'📜 Fonte oficial' if d['tipo_fonte'] == 'Fonte oficial' else '💡 Orientação geral'} • {d['tema']} • {d['fonte']}")


# ---------- PERGUNTE ----------
def aba_pergunte():
    st.subheader("💬 Pergunte")
    ss.setdefault("msgs", [{"role": "assistant", "texto": "Oi! Sou o ArteConecta. Pergunte sobre direitos culturais, MEI, editais ou direitos autorais.", "fontes": []}])
    c1, c2 = st.columns(2)
    atalhos = [("Como virar MEI sendo artista?", c1), ("O que é a Lei Paulo Gustavo?", c2), ("Como me inscrever em um edital?", c1), ("Posso tocar na rua sem autorização?", c2)]
    pergunta = None
    for i, (texto, col) in enumerate(atalhos):
        if col.button(texto, key=f"atalho_{i}", use_container_width=True):
            pergunta = texto
    for m in ss.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["texto"])
            if m["fontes"]:
                st.caption("Fonte: " + " | ".join(m["fontes"]))
    pergunta = st.chat_input("Escreva sua dúvida...") or pergunta
    if pergunta:
        ss.msgs.append({"role": "user", "texto": pergunta, "fontes": []})
        resposta, fontes, _ = motor.responder(pergunta, TOKEN_IA)
        ss.msgs.append({"role": "assistant", "texto": resposta, "fontes": fontes})
        st.rerun()


# ---------- COMUNIDADE ----------
def aba_comunidade():
    st.subheader("🤝 Comunidade e colaboração")
    st.info("Neste protótipo, as publicações ficam só na sua sessão: outras pessoas ainda não as veem. Uma comunidade real exige banco de dados e moderação (Etapa 3).")
    with st.expander("🛡️ Como se proteger de golpes"):
        st.markdown(
            "- Desconfie de quem pede **pagamento antecipado**, taxa de inscrição ou Pix para “reservar vaga”.\n"
            "- Não envie documentos pessoais, senhas ou códigos recebidos por SMS.\n"
            "- Combine tudo por escrito e peça referências do projeto ou do espaço.\n"
            "- Para o primeiro encontro, escolha um lugar público e avise alguém de confiança.\n"
            "- Publicações que excluam pessoas por raça, gênero, orientação sexual, religião, deficiência ou origem podem ser denunciadas."
        )
    if ss.get("aviso_com"):
        st.success(ss.pop("aviso_com"))
    c1, c2 = st.columns(2)
    area = c1.selectbox("Área", ["Todas"] + op.AREAS, key="c_area")
    uf = c2.selectbox("Estado", ["Todos"] + op.ESTADOS, key="c_uf")
    c3, c4 = st.columns(2)
    formato = c3.selectbox("Formato", ["Todos"] + co.FORMATOS, key="c_formato")
    disp = c4.selectbox("Disponibilidade", ["Todas"] + co.DISPONIBILIDADES, key="c_disp")
    tipo = st.selectbox("Tipo de publicação", ["Todos"] + co.TIPOS, key="c_tipo")
    posts = co.filtrar(todos_posts(), area, uf, formato, disp, tipo, ss.bloqueados)
    st.caption(f"{len(posts)} publicações. Não há ranking por popularidade, curtidas ou seguidores.")
    for p in posts:
        with tema.cartao():
            st.markdown(f"**{p['titulo']}**" + (" 🧪 exemplo fictício" if p.get("exemplo") else ""))
            st.caption(f"{p['tipo']} • de {p['autor']} • área: {p['area']} • procura: {p['procura']}")
            st.write(p["descricao"])
            st.caption(f"📍 {p['formato']} • {p['cidade']}/{p['estado']} • 🕒 {p['disponibilidade']}")
            st.caption(f"Contato: {p['contato']}" if p.get("contato") else "Sem contato público. Neste protótipo ainda não há mensagens internas.")
            with st.expander("Denunciar ou bloquear"):
                k = f"mot_{p['id']}"
                st.selectbox("Motivo", ["Golpe ou cobrança suspeita", "Conteúdo ofensivo ou discriminatório", "Dados pessoais expostos", "Outro"], key=k)
                b1, b2 = st.columns(2)
                b1.button("Denunciar", key=f"den_{p['id']}", on_click=_denunciar, args=(p["id"], k))
                b2.button(f"Bloquear {p['autor']}", key=f"blo_{p['id']}", on_click=_bloquear, args=(p["autor"],))
    if ss.denuncias:
        st.download_button("⬇️ Baixar denúncias registradas", json.dumps(ss.denuncias, ensure_ascii=False, indent=2), "denuncias.json", "application/json")
    if ss.bloqueados:
        st.caption("Bloqueados nesta sessão: " + ", ".join(ss.bloqueados))
    st.markdown("### Publicar um pedido de colaboração")
    with st.form("form_post", clear_on_submit=True):
        tp = st.selectbox("Tipo", co.TIPOS, key="po_tipo")
        titulo = st.text_input("Título", key="po_titulo")
        desc = st.text_area("Descrição", key="po_desc")
        a1, a2 = st.columns(2)
        meu_area = a1.selectbox("Sua área", op.AREAS, index=_i(op.AREAS, ss.perfil.get("area")), key="po_area")
        procura = a2.selectbox("Você procura", ["Qualquer área"] + op.AREAS, key="po_procura")
        b1, b2 = st.columns(2)
        uf_p = b1.selectbox("Estado do projeto", op.ESTADOS, index=_i(op.ESTADOS, ss.perfil.get("estado", "SP")), key="po_uf")
        cid = b2.text_input("Cidade do projeto", key="po_cidade")
        d1, d2 = st.columns(2)
        fm = d1.selectbox("Formato do projeto", co.FORMATOS, key="po_formato")
        dp = d2.selectbox("Sua disponibilidade", co.DISPONIBILIDADES, key="po_disp")
        autor = st.text_input("Nome público (use apelido, não dados completos)", value=ss.perfil.get("apelido", ""), key="po_autor")
        contato = st.text_input("Contato público (opcional; qualquer pessoa verá)", key="po_contato")
        ok = st.form_submit_button("Publicar")
    if ok:
        if not (titulo.strip() and desc.strip() and autor.strip()):
            st.error("Preencha título, descrição e nome público.")
        else:
            for a in co.alertas_privacidade(titulo + " " + desc):
                st.warning(a)
            ss.posts_usuario.append(dict(id=f"u-{len(ss.posts_usuario) + 1}", autor=autor.strip(), tipo=tp, area=meu_area, procura=procura, titulo=titulo.strip(), descricao=desc.strip(),
                                         estado=uf_p, cidade=cid.strip(), formato=fm, disponibilidade=dp, contato=contato.strip(), exemplo=False))
            st.success("Publicado na sua sessão. Ele aparece na lista acima na próxima atualização da página.")


tabs = st.tabs(["🏠 Início", "🧭 Primeiro passo", "📡 Radar", "📄 Tradutor", "🖼️ Portfólio", "📚 Aprender", "💬 Pergunte", "🤝 Comunidade"])
for tab, fn in zip(tabs, [aba_inicio, aba_primeiro_passo, aba_radar, aba_tradutor, aba_portfolio, aba_aprender, aba_pergunte, aba_comunidade]):
    with tab:
        fn()

st.divider()
st.caption("ArteConecta IA • Código aberto • Protótipo: não armazena seus dados em servidor.")
