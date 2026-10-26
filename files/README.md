# ArteConecta IA - protótipo v2

Plataforma para artistas independentes: do "não sei por onde começar" até a candidatura preparada.

## Abas
| Aba | O que faz | Precisa de IA? |
|---|---|---|
| 🏠 Início | Perfil, próximo passo, oportunidades compatíveis, candidaturas, sugestões de colaboração | Não |
| 🧭 Primeiro passo | Plano de tarefas por regras, com justificativa ligada às respostas do perfil | Não |
| 📡 Radar | Filtros, estado da informação, compatibilidade explicada e checklist "Caminho até a oportunidade" | Não |
| 📄 Tradutor | Edital colado/PDF → trechos por tema com página, datas, valores, tarefas e perguntas ao documento | Opcional (resumo simples) |
| 🖼️ Portfólio | Formulário → apresentação e biografia editáveis → HTML para baixar (imprimir como PDF) | Opcional (reescrita) |
| 📚 Aprender | 17 guias por tema e nível, com tipo de fonte | Não |
| 💬 Pergunte | Busca nos guias, sempre com fonte | Opcional |
| 🤝 Comunidade | Pedidos de colaboração, filtros, denúncia, bloqueio, dicas contra golpe | Não |

## Arquivos
- `app.py` interface | `motor.py` busca nos guias | `oportunidades.py` filtros, datas e compatibilidade
- `plano.py` primeiro passo | `caminho.py` checklist | `tradutor.py` editais | `portfolio.py` portfólio
- `comunidade.py` | `estado.py` salvar/continuar | `ia.py` único ponto de contato com IA externa
- `dados/` oportunidades.csv (FICTÍCIAS), base_conhecimento.json, edital_exemplo.txt
- `tests/test_logica.py` testes da lógica

## Rodar
```
pip install -r requirements.txt
streamlit run app.py
python tests/test_logica.py
```

## IA opcional (Hugging Face)
1. Gere um token de leitura em huggingface.co (Settings > Access Tokens).
2. Streamlit Cloud: App > Settings > Secrets: `HF_TOKEN = "hf_..."` (nunca coloque o token no código ou no GitHub).
3. No app, marque "Permitir IA externa" na barra lateral. Sem essa autorização, nenhum texto é enviado.
4. Modelo padrão: `Qwen/Qwen2.5-7B-Instruct` (troque com a variável `MODELO_HF`). Confira licença e limites de uso do modelo e do plano gratuito.

## Como usar oportunidades REAIS
Edite `dados/oportunidades.csv` (uma linha por oportunidade). Campos importantes:
- `status_base`: `verificada` (você conferiu na fonte), `pendente` ou `exemplo`.
- `ultima_verificacao`: data (AAAA-MM-DD) em que você conferiu. Passados 30 dias, o app marca como "Desatualizada".
- `documentos`: separe por `;`. `link` e `fonte`: use só o endereço oficial.
Nunca marque `verificada` sem abrir a fonte.

## Limitações atuais
- Oportunidades são exemplos fictícios. Não há coleta automática.
- Sem banco de dados e sem contas: o progresso só persiste se o usuário baixar o arquivo (botão na barra lateral). A comunidade existe só na sessão de cada pessoa.
- Sem mapa de espaços culturais (Etapa 3).
- Tradutor: busca por palavras, não por significado. Pode errar em editais com redação muito diferente. PDFs escaneados não são lidos.
- Portfólio: exporta HTML; PDF via impressão do navegador; sem link público.
- Compatibilidade e plano são regras simples, não IA.
