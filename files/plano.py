"""plano.py - 'Meu primeiro passo': plano de ação por REGRAS (sem IA).
Cada tarefa só aparece se uma resposta do perfil a justifica, e diz qual foi."""

OBJETIVOS = ["Fazer minha primeira apresentação ou exposição", "Ter renda com a minha arte",
             "Participar de editais e prêmios", "Aprender e me profissionalizar",
             "Encontrar parceiros para projetos", "Divulgar meu trabalho"]
DIFICULDADES = ["Não tenho portfólio", "Não sei onde achar oportunidades",
                "Tenho dificuldade com editais", "Não sei quanto cobrar",
                "Falta de contatos e parcerias", "Não sei divulgar meu trabalho",
                "Dúvidas sobre direitos autorais", "Não sei se devo formalizar (MEI)"]

ESPECIFICAS = {
    "Música": [("repertorio", "Organizar um repertório curto", "Escolha de 5 a 8 músicas que você domina e que mostram seu estilo. Anote duração e tom de cada uma.", "Aba 🖼️ Portfólio (para registrar)"),
               ("audio", "Gravar um vídeo ou áudio curto de apresentação", "Um registro de 2 a 3 minutos com o celular, em local silencioso, já serve para portfólios e editais.", "Aba 🖼️ Portfólio")],
    "Artes visuais": [("fotografar", "Fotografar suas obras com boa luz", "Fotografe de frente, com luz natural, e anote título, técnica, tamanho e ano de cada obra.", "Aba 🖼️ Portfólio")],
    "Ilustração": [("fotografar", "Reunir e organizar suas ilustrações", "Salve em boa resolução 5 a 10 trabalhos e anote o projeto ou a finalidade de cada um.", "Aba 🖼️ Portfólio")],
    "Teatro e dança": [("video_cena", "Gravar um vídeo curto de uma cena ou coreografia", "Um registro de 1 a 3 minutos, com enquadramento do corpo inteiro e som claro.", "Aba 🖼️ Portfólio")],
    "Artesanato": [("produtos", "Fotografar seus produtos e anotar o custo de cada um", "Anote material, tempo e custo. Isso ajuda a definir preço e a preencher inscrições em feiras.", "Aba 📚 Aprender (Organização financeira)")],
    "Audiovisual e fotografia": [("showreel", "Selecionar seus melhores trabalhos", "Escolha de 3 a 5 projetos que mostrem seu olhar e liste sua função em cada um.", "Aba 🖼️ Portfólio")],
    "Literatura": [("textos", "Organizar seus textos", "Reúna os textos em uma pasta, escolha os melhores e separe um trecho de cerca de uma página para apresentar.", "Aba 🖼️ Portfólio")],
    "Cultura popular e artes de rua": [("regras_rua", "Conferir as regras de apresentação em espaço público", "Pergunte à Secretaria de Cultura da sua cidade se existe cadastro ou autorização para artistas de rua.", "Aba 📚 Aprender (Apresentações públicas)"),
                                       ("registro_rua", "Registrar suas apresentações", "Peça a alguém para filmar um trecho. Esses registros servem como comprovação de atuação em editais.", "Aba 🖼️ Portfólio")],
}


def _dif(p, d):
    return d in (p.get("dificuldades") or [])


def _obj(p, o):
    return p.get("objetivo") == o


def gerar_plano(p: dict, limite: int = 8) -> list[dict]:
    """Devolve tarefas ordenadas; cada uma traz 'porque' ligado às respostas do usuário."""
    t = []

    def add(prio, id, titulo, desc, porque, onde):
        t.append(dict(id=id, prio=prio, titulo=titulo, descricao=desc, porque=porque, onde=onde))

    area = p.get("area", "sua área")
    if _dif(p, "Não tenho portfólio") or p.get("nivel") == "Iniciante":
        motivo = "Você marcou que não tem portfólio." if _dif(p, "Não tenho portfólio") else "Você está começando, e o portfólio é a base de quase tudo."
        add(1, "portfolio", "Montar um portfólio simples com 3 a 5 trabalhos",
            "Escolha os trabalhos que melhor representam você e junte foto, vídeo ou link de cada um.",
            motivo, "Aba 🖼️ Portfólio")
    for (tid, titulo, desc, onde) in ESPECIFICAS.get(area, []):
        add(2, tid, titulo, desc, f"Sugestão para quem atua em {area}.", onde)
    if p.get("tipos") and "Edital" in p["tipos"] or _obj(p, "Participar de editais e prêmios") or _dif(p, "Não sei onde achar oportunidades"):
        add(3, "documentos", "Separar seus documentos pessoais em uma pasta",
            "Digitalize RG, CPF e comprovante de residência. Quase todo edital pede esses documentos.",
            "Você quer participar de editais ou oportunidades, e a documentação é uma etapa comum.", "Pasta no seu celular ou computador")
    add(4, "radar", f"Ver as oportunidades compatíveis com {area}",
        "Abra o Radar, filtre pela sua área e região e leia os motivos de compatibilidade.",
        "Você precisa saber o que existe para se planejar.", "Aba 📡 Radar")
    if _dif(p, "Tenho dificuldade com editais"):
        add(3, "tradutor", "Usar o Tradutor para entender um edital",
            "Cole o texto de um edital e veja o resumo, os documentos e os prazos, com a página de onde cada trecho saiu.",
            "Você marcou dificuldade com editais.", "Aba 📄 Tradutor")
    if _dif(p, "Não sei quanto cobrar") or _obj(p, "Ter renda com a minha arte"):
        add(4, "cache", "Estimar quanto cobrar por um trabalho",
            "Some seus custos reais, pesquise valores na sua região e anote uma faixa de preço.",
            "Você quer renda ou marcou dúvida sobre preços.", "Aba 📚 Aprender (Negociação e cachê)")
    if _dif(p, "Não sei se devo formalizar (MEI)") or _obj(p, "Ter renda com a minha arte"):
        add(5, "mei", "Entender se o MEI faz sentido para você",
            "Leia o guia sobre MEI e confira no Portal do Empreendedor se a sua atividade está na lista.",
            "Você quer renda ou tem dúvida sobre formalização.", "Aba 📚 Aprender (Formalização e MEI)")
    if _dif(p, "Dúvidas sobre direitos autorais") or area in ("Música", "Literatura", "Audiovisual e fotografia", "Ilustração", "Artes visuais"):
        add(5, "autoral", "Entender como proteger e usar obras",
            "Leia os guias de direitos autorais e guarde datas e versões dos seus trabalhos.",
            "Sua área produz obras autorais, ou você marcou dúvidas sobre o tema.", "Aba 📚 Aprender (Direitos autorais)")
    if _dif(p, "Não sei divulgar meu trabalho") or _obj(p, "Divulgar meu trabalho"):
        add(4, "divulgacao", "Criar ou organizar seu perfil profissional online",
            "Use foto, descrição curta, contato e 3 publicações do seu trabalho.",
            "Você quer divulgar seu trabalho.", "Aba 📚 Aprender (Divulgação)")
    if _dif(p, "Falta de contatos e parcerias") or _obj(p, "Encontrar parceiros para projetos"):
        add(4, "parceiros", "Procurar parceiros de projeto",
            "Veja os pedidos de colaboração e publique o que você procura.",
            "Você quer parcerias ou marcou falta de contatos.", "Aba 🤝 Comunidade")
    if _obj(p, "Fazer minha primeira apresentação ou exposição"):
        add(3, "espacos", "Listar 5 lugares da sua cidade que recebem apresentações",
            "Pense em centros culturais, bibliotecas, escolas, praças e feiras. Anote como cada um recebe propostas.",
            "Seu objetivo é fazer a primeira apresentação ou exposição.", "Caderno ou celular")
    vistos, unico = set(), []
    for x in sorted(t, key=lambda x: x["prio"]):
        if x["id"] not in vistos:
            vistos.add(x["id"]); unico.append(x)
    return unico[:limite]
