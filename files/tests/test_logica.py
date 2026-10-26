"""Testes da lógica (sem interface). Rodar: python tests/test_logica.py"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import comunidade as co
import oportunidades as op
import plano as pl
import portfolio as pf
import tradutor as tr

HOJE = date(2026, 10, 26)


def base(**k):
    o = dict(id="t", nome="t", tipo="Edital", area="Música", estado="SP", cidade="X", modalidade="Presencial", gratuito="Sim",
             remuneracao="Sim", nivel="Todos os níveis", elegibilidade="", documentos_lista=[], status_base="verificada",
             prazo=HOJE + timedelta(days=20), ultima_verificacao=HOJE - timedelta(days=5))
    o.update(k)
    o["estado_info"] = op.estado_info(o, HOJE); o["situacao_prazo"] = op.situacao_prazo(o, HOJE); o["disponibilidade"] = op.disponibilidade(o)
    return o


# estado da informação
assert base()["estado_info"] == "Verificada"
assert base(ultima_verificacao=HOJE - timedelta(days=90))["estado_info"] == "Desatualizada"
assert base(status_base="pendente")["estado_info"] == "Pendente de confirmação"
assert base(status_base="exemplo")["estado_info"] == "Exemplo fictício"
assert base(ultima_verificacao=None)["estado_info"] == "Pendente de confirmação"
# nunca afirma "aberta" sem verificação
assert "não é uma oportunidade real" in base(status_base="exemplo")["disponibilidade"].lower()
assert "não confirmada" in base(ultima_verificacao=HOJE - timedelta(days=90))["disponibilidade"].lower()
assert "provavelmente encerrada" in base(prazo=HOJE - timedelta(days=1))["disponibilidade"].lower()
assert base(prazo=None)["situacao_prazo"] == "Prazo não informado"

# filtros
L = [base(id="a"), base(id="b", area="Literatura"), base(id="c", prazo=HOJE - timedelta(days=2)), base(id="d", modalidade="Online", estado="RJ"), base(id="e", gratuito="Não")]
ids = lambda l: [o["id"] for o in l]
assert ids(op.filtrar(L, hoje=HOJE)) == ["a", "b", "d", "e"]          # encerrada escondida
assert "c" in ids(op.filtrar(L, so_abertas=False, hoje=HOJE))
assert ids(op.filtrar(L, area="Música", hoje=HOJE)) == ["a", "d", "e"]
assert ids(op.filtrar(L, estado="SP", hoje=HOJE)) == ["a", "b", "d", "e"]  # d é online
assert ids(op.filtrar(L, so_gratuitas=True, hoje=HOJE)) == ["a", "b", "d"]
assert ids(op.filtrar(L, prazo_max_dias=10, hoje=HOJE)) == []

# compatibilidade explica e lista o que conferir
c = op.compatibilidade(base(elegibilidade="Residentes"), dict(area="Música", estado="SP", cidade="x", nivel="Iniciante", tipos=["Edital"]), HOJE)
assert c["nivel"] == "Alta" and c["motivos"] and any("Residentes" in x for x in c["conferir"])
c2 = op.compatibilidade(base(area="Literatura", estado="RJ"), dict(area="Música", estado="SP", nivel="Iniciante"), HOJE)
assert c2["nivel"] == "Baixa" and len(c2["conferir"]) >= 2

# dados reais do projeto
dados = op.carregar(HOJE)
assert all(o["estado_info"] == "Exemplo fictício" and o["nome"].startswith("EXEMPLO") for o in dados), "dados fictícios devem estar identificados"
assert any(o["situacao_prazo"] == "Encerrada" for o in dados) and any(o["situacao_prazo"] == "Prazo não informado" for o in dados)

# plano: cada tarefa tem justificativa e muda com o perfil
a = pl.gerar_plano(dict(area="Música", nivel="Iniciante", dificuldades=["Não tenho portfólio"]))
b = pl.gerar_plano(dict(area="Artesanato", nivel="Experiente", dificuldades=["Não sei quanto cobrar"], objetivo="Ter renda com a minha arte"))
assert all(t["porque"] and t["descricao"] for t in a + b) and [t["id"] for t in a] != [t["id"] for t in b]

# tradutor: não inventa
r = tr.analisar(open(Path(__file__).parent.parent / "dados" / "edital_exemplo.txt", encoding="utf-8").read())
assert {d["data"] for d in r["datas"]} >= {"30/11/2026", "15/12/2026"} and any(v == "R$ 5.000,00" for v, _ in r["valores"])
assert tr.perguntar(r["trechos"], "qual a cor do céu em Marte")[1] == []
assert tr.analisar("Texto qualquer sem nada de edital " * 5)["datas"] == []
assert tr.dividir_em_trechos("Prazo final sem pontuação no fim")  # trecho curto não pode sumir
assert tr.analisar("Inscrições até 32/13/2026.")["datas"] == []

# portfólio: escapa HTML e avisa invenção
assert "<script>" not in pf.gerar_html(dict(nome="<script>x</script>", area="Música"), "oi", "bio")
assert pf._invencoes("Ana ganhou 3 prêmios.", "Ana canta.") == ["3"]

# comunidade: bloqueio, privacidade e recomendação sem popularidade
assert "Exemplo_A" not in [p["autor"] for p in co.filtrar(co.EXEMPLOS, bloqueados=["Exemplo_A"])]
assert co.alertas_privacidade("a@b.com") and co.alertas_privacidade("faça um pix para reservar a vaga")
assert not co.alertas_privacidade("Procuro violonista para projeto de samba")
print("OK: todos os testes de lógica passaram")
