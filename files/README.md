# ArteConecta IA - Protótipo

Chatbot + busca de editais + guias educativos para artistas independentes.

## Estrutura
- `app.py` - interface (Streamlit)
- `motor.py` - busca nos documentos (RAG) + resposta com fonte
- `dados/base_conhecimento.json` - textos sobre direitos e oportunidades
- `dados/editais.csv` - editais (OS ATUAIS SÃO EXEMPLOS FICTÍCIOS)

## Rodar no seu computador
```
pip install -r requirements.txt
streamlit run app.py
```

## Publicar grátis (Streamlit Community Cloud)
1. Crie uma conta em github.com e um repositório público; suba estes arquivos.
2. Entre em share.streamlit.io, faça login com o GitHub e clique em "Create app".
3. Escolha o repositório e o arquivo `app.py`, e clique em Deploy.

## Ligar a IA generativa (opcional)
1. Crie conta em huggingface.co e gere um token de leitura (Settings > Access Tokens).
2. No Streamlit Cloud: App > Settings > Secrets, e escreva:
   `HF_TOKEN = "seu_token_aqui"`
3. Para trocar o modelo, defina a variável `MODELO_HF` (padrão: Qwen/Qwen2.5-7B-Instruct).
Sem token, o app funciona normalmente mostrando os trechos das fontes.

## Antes de apresentar
- Troque os editais de exemplo por editais REAIS da sua cidade (edite `dados/editais.csv`).
- Confira cada texto da base de conhecimento na fonte oficial.
- Adicione mais documentos ao `base_conhecimento.json` (titulo, fonte, texto).
