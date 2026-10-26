"""tradutor.py - Tradutor de Editais.
Fluxo: texto -> trechos com página -> busca por tema (RAG simples) -> resultado com citação.
Sem IA, mostra os trechos encontrados (extrativo). Com IA, ela só reescreve o que foi encontrado."""
import re
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import ia
from motor import STOP, sem_acento

LIMITE_CARACTERES = 200_000
MARCADOR = re.compile(r"\[\[P[ÁA]GINA\s+(\d+)\]\]", re.I)

TOPICOS = {
    "Quem pode participar": ["podem participar", "poderao participar", "pessoa fisica", "pessoas fisicas", "pessoa juridica", "maiores de", "residen", "coletivo", "candidato", "elegib", "proponente"],
    "O que está sendo oferecido": ["premio", "premiacao", "bolsa", "remuneracao", "r$", "apoio financeiro", "cache", "recurso", "valor"],
    "Requisitos obrigatórios": ["obrigatori", "exigid", "requisito", "devera", "devem ", "comprovar", "comprovacao", "necessari"],
    "Documentos necessários": ["documento", "rg", "cpf", "comprovante", "portfolio", "certidao", "declaracao", "curriculo", "carta", "copia"],
    "Etapas de inscrição": ["inscric", "inscrev", "formulario", "plataforma", "enviar", "envio", "preenchimento", "site oficial"],
    "Critérios de seleção": ["criterio", "selecao", "avaliad", "avaliacao", "pontuacao", "notas", "comissao", "julgamento"],
    "Prazos importantes": ["prazo", "ate o dia", "periodo", "cronograma", "resultado", "recurso", "ate "],
    "Possíveis impedimentos": ["vedad", "impedid", "nao podera", "nao poderao", "desclassific", "proibid", "nao sera permitido", "nao serao aceit", "inabilit"],
}

DATA_RE = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+de\s+[a-zçã]+\s+de\s+\d{4})", re.I)
VALOR_RE = re.compile(r"R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?")


def esc_md(t: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+!|>~$])", r"\\\1", t)


def extrair_pdf(arquivo) -> str:
    """Lê um PDF com texto (não lê imagens/escaneados) e devolve texto com marcadores de página."""
    from pypdf import PdfReader

    leitor = PdfReader(arquivo)
    partes = []
    for i, pag in enumerate(leitor.pages, 1):
        partes.append(f"[[PÁGINA {i}]]\n{pag.extract_text() or ''}")
    texto = "\n".join(partes)
    if len(re.sub(r"\[\[P[ÁA]GINA \d+\]\]|\s", "", texto)) < 50:
        raise ValueError("Não consegui ler texto neste PDF (pode ser um documento escaneado). Copie e cole o texto do edital.")
    return texto


def dividir_em_trechos(texto: str, max_chars: int = 600) -> list[dict]:
    texto = texto[:LIMITE_CARACTERES]
    pedacos = MARCADOR.split(texto)
    paginas = []
    if len(pedacos) == 1:
        paginas.append((None, pedacos[0]))
    else:
        if pedacos[0].strip():
            paginas.append((None, pedacos[0]))
        for i in range(1, len(pedacos), 2):
            paginas.append((int(pedacos[i]), pedacos[i + 1]))
    trechos = []
    for pag, conteudo in paginas:
        prefixo = ""
        for bloco in re.split(r"\n\s*\n|\n(?=\s*\d+(?:\.\d+)*\.?\s)", conteudo):
            bloco = re.sub(r"\s+", " ", bloco).strip()
            if len(bloco) < 15:
                continue
            if len(bloco) < 70 and not bloco.endswith((".", ";", ":", ")")):
                prefixo = (prefixo + " " + bloco).strip()  # título curto: junta ao próximo trecho
                continue
            if prefixo:
                bloco, prefixo = f"{prefixo} - {bloco}", ""
            frases = re.split(r"(?<=[.;:])\s+", bloco)
            atual = ""
            for f in frases:
                if len(atual) + len(f) > max_chars and atual:
                    trechos.append({"pagina": pag, "texto": atual.strip()}); atual = ""
                atual += f + " "
            if atual.strip():
                trechos.append({"pagina": pag, "texto": atual.strip()})
        if prefixo:  # sobrou um título/trecho curto no fim da página: não pode se perder
            trechos.append({"pagina": pag, "texto": prefixo})
    return trechos


def _por_topico(trechos, topico, k=3):
    palavras = TOPICOS[topico]
    pontuados = []
    for pos, t in enumerate(trechos):
        norm = sem_acento(t["texto"])
        acertos = sum(1 for p in palavras if p in norm)
        if acertos:
            pontuados.append((acertos, -pos, t))
    pontuados.sort(key=lambda x: (x[0], x[1]), reverse=True)
    escolhidos = [t for _, _, t in pontuados[:k]]
    return sorted(escolhidos, key=lambda t: trechos.index(t))


def _datas_validas(trechos):
    achadas, vistas = [], set()
    for t in trechos:
        for m in DATA_RE.finditer(t["texto"]):
            bruto = m.group(1)
            if "/" in bruto:
                ok = False
                for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                    try:
                        datetime.strptime(bruto, fmt); ok = True; break
                    except ValueError:
                        pass
                if not ok:
                    continue
            if (bruto, t["pagina"]) in vistas:
                continue
            vistas.add((bruto, t["pagina"]))
            ini = max(0, m.start() - 70)
            achadas.append({"data": bruto, "pagina": t["pagina"], "contexto": t["texto"][ini:m.end() + 70]})
    return achadas


def _valores(trechos):
    return sorted({(v, t["pagina"]) for t in trechos for v in VALOR_RE.findall(t["texto"])}, key=lambda x: (x[1] or 0, x[0]))


def _pg(p):
    return f"p. {p}" if p else "sem página"


def _tarefas(res):
    tarefas = ["Ler o edital oficial completo. Este resumo ajuda, mas não substitui o documento."]
    for d in res["datas"][:6]:
        tarefas.append(f"Anotar na agenda a data {d['data']} ({_pg(d['pagina'])}).")
    for tema, rotulo in (("Requisitos obrigatórios", "os requisitos"), ("Documentos necessários", "a lista de documentos"), ("Possíveis impedimentos", "as vedações e motivos de desclassificação")):
        pgs = sorted({t["pagina"] for t in res["topicos"].get(tema, []) if t["pagina"]})
        if res["topicos"].get(tema):
            tarefas.append(f"Conferir {rotulo}" + (f" (páginas {', '.join(map(str, pgs))})." if pgs else "."))
    tarefas.append("Preparar portfólio e descrição do projeto (veja as abas Portfólio e Aprender).")
    tarefas.append("Fazer a inscrição só pelo canal oficial indicado no edital e guardar o comprovante.")
    return tarefas


def analisar(texto: str, token=None) -> dict:
    trechos = dividir_em_trechos(texto)
    res = {"trechos": trechos, "topicos": {t: _por_topico(trechos, t) for t in TOPICOS},
           "datas": _datas_validas(trechos), "valores": _valores(trechos), "resumo_ia": None}
    res["tarefas"] = _tarefas(res)
    if token and trechos:
        blocos = []
        for tema, lista in res["topicos"].items():
            if lista:
                blocos.append(f"## {tema}\n" + "\n".join(f"[{_pg(t['pagina'])}] {t['texto']}" for t in lista))
        contexto = "\n\n".join(blocos)[:9000]
        sistema = ("Você explica editais culturais em português muito simples para artistas iniciantes. "
                   "Use SOMENTE os trechos fornecidos. Para cada tema, escreva 1 a 3 frases curtas e cite a página no formato [p. N]. "
                   "Se o tema não tiver trechos, escreva 'Não encontrei no texto analisado.' "
                   "Nunca invente exigências, valores ou datas. Não prometa aprovação. "
                   "No final, escreva 'Interpretação:' apenas se precisar interpretar algo, deixando claro que é interpretação.")
        res["resumo_ia"] = ia.gerar(token, sistema, contexto, 900)
    return res


EXPANSAO = {  # a busca é por palavras; estes sinônimos ajudam a achar o trecho certo
    "document": "rg cpf comprovante portfolio enviados copia carta declaracao",
    "prazo": "ate data periodo inscricoes",
    "inscrev": "inscricao formulario",
    "inscric": "inscricao formulario",
    "ganh": "premio valor r$",
    "receb": "premio valor r$",
    "pagamento": "premio valor r$",
    "pode particip": "podem participar pessoas maiores residencia",
    "quem": "podem participar pessoas",
}


def _expandir(pergunta: str) -> str:
    q = sem_acento(pergunta)
    extras = " ".join(v for k, v in EXPANSAO.items() if k in q)
    return f"{q} {extras}".strip()


def perguntar(trechos, pergunta: str, token=None, k=3):
    """Responde usando só o documento. Devolve (resposta|None, trechos_encontrados)."""
    if not trechos:
        return None, []
    vet = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), sublinear_tf=True)
    try:
        m = vet.fit_transform([sem_acento(t["texto"]) for t in trechos])
    except ValueError:
        return None, []
    notas = cosine_similarity(vet.transform([_expandir(pergunta)]), m).ravel()
    ordem = [i for i in notas.argsort()[::-1][:k] if notas[i] >= 0.08]
    achados = [trechos[i] for i in ordem]
    if not achados:
        return None, []
    resposta = None
    if token:
        ctx = "\n".join(f"[{_pg(t['pagina'])}] {t['texto']}" for t in achados)
        resposta = ia.gerar(token, "Responda em português simples usando SOMENTE os trechos. Cite [p. N]. Se não responderem, diga que não encontrou no texto analisado. Não invente.", f"Trechos:\n{ctx}\n\nPergunta: {pergunta}", 400)
    return resposta, achados
