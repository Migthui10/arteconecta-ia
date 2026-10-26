"""comunidade.py - pedidos de colaboração, filtros, recomendação sem popularidade e segurança."""
import re

TIPOS = ["Pedido de colaboração", "Convite para projeto", "Procura de profissional",
         "Projeto precisa de participantes", "Troca de conhecimentos"]
FORMATOS = ["Presencial", "Online", "Híbrido"]
DISPONIBILIDADES = ["Flexível", "Fins de semana", "Noites", "Dias úteis"]

EXEMPLOS = [
    dict(id="cx-1", autor="Exemplo_A", tipo="Procura de profissional", area="Música", procura="Ilustração", titulo="Banda procura ilustrador(a) para capa de EP",
         descricao="Exemplo fictício: buscamos alguém para criar a arte de um EP independente. Podemos trocar divulgação e cachê simbólico.", estado="SP", cidade="Cidade Exemplo", formato="Online", disponibilidade="Flexível", contato="", exemplo=True),
    dict(id="cx-2", autor="Exemplo_B", tipo="Projeto precisa de participantes", area="Teatro e dança", procura="Música", titulo="Teatro de rua precisa de músicos ao vivo",
         descricao="Exemplo fictício: espetáculo curto para praças, ensaios aos sábados.", estado="MG", cidade="Cidade Exemplo", formato="Presencial", disponibilidade="Fins de semana", contato="", exemplo=True),
    dict(id="cx-3", autor="Exemplo_C", tipo="Troca de conhecimentos", area="Audiovisual e fotografia", procura="Qualquer área", titulo="Troco aulas de edição de vídeo por aulas de violão",
         descricao="Exemplo fictício: encontros on-line quinzenais, sem custo para os dois lados.", estado="RJ", cidade="Cidade Exemplo", formato="Online", disponibilidade="Noites", contato="", exemplo=True),
    dict(id="cx-4", autor="Exemplo_D", tipo="Convite para projeto", area="Artes visuais", procura="Artesanato", titulo="Mural coletivo no bairro: convite para artistas",
         descricao="Exemplo fictício: pintura coletiva de um muro cedido pela associação de moradores.", estado="SP", cidade="Cidade Exemplo", formato="Presencial", disponibilidade="Fins de semana", contato="", exemplo=True),
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
FONE_RE = re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}")
GOLPE_RE = re.compile(r"(pagamento antecipado|taxa de inscri|deposite|pix para (garantir|reservar)|ganhe dinheiro f[aá]cil)", re.I)


def alertas_privacidade(texto: str) -> list[str]:
    a = []
    if EMAIL_RE.search(texto or "") or FONE_RE.search(texto or ""):
        a.append("Seu texto parece conter e-mail ou telefone. Evite expor dados pessoais em texto aberto; use o campo de contato só se quiser mesmo.")
    if GOLPE_RE.search(texto or ""):
        a.append("O texto menciona cobrança antecipada ou promessa fácil de ganho, um sinal comum de golpe.")
    return a


def filtrar(posts, area="Todas", estado="Todos", formato="Todos", disponibilidade="Todas", tipo="Todos", bloqueados=()):
    saida = []
    for p in posts:
        if p["autor"] in bloqueados: continue
        if area != "Todas" and area not in (p["area"], p["procura"]): continue
        if estado != "Todos" and not (p["estado"] == estado or p["formato"] == "Online"): continue
        if formato != "Todos" and p["formato"] != formato: continue
        if disponibilidade != "Todas" and p["disponibilidade"] not in (disponibilidade, "Flexível"): continue
        if tipo != "Todos" and p["tipo"] != tipo: continue
        saida.append(p)
    return saida


def recomendar(posts, perfil, bloqueados=(), n=2):
    """Combina interesses, área, local e formato. NÃO usa curtidas, seguidores ou engajamento."""
    pares = []
    for p in posts:
        if p["autor"] in bloqueados: continue
        pts, motivos = 0, []
        if p["procura"] == perfil.get("area"):
            pts += 40; motivos.append(f"Procura alguém de {p['procura']}, a sua área.")
        elif p["area"] == perfil.get("area"):
            pts += 20; motivos.append("É da mesma área que você; pode haver troca de experiências.")
        if p["formato"] == "Online":
            pts += 15; motivos.append("É on-line.")
        elif p["estado"] == perfil.get("estado"):
            pts += 20; motivos.append("É no seu estado.")
        if p["tipo"] == "Troca de conhecimentos" and perfil.get("nivel") == "Iniciante":
            pts += 10; motivos.append("Troca de conhecimentos costuma ajudar quem está começando.")
        if pts >= 20:
            pares.append((p, pts, motivos))
    pares.sort(key=lambda x: -x[1])
    return pares[:n]
