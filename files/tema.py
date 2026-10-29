"""tema.py - identidade visual 'arte de rua' (lambe-lambe em parede de concreto).
Só aparência: nenhuma regra do app depende deste arquivo."""
import urllib.parse
from contextlib import contextmanager

import streamlit as st

# Ilustração do cabeçalho: lata de spray, respingos, estrela e coroa de grafite.
ARTE_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 420 220'>"
    "<g opacity='.92'><circle cx='70' cy='70' r='44' fill='#ff2e93'/><circle cx='115' cy='48' r='34' fill='#ff2e93'/>"
    "<circle cx='55' cy='125' r='30' fill='#ffe600'/><circle cx='120' cy='105' r='26' fill='#00bcd4'/><circle cx='165' cy='75' r='20' fill='#ff2e93'/></g>"
    "<g fill='#000'><circle cx='20' cy='30' r='4'/><circle cx='34' cy='170' r='3'/><circle cx='95' cy='170' r='5'/><circle cx='150' cy='150' r='3'/>"
    "<circle cx='178' cy='30' r='4'/><circle cx='15' cy='95' r='3'/><circle cx='200' cy='115' r='3'/></g>"
    "<g transform='rotate(-28 290 130)' stroke='#000' stroke-width='5' stroke-linejoin='round'>"
    "<rect x='255' y='72' width='70' height='128' rx='12' fill='#00bcd4'/><rect x='255' y='112' width='70' height='42' fill='#fff'/>"
    "<path d='M268 133 h44' stroke-width='6' stroke-linecap='round'/><rect x='265' y='44' width='50' height='30' rx='7' fill='#ffe600'/>"
    "<rect x='284' y='28' width='14' height='18' fill='#000'/></g>"
    "<polygon points='372,28 380,52 405,52 385,67 393,92 372,77 351,92 359,67 339,52 364,52' fill='#ffe600' stroke='#000' stroke-width='4' stroke-linejoin='round'/>"
    "<path d='M330 190 l14 -34 l16 22 l16 -28 l16 28 l16 -22 l14 34 z' fill='#ff2e93' stroke='#000' stroke-width='4' stroke-linejoin='round'/>"
    "<g fill='#000'><circle cx='344' cy='154' r='4'/><circle cx='376' cy='146' r='4'/><circle cx='408' cy='154' r='4'/></g></svg>"
)
ARTE_URI = "data:image/svg+xml," + urllib.parse.quote(ARTE_SVG, safe="/:=' ")

CARTAO = '[data-testid="stVerticalBlockBorderWrapper"]:has(.marca-cartao):not(:has([data-testid="stVerticalBlockBorderWrapper"] .marca-cartao))'

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Rubik:wght@500;600;700;800&family=Rubik+Spray+Paint&display=swap');
:root{--concreto:#c8cdd0;--cartaz:#fffefb;--tinta:#000;--magenta:#ff2e93;--amarelo:#ffe600;--ciano:#00bcd4;}
html{font-size:112.5%;}
.stApp{background-color:var(--concreto);background-image:radial-gradient(circle at 4% 6%,rgba(255,46,147,.40),transparent 18%),radial-gradient(circle at 96% 14%,rgba(0,188,212,.38),transparent 20%),radial-gradient(circle at 90% 88%,rgba(255,230,0,.45),transparent 22%),radial-gradient(circle at 6% 92%,rgba(0,188,212,.28),transparent 18%),radial-gradient(rgba(0,0,0,.07) 1px,transparent 1.5px),radial-gradient(rgba(255,255,255,.35) 1px,transparent 1.5px);background-size:auto,auto,auto,auto,17px 17px,29px 29px;background-attachment:fixed,fixed,fixed,fixed,scroll,scroll;color:var(--tinta);}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stMain"] .block-container,.block-container{max-width:100% !important;padding:1.2rem 2.2rem 3rem 2.2rem !important;}
p,li,label,a,input,textarea,button,summary,td,th,[data-testid="stMarkdownContainer"]{font-family:'Rubik',system-ui,-apple-system,'Segoe UI',Arial,sans-serif;}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{font-size:1.08rem;font-weight:600;line-height:1.55;color:#000;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,.stCaption{font-size:1rem !important;font-weight:600 !important;color:#1a1a1a !important;}
[data-testid="stWidgetLabel"] p,label p{font-size:1.08rem !important;font-weight:800 !important;color:#000 !important;}
[data-testid="stHeaderActionElements"]{display:none !important;}
h1,h2,h3,h4{font-family:'Anton',Impact,'Arial Narrow',sans-serif !important;font-weight:400 !important;letter-spacing:.015em;color:var(--tinta) !important;line-height:1.15 !important;}
h2{font-size:clamp(1.9rem,4.5vw,2.7rem) !important;}
h3{font-size:clamp(1.5rem,3.6vw,2.05rem) !important;}
h3::before{content:"★ ";color:var(--magenta);-webkit-text-stroke:1px var(--tinta);}
h2 span,h3 span,h2,h3{background:linear-gradient(transparent 60%,var(--amarelo) 60%);padding:0 .25em;-webkit-box-decoration-break:clone;box-decoration-break:clone;}
.hero{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.6rem 1.5rem;margin:0 0 .6rem 0;}
.hero .texto{flex:1 1 420px;min-width:0;}
.hero .logo{font-family:'Rubik Spray Paint','Anton',Impact,sans-serif !important;font-size:clamp(2.4rem,9vw,4.6rem);line-height:1.05;margin:0;padding:0;color:var(--magenta) !important;text-shadow:3px 3px 0 var(--tinta);background:none !important;display:block;}
.hero .logo span{color:var(--amarelo);-webkit-text-stroke:2px var(--tinta);}
.hero .lema{display:inline-block;margin:.7rem 0 0 0;padding:.35rem .8rem;background:var(--amarelo);border:3px solid var(--tinta);box-shadow:4px 4px 0 var(--tinta);transform:rotate(-1deg);font-weight:800;font-size:1.12rem;color:var(--tinta);}
.hero .arte{flex:0 1 380px;height:190px;background:url("__ARTE__") center/contain no-repeat;}
.faixa{background:var(--tinta);color:var(--amarelo);font-family:'Anton',Impact,sans-serif;font-size:1.25rem;letter-spacing:.08em;padding:.45rem 1rem;margin:.4rem -.4rem 1rem -.4rem;transform:rotate(-.5deg);border-top:3px solid var(--magenta);border-bottom:3px solid var(--magenta);text-align:center;line-height:1.5;}
.chamada{margin:.2rem 0 1rem 0;}
.chamada h2{display:inline;font-size:clamp(2.1rem,5.8vw,3.6rem) !important;line-height:1.25 !important;}
.chamada .pergunta{font-family:'Anton',Impact,sans-serif;font-size:clamp(1.4rem,3.4vw,2.1rem);margin:.5rem 0 0 0;color:var(--tinta);letter-spacing:.02em;}
.poster{background:var(--cartaz);border:3px solid var(--tinta);box-shadow:6px 6px 0 var(--tinta);padding:1rem 1.2rem;font-weight:700;font-size:1.1rem;line-height:1.6;}
.poster b{background:var(--amarelo);padding:0 .2em;}
__CARTAO__{position:relative;background:var(--cartaz);border:3px solid var(--tinta) !important;border-radius:4px !important;box-shadow:6px 6px 0 var(--tinta);padding:.35rem .6rem;}
__CARTAO__::before,[data-testid="stForm"]::before{content:"";position:absolute;top:-13px;left:22px;width:86px;height:24px;background:rgba(255,230,0,.88);border:1px solid rgba(0,0,0,.35);transform:rotate(-3deg);z-index:2;pointer-events:none;}
[data-testid="stElementContainer"]:has(.marca-cartao),[data-testid="element-container"]:has(.marca-cartao){display:none !important;}
[data-testid="stForm"]{position:relative;background:var(--cartaz);border:3px solid var(--tinta) !important;border-radius:4px;box-shadow:6px 6px 0 var(--tinta);padding:1.1rem !important;}
[role="tablist"],[data-baseweb="tab-list"]{flex-wrap:wrap !important;overflow:visible !important;height:auto !important;gap:10px;padding:6px 2px 14px 2px;border:none !important;}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none !important;}
button[role="tab"]{background:#fff !important;border:3px solid var(--tinta) !important;border-radius:6px !important;padding:.45rem 1rem !important;box-shadow:4px 4px 0 var(--tinta);height:auto !important;}
button[role="tab"] p{font-family:'Anton',Impact,sans-serif !important;font-size:1.3rem !important;font-weight:400 !important;letter-spacing:.03em;color:var(--tinta) !important;}
button[role="tab"][aria-selected="true"]{background:var(--amarelo) !important;transform:rotate(-1.2deg);}
button[role="tab"]:hover{background:var(--magenta) !important;}
[data-testid^="stBaseButton"],[data-testid^="stBaseLinkButton"],.stButton button,.stDownloadButton button,.stLinkButton a{background:#fff;color:var(--tinta) !important;border:3px solid var(--tinta) !important;border-radius:999px !important;box-shadow:4px 4px 0 var(--tinta);min-height:48px;padding:.4rem 1.2rem !important;}
[data-testid^="stBaseButton"] p,[data-testid^="stBaseLinkButton"] p,.stButton button p,.stDownloadButton button p,.stLinkButton a p{font-weight:800 !important;font-size:1.12rem !important;color:var(--tinta) !important;}
[data-testid^="stBaseButton"]:hover,[data-testid^="stBaseLinkButton"]:hover,.stButton button:hover,.stDownloadButton button:hover,.stLinkButton a:hover{background:var(--amarelo) !important;}
[data-testid^="stBaseButton"]:active,.stButton button:active{transform:translate(3px,3px);box-shadow:1px 1px 0 var(--tinta);}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"],button[kind="primary"],button[kind="primaryFormSubmit"]{background:var(--magenta) !important;}
[data-testid="stBaseButton-primary"]:hover,button[kind="primary"]:hover{background:var(--amarelo) !important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input{font-family:'Rubik',sans-serif !important;font-size:1.12rem !important;font-weight:700 !important;color:#000 !important;background:#fff !important;}
[data-testid="stSelectbox"] div,[data-testid="stMultiSelect"] div{font-size:1.08rem;font-weight:700;color:#000;}
[data-testid="stTextInput"] > div > div,[data-testid="stTextArea"] > div > div,[data-testid="stSelectbox"] > div > div,[data-testid="stMultiSelect"] > div > div{border:2px solid var(--tinta) !important;border-radius:4px !important;background:#fff !important;box-shadow:3px 3px 0 var(--tinta);}
[data-testid="stExpander"] details{background:#fff !important;border:3px solid var(--tinta) !important;border-radius:4px !important;box-shadow:4px 4px 0 var(--tinta);}
[data-testid="stExpander"] summary p{font-weight:800 !important;font-size:1.12rem !important;}
[data-testid="stAlert"]{background:#fffef0 !important;border:3px solid var(--tinta);border-radius:4px;box-shadow:4px 4px 0 var(--tinta);}
[data-testid="stAlert"] p{font-weight:700 !important;font-size:1.08rem !important;color:#000 !important;}
[data-testid="stCheckbox"] label p{font-weight:700 !important;font-size:1.1rem !important;}
[data-testid="stSidebar"]{background:#aeb4b8;border-right:4px solid var(--tinta);}
[data-testid="stSidebar"] *{color:var(--tinta);}
hr{border:0 !important;height:12px !important;background:repeating-linear-gradient(135deg,var(--tinta) 0 8px,var(--amarelo) 8px 16px) !important;margin:1.5rem 0 !important;}
*:focus-visible{outline:4px solid #0050ff !important;outline-offset:2px;}
@media (max-width:640px){html{font-size:106%;}.block-container{padding:.8rem .7rem 2rem .7rem !important;}.hero .arte{flex-basis:100%;height:120px;}__CARTAO__,[data-testid="stForm"]{box-shadow:4px 4px 0 var(--tinta);}button[role="tab"]{padding:.35rem .7rem !important;}button[role="tab"] p{font-size:1.1rem !important;}}
@media (prefers-reduced-motion:reduce){*{transition:none !important;animation:none !important;}button[role="tab"][aria-selected="true"],.hero .lema,.faixa{transform:none;}}
</style>""".replace("__ARTE__", ARTE_URI).replace("__CARTAO__", CARTAO)

AREAS_FAIXA = ["Música", "Artes visuais", "Ilustração", "Teatro e dança", "Artesanato", "Audiovisual", "Literatura", "Cultura popular"]

HERO = (
    '<div class="hero"><div class="texto"><h1 class="logo">ArteConecta<span> IA</span></h1>'
    '<p class="lema">Direitos, editais e oportunidades para quem faz arte na rua e fora dela.</p></div>'
    '<div class="arte" role="img" aria-label="Ilustração de uma lata de spray, respingos de tinta, estrela e coroa"></div></div>'
    '<div class="faixa">' + " ★ ".join(AREAS_FAIXA) + "</div>"
)

CHAMADA = '<div class="chamada"><h2>Seu talento merece uma oportunidade.</h2><p class="pergunta">Vamos encontrar o próximo passo?</p></div>'


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)


def cabecalho():
    st.markdown(HERO, unsafe_allow_html=True)


def chamada():
    st.markdown(CHAMADA, unsafe_allow_html=True)


def poster(html: str):
    st.markdown(f'<div class="poster">{html}</div>', unsafe_allow_html=True)


@contextmanager
def cartao():
    """Cartão 'cartaz colado'. A marca invisível permite ao CSS achar este cartão sem depender de nomes internos."""
    with st.container(border=True):
        st.markdown('<span class="marca-cartao"></span>', unsafe_allow_html=True)
        yield
