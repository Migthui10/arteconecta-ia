"""portfolio.py - Portfólio de bolso. Organiza o que o usuário escreveu; nunca cria fatos."""
import html
import re

import ia


def _limpa(t): return re.sub(r"[ \t]+", " ", (t or "").strip())
def _linhas(t): return [l.strip(" -•\t") for l in (t or "").splitlines() if l.strip()]


def montar_sem_ia(d: dict) -> dict:
    nome = _limpa(d.get("nome")) or "Artista"
    area = _limpa(d.get("area"))
    local = f", em {_limpa(d['cidade'])}" if _limpa(d.get("cidade")) else ""
    habil = [h.strip() for h in re.split(r"[,;\n]", d.get("habilidades") or "") if h.strip()]
    curta = f"{nome} atua em {area}{local}." if area else f"{nome}{local}."
    if habil:
        curta += " Habilidades: " + ", ".join(habil) + "."
    return {"apresentacao": curta, "biografia": _limpa(d.get("biografia")), "usou_ia": False}


def _invencoes(gerado: str, entrada: str) -> list[str]:
    """Alerta simples: números e nomes próprios que NÃO estavam nos dados do usuário."""
    ent = entrada.lower()
    suspeitos = [n for n in set(re.findall(r"\d+", gerado)) if n not in re.findall(r"\d+", entrada)]
    for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wáéíóúâêôãõç]+)", gerado):
        if m.group(1).lower() not in ent:
            suspeitos.append(m.group(1))
    return sorted(set(suspeitos))


def montar(d: dict, token=None) -> dict:
    base = montar_sem_ia(d)
    base["avisos"] = []
    if not (d.get("biografia") or "").strip():
        base["avisos"].append("Você não escreveu uma biografia. Escreva ao menos 2 ou 3 frases sobre você.")
    if not token:
        return base
    entrada = "\n".join(f"{k}: {v}" for k, v in d.items() if v)
    sistema = ("Você ajuda artistas a escrever apresentações profissionais em português simples. "
               "Use SOMENTE os dados fornecidos. É PROIBIDO inventar prêmios, clientes, exposições, datas, formações ou projetos. "
               "Responda exatamente neste formato:\n### APRESENTACAO\n(1 a 2 frases)\n### BIOGRAFIA\n(um parágrafo em terceira pessoa)")
    saida = ia.gerar(token, sistema, entrada, 600)
    if saida and "### APRESENTACAO" in saida and "### BIOGRAFIA" in saida:
        ap = saida.split("### APRESENTACAO")[1].split("### BIOGRAFIA")[0].strip()
        bio = saida.split("### BIOGRAFIA")[1].strip()
        if ap and bio:
            sus = _invencoes(ap + " " + bio, entrada)
            if sus:
                base["avisos"].append("Confira estes termos que não estavam nos seus dados: " + ", ".join(sus) + ". Apague o que não for verdadeiro.")
            base.update(apresentacao=ap, biografia=bio, usou_ia=True)
    else:
        base["avisos"].append("A IA não respondeu agora. Mostrei seu texto organizado, sem reescrita.")
    return base


def estrutura(d: dict) -> list[tuple[str, bool]]:
    return [("Apresentação curta", bool(d.get("nome") and d.get("area"))),
            ("Biografia", bool((d.get("biografia") or "").strip())),
            ("Habilidades", bool((d.get("habilidades") or "").strip())),
            ("Projetos e obras", bool((d.get("projetos") or "").strip())),
            ("Experiências reais", bool((d.get("experiencias") or "").strip())),
            ("Links de trabalhos", bool((d.get("links") or "").strip())),
            ("Contato profissional (opcional)", bool((d.get("contato") or "").strip()))]


TEMAS = {
    "Claro (roxo)": ("#faf7ff", "#1f1535", "#4b2a8a", "#e3d9f5"),
    "Arte de rua": ("#fffefb", "#000000", "#c4006d", "#ffe600"),
    "Alto contraste": ("#ffffff", "#000000", "#00338d", "#000000"),
}


def gerar_html(d: dict, apresentacao: str, biografia: str, tema: str = "Claro (roxo)") -> str:
    bg, tx, ac, bd = TEMAS.get(tema, TEMAS["Claro (roxo)"])
    e = html.escape

    def lista(t):
        l = _linhas(t)
        return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in l) + "</ul>" if l else ""

    def link(x):
        x = x.strip()
        return f'<li><a href="{e(x, quote=True)}" rel="noopener noreferrer">{e(x)}</a></li>' if x.startswith(("http://", "https://")) else f"<li>{e(x)}</li>"

    secoes = []
    if biografia: secoes.append(f"<h2>Biografia</h2><p>{e(biografia)}</p>")
    if d.get("habilidades"): secoes.append(f"<h2>Habilidades</h2><p>{e(_limpa(d['habilidades']))}</p>")
    if d.get("projetos"): secoes.append("<h2>Projetos e obras</h2>" + lista(d["projetos"]))
    if d.get("experiencias"): secoes.append("<h2>Experiências</h2>" + lista(d["experiencias"]))
    if d.get("links"): secoes.append("<h2>Trabalhos publicados</h2><ul>" + "".join(link(x) for x in _linhas(d["links"])) + "</ul>")
    if d.get("contato"): secoes.append(f"<h2>Contato</h2><p>{e(_limpa(d['contato']))}</p>")
    nome = e(_limpa(d.get("nome")) or "Artista")
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{nome} - Portfólio</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;background:{bg};color:{tx};max-width:760px;margin:0 auto;padding:24px;line-height:1.6}}
h1{{color:{ac};margin-bottom:0}}h2{{color:{ac};border-bottom:2px solid {bd};padding-bottom:4px;margin-top:28px}}
.sub{{font-size:1.1rem;margin-top:4px}}a{{color:{ac}}}@media print{{body{{padding:0}}}}</style></head>
<body><h1>{nome}</h1><p class="sub">{e(apresentacao)}</p>{''.join(secoes)}
<p style="font-size:.8rem;margin-top:40px">Criado com ArteConecta IA. Conteúdo informado e revisado pelo próprio artista.</p></body></html>"""
