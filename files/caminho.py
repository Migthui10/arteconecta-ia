"""caminho.py - checklist 'Caminho até a oportunidade'.
Separa o que vem da oportunidade (requisito oficial) do que é sugestão de preparação."""

OFICIAL = "Requisito da oportunidade"
SUGESTAO = "Sugestão de preparação"


def gerar_checklist(o: dict) -> list[dict]:
    itens = []
    if o.get("elegibilidade"):
        itens.append(dict(tipo=OFICIAL, texto="Conferir se você pode participar", detalhe=o["elegibilidade"]))
    else:
        itens.append(dict(tipo=OFICIAL, texto="Conferir quem pode participar", detalhe="Os critérios não foram informados. Veja na fonte oficial."))
    prazo = o["prazo"].strftime("%d/%m/%Y") if o.get("prazo") else "não informado"
    itens.append(dict(tipo=OFICIAL, texto="Confirmar o prazo de inscrição na fonte oficial", detalhe=f"Prazo cadastrado: {prazo}."))
    if o["tipo"] in ("Edital", "Bolsa ou residência", "Concurso", "Chamada aberta"):
        itens.append(dict(tipo=SUGESTAO, texto="Separar as obras ou trabalhos do portfólio", detalhe="Escolha os que mais combinam com o tema da oportunidade."))
        itens.append(dict(tipo=SUGESTAO, texto="Preparar a descrição do seu projeto ou proposta", detalhe="Escreva em frases curtas: o que você vai fazer, para quem e como."))
    for d in o.get("documentos_lista", []):
        itens.append(dict(tipo=OFICIAL, texto=f"Reunir: {d}", detalhe="Confira o formato exigido na fonte oficial."))
    itens.append(dict(tipo=SUGESTAO, texto="Revisar todas as informações antes de enviar", detalhe="Releia nomes, números e anexos. Peça a alguém de confiança para ler."))
    itens.append(dict(tipo=OFICIAL, texto="Acessar a página oficial e concluir a inscrição", detalhe="Use apenas o canal indicado na fonte oficial. Guarde o comprovante."))
    for i, it in enumerate(itens):
        it["id"] = i
    return itens


def progresso(oid: str, itens: list[dict], marcados: dict) -> tuple[int, int]:
    feitos = sum(1 for it in itens if marcados.get(f"chk:{oid}:{it['id']}"))
    return feitos, len(itens)
