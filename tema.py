"""tema.py - identidade visual 'arte de rua' (lambe-lambe em parede de concreto).
Só aparência: nenhuma regra do app depende deste arquivo."""
import streamlit as st

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Rubik+Spray+Paint&display=swap');
:root{--concreto:#c8cdd0;--cartaz:#fffefb;--tinta:#000;--magenta:#ff2e93;--amarelo:#ffe600;}
.stApp{background-color:var(--concreto);background-image:radial-gradient(rgba(0,0,0,.07) 1px,transparent 1.5px),radial-gradient(rgba(255,255,255,.35) 1px,transparent 1.5px);background-size:17px 17px,29px 29px;background-position:0 0,7px 11px;color:var(--tinta);}
[data-testid="stHeader"]{background:transparent;}
h1,h2,h3,h4{font-family:'Anton',Impact,'Arial Narrow',sans-serif !important;font-weight:400 !important;letter-spacing:.01em;color:var(--tinta) !important;}
h2,h3{background:linear-gradient(transparent 62%,var(--amarelo) 62%);display:inline;padding:0 .2em;}
.hero{padding:.4rem 0 .2rem 0;margin-bottom:.4rem;}
.hero .logo{font-family:'Rubik Spray Paint','Anton',Impact,sans-serif !important;font-size:clamp(2.2rem,9.5vw,3.8rem);line-height:1.05;margin:0;padding:0;color:var(--magenta) !important;text-shadow:3px 3px 0 var(--tinta);background:none;display:block;}
.hero .logo span{color:var(--amarelo);-webkit-text-stroke:2px var(--tinta);text-shadow:3px 3px 0 var(--tinta);}
.hero .lema{display:inline-block;margin:.5rem 0 0 0;padding:.25rem .7rem;background:var(--amarelo);border:2px solid var(--tinta);box-shadow:3px 3px 0 var(--tinta);transform:rotate(-1deg);font-weight:600;font-size:.98rem;color:var(--tinta);}
[class*="st-key-card_"]{background:var(--cartaz);border:2px solid var(--tinta) !important;border-radius:4px !important;box-shadow:5px 5px 0 var(--tinta);}
[data-testid="stVerticalBlockBorderWrapper"]:has(> [class*="st-key-card_"]){border:none !important;background:transparent !important;box-shadow:none !important;}
.stTabs [data-baseweb="tab-list"]{gap:8px;padding:4px 2px 10px 2px;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}
.stTabs button[role="tab"]{background:#fff;border:2px solid var(--tinta);border-radius:6px;padding:.35rem .8rem;box-shadow:3px 3px 0 var(--tinta);}
.stTabs button[role="tab"] p{font-family:'Anton',Impact,sans-serif;font-size:1rem;letter-spacing:.02em;color:var(--tinta);}
.stTabs button[role="tab"][aria-selected="true"]{background:var(--amarelo);transform:rotate(-1deg);}
.stButton>button,.stDownloadButton>button,.stLinkButton>a,[data-testid="stFormSubmitButton"]>button{background:#fff;color:var(--tinta) !important;border:2px solid var(--tinta) !important;border-radius:999px !important;box-shadow:3px 3px 0 var(--tinta);min-height:44px;font-weight:700;}
.stButton>button:hover,.stDownloadButton>button:hover,.stLinkButton>a:hover,[data-testid="stFormSubmitButton"]>button:hover{background:var(--amarelo);color:var(--tinta) !important;}
.stButton>button:active,.stDownloadButton>button:active,[data-testid="stFormSubmitButton"]>button:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--tinta);}
button[kind="primary"],[data-testid="stBaseButton-primary"]{background:var(--magenta) !important;color:var(--tinta) !important;border:2px solid var(--tinta) !important;}
div[data-baseweb="input"],div[data-baseweb="textarea"],div[data-baseweb="select"]>div{border:2px solid var(--tinta) !important;border-radius:4px !important;background:#fff !important;}
[data-testid="stExpander"]{background:#fff;border:2px solid var(--tinta) !important;border-radius:4px !important;}
[data-testid="stAlert"]{border:2px solid var(--tinta);border-radius:4px;box-shadow:3px 3px 0 var(--tinta);}
[data-testid="stForm"]{background:var(--cartaz);border:2px solid var(--tinta) !important;border-radius:4px;box-shadow:5px 5px 0 var(--tinta);}
[data-testid="stSidebar"]{background:#aeb4b8;border-right:3px solid var(--tinta);}
[data-testid="stSidebar"] *{color:var(--tinta);}
[data-testid="stCaptionContainer"],.stCaption{color:#262626 !important;}
*:focus-visible{outline:3px solid #0050ff !important;outline-offset:2px;}
@media (max-width:640px){.block-container{padding:1rem .8rem !important;}[class*="st-key-card_"],[data-testid="stForm"]{box-shadow:3px 3px 0 var(--tinta);}.stTabs button[role="tab"]{padding:.3rem .6rem;}}
@media (prefers-reduced-motion:reduce){*{transition:none !important;animation:none !important;}.stButton>button:active{transform:none;}}
</style>"""

HERO = """<div class="hero"><h1 class="logo">ArteConecta<span> IA</span></h1><p class="lema">Direitos, editais e oportunidades para quem faz arte na rua e fora dela.</p></div>"""

_n = [0]


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)


def cabecalho():
    st.markdown(HERO, unsafe_allow_html=True)


def reiniciar_contagem():
    _n[0] = 0


def cartao():
    """Cartão 'cartaz colado'. A chave dá ao cartão uma classe CSS estável (precisa de Streamlit 1.39+)."""
    _n[0] += 1
    try:
        return st.container(border=True, key=f"card_{_n[0]}")
    except TypeError:
        return st.container(border=True)
