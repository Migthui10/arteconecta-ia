"""oportunidades.py - dados, filtros, estado da informação e compatibilidade.
Tudo aqui é regra comum (sem IA): datas, filtros e pontuação são verificáveis."""
from datetime import date
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).parent / "dados"
DIAS_VALIDADE = 30  # depois disso, a informação é considerada desatualizada

AREAS = ["Música", "Artes visuais", "Ilustração", "Teatro e dança", "Artesanato",
         "Audiovisual e fotografia", "Literatura", "Cultura popular e artes de rua"]
ESTADOS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
           "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
NIVEIS = ["Iniciante", "Intermediário", "Experiente"]
TIPOS = ["Edital", "Festival ou exposição", "Oficina ou curso", "Bolsa ou residência",
         "Apresentação remunerada", "Concurso", "Projeto colaborativo", "Chamada aberta"]
MODALIDADES = ["Presencial", "Online", "Híbrido"]


def carregar(hoje: date | None = None) -> list[dict]:
    hoje = hoje or date.today()
    df = pd.read_csv(PASTA / "oportunidades.csv", dtype=str).fillna("")
    df["prazo"] = pd.to_datetime(df["prazo"], errors="coerce").dt.date
    df["ultima_verificacao"] = pd.to_datetime(df["ultima_verificacao"], errors="coerce").dt.date
    registros = df.to_dict("records")
    for o in registros:
        o["prazo"] = None if pd.isna(o["prazo"]) else o["prazo"]
        o["ultima_verificacao"] = None if pd.isna(o["ultima_verificacao"]) else o["ultima_verificacao"]
        o["estado_info"] = estado_info(o, hoje)
        o["situacao_prazo"] = situacao_prazo(o, hoje)
        o["disponibilidade"] = disponibilidade(o)
        o["documentos_lista"] = [d.strip() for d in o["documentos"].split(";") if d.strip()]
    return registros


def situacao_prazo(o, hoje) -> str:
    if o["prazo"] is None:
        return "Prazo não informado"
    return "Encerrada" if o["prazo"] < hoje else "Aberta"


def estado_info(o, hoje) -> str:
    if o["status_base"] == "exemplo":
        return "Exemplo fictício"
    ver = o["ultima_verificacao"]
    if ver is None:
        return "Pendente de confirmação"
    if (hoje - ver).days > DIAS_VALIDADE:
        return "Desatualizada"
    return "Verificada" if o["status_base"] == "verificada" else "Pendente de confirmação"


def disponibilidade(o) -> str:
    """Nunca afirma que está 'aberta' só por estar cadastrada."""
    if o["situacao_prazo"] == "Encerrada":
        return "Prazo cadastrado já passou. Provavelmente encerrada."
    if o["estado_info"] == "Exemplo fictício":
        return "Exemplo para demonstração. Não é uma oportunidade real."
    if o["estado_info"] != "Verificada":
        return "Informação não confirmada recentemente. Confirme na fonte oficial se ainda está aberta."
    if o["situacao_prazo"] == "Prazo não informado":
        return "Prazo não informado. Confirme na fonte oficial."
    return "Dentro do prazo cadastrado. Confirme na fonte oficial antes de se inscrever."


def filtrar(lista, area="Todas", estado="Todos", modalidade="Todas", so_gratuitas=False,
            so_remuneradas=False, tipo="Todos", nivel="Todos", prazo_max_dias=None,
            so_abertas=True, hoje=None):
    hoje = hoje or date.today()
    saida = []
    for o in lista:
        if so_abertas and o["situacao_prazo"] == "Encerrada":
            continue
        if area != "Todas" and o["area"] not in (area, "Todas as áreas"):
            continue
        if estado != "Todos" and not (o["estado"] in (estado, "Nacional") or o["modalidade"] == "Online"):
            continue
        if modalidade != "Todas" and o["modalidade"] != modalidade:
            continue
        if so_gratuitas and o["gratuito"] != "Sim":
            continue
        if so_remuneradas and o["remuneracao"] != "Sim":
            continue
        if tipo != "Todos" and o["tipo"] != tipo:
            continue
        if nivel != "Todos" and o["nivel"] not in (nivel, "Todos os níveis"):
            continue
        if prazo_max_dias is not None:
            if o["prazo"] is None or (o["prazo"] - hoje).days > prazo_max_dias:
                continue
        saida.append(o)
    return sorted(saida, key=lambda o: (o["prazo"] is None, o["prazo"] or date.max))


def compatibilidade(o, perfil: dict, hoje=None) -> dict:
    """Pontua o encaixe perfil x oportunidade e EXPLICA o porquê.
    Devolve {pontos (0-100), nivel, motivos, conferir}."""
    hoje = hoje or date.today()
    pontos, maximo = 0, 35 + 20 + 15
    motivos, conferir = [], []

    area = perfil.get("area")
    if o["area"] == area:
        pontos += 35; motivos.append(f"É da sua área ({area}).")
    elif o["area"] == "Todas as áreas":
        pontos += 20; motivos.append("Aceita todas as áreas artísticas.")
    else:
        conferir.append(f"A área indicada é {o['area']}, diferente da sua.")

    if o["modalidade"] == "Online":
        pontos += 20; motivos.append("É on-line, então você pode participar de qualquer lugar.")
    elif o["estado"] == perfil.get("estado"):
        pontos += 20; motivos.append(f"É no seu estado ({o['estado']}).")
    elif o["estado"] == "Nacional":
        pontos += 15; motivos.append("É aberta a todo o Brasil.")
    else:
        conferir.append(f"Fica em {o['estado']}, fora do seu estado. Veja se aceita inscrição de outros locais.")
    cidade = (perfil.get("cidade") or "").strip().lower()
    if cidade and cidade in o["cidade"].lower():
        pontos += 5; motivos.append("É na sua cidade.")

    if o["nivel"] in ("Todos os níveis", perfil.get("nivel")):
        pontos += 15; motivos.append("O nível de experiência pedido combina com o seu.")
    else:
        conferir.append(f"É indicada para o nível {o['nivel']}; o seu é {perfil.get('nivel', 'não informado')}.")

    tipos = perfil.get("tipos") or []
    if tipos:
        maximo += 20
        if o["tipo"] in tipos:
            pontos += 20; motivos.append(f"É do tipo que você procura ({o['tipo']}).")

    if o["prazo"] is not None and 0 <= (o["prazo"] - hoje).days <= 7:
        conferir.append("O prazo está muito próximo. Veja se dá tempo de reunir os documentos.")
    if o["elegibilidade"]:
        conferir.append(f"Requisito de participação: {o['elegibilidade']}. Confirme se você se enquadra.")
    if o["documentos_lista"]:
        conferir.append("Confira a lista oficial de documentos antes de se inscrever.")

    pct = min(100, round(100 * pontos / maximo))
    nivel = "Alta" if pct >= 70 else "Média" if pct >= 40 else "Baixa"
    return {"pontos": pct, "nivel": nivel, "motivos": motivos, "conferir": conferir}


def recomendadas(lista, perfil, n=3, hoje=None):
    abertas = [o for o in lista if o["situacao_prazo"] != "Encerrada"]
    pares = [(o, compatibilidade(o, perfil, hoje)) for o in abertas]
    pares.sort(key=lambda p: (-p[1]["pontos"], p[0]["prazo"] is None, p[0]["prazo"] or date.max))
    return pares[:n]
