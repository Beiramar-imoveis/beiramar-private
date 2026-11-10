#!/usr/bin/env python3
"""Gera as páginas do site da Beiramar Private, em português e em inglês.

Uso (na pasta do projeto):
    python3 ferramentas/gerar_site.py

Fontes de conteúdo:
    dados/empreendimentos.json   textos em português (fonte principal)
    dados/traducoes-en.json      textos em inglês dos empreendimentos e regiões
    dados/blog/, dados/privacidade*.html

O script recria todas as páginas HTML nas duas línguas (a versão em inglês fica em /en/),
os redirecionamentos dos endereços antigos do WordPress, o sitemap.xml e o robots.txt.
Não precisa instalar nada além do Python 3.

Todos os links internos são relativos, então o site funciona tanto no domínio
próprio quanto na prévia do GitHub Pages (usuario.github.io/beiramar-private/).
"""
import copy
import json
import shutil
from html import escape
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DADOS = json.loads((RAIZ / "dados" / "empreendimentos.json").read_text(encoding="utf-8"))
TRAD = json.loads((RAIZ / "dados" / "traducoes-en.json").read_text(encoding="utf-8"))

DOMINIO = "https://beiramarprivate.com.br"
WHATS_NUM = "556131426671"
WHATS_TXT = "(61) 3142-6671"
WHATS_TXT_INTL = "+55 61 3142-6671"
INSTAGRAM = "https://www.instagram.com/beiramarprivate/"
LINKEDIN = "https://www.linkedin.com/company/beiramarimoveis/"
FACEBOOK = "https://www.facebook.com/BeiramarImoveis"
GRUPO = "https://grupobeiramar.com.br/"
BEIRAMAR_IMOVEIS = "https://www.beiramarimoveis.com.br/"
# Formulário: Web3Forms (mesmo serviço do site do Grupo). A chave define o e-mail que recebe os contatos.
WEB3FORMS_KEY = "3d4ebba9-bbea-4efb-b910-c1501ea4f2af"
ANO = "2026"

EMPS_PT = [x for x in DADOS["empreendimentos"] if x.get("ativo", True)]
REG_PT = {r["slug"]: r for r in DADOS["regioes"]}

LANG = "pt"          # idioma da página em geração


def versao(rel):
    """Código curto do conteúdo do arquivo, para o navegador baixar a versão nova a cada mudança."""
    import hashlib
    return hashlib.md5((RAIZ / rel).read_bytes()).hexdigest()[:8]
geradas = []         # caminhos para o sitemap


# ---------------------------------------------------------------- idioma
def en():
    return LANG == "en"


def t(pt, ingles):
    return ingles if en() else pt


def regioes():
    """Regiões no idioma atual."""
    if not en():
        return REG_PT
    out = {}
    for slug, r in REG_PT.items():
        x = copy.deepcopy(r)
        x.update(TRAD["regioes"].get(slug, {}))
        out[slug] = x
    return out


def emps():
    """Empreendimentos no idioma atual."""
    if not en():
        return EMPS_PT
    out = []
    for x in EMPS_PT:
        y = copy.deepcopy(x)
        y.update(TRAD["empreendimentos"].get(x["slug"], {}))
        y["status"] = TRAD["status"].get(x.get("status", ""), x.get("status", ""))
        y["assinaturas"] = [[TRAD["rotulos_assinatura"].get(k, k), v] for k, v in x.get("assinaturas", [])]
        out.append(y)
    return out


def numeros_dados():
    n = copy.deepcopy(DADOS["numeros_noroeste"])
    if en():
        n.update(TRAD["numeros_noroeste"])
    return n


def prefixo(lang=None):
    return "en/" if (lang or LANG) == "en" else ""


# rotas que mudam de nome entre os idiomas
ROTAS = {"obrigado": {"pt": "obrigado/", "en": "thank-you/"},
         "privacidade": {"pt": "privacidade/", "en": "privacy/"}}


def rota(chave, lang=None):
    lang = lang or LANG
    return ROTAS[chave][lang] if chave in ROTAS else chave


# ---------------------------------------------------------------- utilidades
def e(txt):
    return escape(str(txt), quote=True)


def wa(msg=None):
    msg = msg or t("Olá! Quero falar com um especialista Beiramar Private.",
                   "Hello! I would like to talk to a Beiramar Private specialist.")
    return f"https://wa.me/{WHATS_NUM}?text={quote(msg)}"


def seta():
    return ('<svg class="seta" viewBox="0 0 64 12" aria-hidden="true">'
            '<path d="M0 6h62M57 1l5 5-5 5"/></svg>')


def assinatura(r, preta=False, classe=""):
    """Logo original da Beiramar Private (arquivos oficiais, sem alterações).
    Versão branca sobre o Preto Private; versão preta sobre o Branco Private."""
    arq = "logo-beiramar-private-preta.png" if preta else "logo-beiramar-private.png"
    return (f'<img class="assinatura {classe}" src="{r}imagens/site/{arq}" '
            f'alt="Beiramar Private" width="716" height="428">')


ICONES = {
    "whats": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.69.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.04 21.8h-.01a9.8 9.8 0 0 1-5-1.37l-.36-.21-3.72.98 1-3.63-.24-.37a9.8 9.8 0 0 1-1.5-5.22c0-5.42 4.41-9.83 9.84-9.83a9.77 9.77 0 0 1 6.95 2.88 9.77 9.77 0 0 1 2.88 6.95c0 5.43-4.41 9.83-9.84 9.83zm8.37-18.2A11.75 11.75 0 0 0 12.04.13C5.5.13.18 5.45.18 11.99c0 2.09.55 4.13 1.59 5.93L.08 24l6.23-1.63a11.82 11.82 0 0 0 5.72 1.46h.01c6.54 0 11.86-5.32 11.86-11.86 0-3.17-1.23-6.15-3.47-8.39z"/></svg>',
    "insta": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.72 3.72 0 0 1-1.38-.9 3.72 3.72 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.13 1.38A5.9 5.9 0 0 0 .63 4.14C.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.3.79.72 1.46 1.38 2.13a5.9 5.9 0 0 0 2.13 1.38c.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56a5.9 5.9 0 0 0 2.13-1.38 5.9 5.9 0 0 0 1.38-2.13c.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91a5.9 5.9 0 0 0-1.38-2.13A5.9 5.9 0 0 0 19.86.63C19.1.33 18.22.13 16.95.07 15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.62 23.1 24 18.1 24 12.07"/></svg>',
}
MENU_ICONE = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>')


def img_emp(slug, nome="capa", p=False):
    return f"imagens/empreendimentos/{slug}/{nome}{'-p' if p else ''}.webp"


def img_site(nome, p=False):
    return f"imagens/site/{nome}{'-p' if p else ''}.webp"


def foto_faixas(src_rel, src_p_rel, alt, classe="", sizes="(max-width: 820px) 100vw, 68vw", eager=False):
    """Foto com o degradê em faixas (grafismo 2)."""
    carrega = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="faixas {classe}"><img src="{src_rel}" srcset="{src_p_rel} 760w, {src_rel} 1600w" '
            f'sizes="{sizes}" alt="{e(alt)}" {carrega} decoding="async"></div>')


def sem_em(txt):
    return txt.replace("<em>", "").replace("</em>", "")


# ---------------------------------------------------------------- blocos comuns
def head(r, titulo, descricao, caminho, par=None, imagem_og="compartilhamento.jpg", noindex=False, canonical=None, extra=""):
    """par = (caminho_pt, caminho_en) para os links de idioma (hreflang)."""
    url = f"{DOMINIO}/{caminho}"
    can = canonical or url
    og_img = imagem_og if imagem_og.startswith("http") else f"{DOMINIO}/{imagem_og}"
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    alternos = ""
    if par and par[0] is not None and par[1] is not None:
        alternos = (f'<link rel="alternate" hreflang="pt-BR" href="{DOMINIO}/{par[0]}">\n'
                    f'<link rel="alternate" hreflang="en" href="{DOMINIO}/{par[1]}">\n'
                    f'<link rel="alternate" hreflang="x-default" href="{DOMINIO}/{par[0]}">')
    return f"""<!DOCTYPE html>
<html lang="{t('pt-BR', 'en')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{e(can)}">
{alternos}
{robots}
<meta name="theme-color" content="#131415">
<script>document.documentElement.classList.add("js")</script>
<link rel="icon" type="image/png" sizes="64x64" href="{r}favicon.png">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="{t('pt_BR', 'en_US')}">
<meta property="og:site_name" content="Beiramar Private">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">
<link rel="preload" href="{r}fontes/didot-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}css/consentimento.css?v={versao("css/consentimento.css")}">
<link rel="stylesheet" href="{r}css/private.css?v={versao("css/private.css")}">
{extra}
</head>
<body>
"""


def idioma_link(r, par):
    """Troca de idioma: botão redondo no desktop e "PT · EN" no menu do celular (modelo BRM Asset)."""
    pt_href = r + (par[0] if par and par[0] is not None else "")
    en_href = r + (par[1] if par and par[1] is not None else "en/")
    if en():
        botao = (f'<a href="{pt_href}" class="nav-idioma" hreflang="pt-BR" lang="pt-BR" aria-label="Ver em português">PT</a>')
        lista = (f'<a href="{pt_href}" hreflang="pt-BR" lang="pt-BR" aria-label="Ver em português">PT</a>'
                 f'<span class="nav-idiomas__sep" aria-hidden="true">·</span>'
                 f'<span class="nav-idiomas__atual" aria-current="true">EN</span>')
    else:
        botao = (f'<a href="{en_href}" class="nav-idioma" hreflang="en" lang="en" aria-label="View in English">EN</a>')
        lista = (f'<span class="nav-idiomas__atual" aria-current="true">PT</span>'
                 f'<span class="nav-idiomas__sep" aria-hidden="true">·</span>'
                 f'<a href="{en_href}" hreflang="en" lang="en" aria-label="View in English">EN</a>')
    return botao, f'<div class="nav-idiomas" role="group" aria-label="{t("Idioma", "Language")}">{lista}</div>'


def topo(r, b, par, atual="", lp=False, eco_local=True):
    """Cabeçalho. r = caminho até a raiz (arquivos); b = raiz do idioma (links)."""
    cta = f'<a href="#contato" class="nav-cta">{t("Falar com um especialista", "Talk to a specialist")}</a>'
    if lp:
        _, lista = idioma_link(r, par)
        nav = f'<nav class="nav" id="nav" aria-label="{t("Principal", "Main")}">{lista}{cta}</nav>'
    else:
        itens = [("noroeste", f"{b}noroeste/", "Noroeste"), ("quadra-500", f"{b}quadra-500/", "Quadra 500"),
                 ("empreendimentos", f"{b}#empreendimentos", t("Empreendimentos", "Properties")),
                 ("private", f"{b}#sobre", t("A Private", "About")),
                 ("grupo", "#ecossistema" if eco_local else f"{b}#ecossistema", "Grupo Beiramar")]
        links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == atual else ""}>{tx}</a>' for k, h, tx in itens)
        botao, lista = idioma_link(r, par)
        nav = f'<nav class="nav" id="nav" aria-label="{t("Principal", "Main")}">{links}{lista}{cta}</nav>'
    toggle = "" if lp else (f'<button class="nav-toggle" type="button" aria-controls="nav" aria-expanded="false" '
                            f'aria-label="{t("Abrir menu", "Open menu")}">{MENU_ICONE}</button>')
    classe_lp = " topo--lp" if lp else ""
    return f"""<header class="topo{classe_lp}" id="topo">
  <div class="wrap">
    <a href="{b}" class="marca" aria-label="Beiramar Private — {t('início', 'home')}">{assinatura(r, classe='logo-branca')}{assinatura(r, preta=True, classe='logo-preta')}</a>
    {nav}
    {toggle}
  </div>
</header>
"""


def rodape(r, b):
    lista = emps()
    noroeste = "".join(f'<li><a href="{b}empreendimentos/{x["slug"]}/">{e(x["nome"])}</a></li>' for x in lista if x["regiao"] == "noroeste")
    q500 = "".join(f'<li><a href="{b}empreendimentos/{x["slug"]}/">{e(x["nome"])}</a></li>' for x in lista if x["regiao"] == "quadra-500")
    blog = "" if en() else f'<li><a href="{b}blog/">Blog</a></li>'
    return f"""<footer class="rodape">
  <div class="wrap">
    <div class="rodape__topo">
      <div>
        <a href="{b}" aria-label="Beiramar Private — {t('início', 'home')}">{assinatura(r)}</a>
        <p class="rodape__frase">{t('A frente de alto padrão da <em>Beiramar</em> no Plano Piloto.', 'The luxury division of <em>Beiramar</em> in Brasília’s Plano Piloto.')}</p>
      </div>
      <div><h4>Noroeste</h4><ul>{noroeste}</ul></div>
      <div><h4>Quadra 500</h4><ul>{q500}</ul></div>
      <div>
        <h4>{t('Contato', 'Contact')}</h4>
        <ul>
          <li><a href="{wa()}" target="_blank" rel="noopener">WhatsApp {t(WHATS_TXT, WHATS_TXT_INTL)}</a></li>
          {blog}
          <li><a href="{BEIRAMAR_IMOVEIS}" target="_blank" rel="noopener">Beiramar Imóveis</a></li>
          <li><a href="{GRUPO}" target="_blank" rel="noopener">Grupo Beiramar</a></li>
        </ul>
        <div class="redes" style="margin-top:22px">
          <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram Beiramar Private">{ICONES['insta']}</a>
          <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn Beiramar">{ICONES['linkedin']}</a>
          <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook Beiramar">{ICONES['facebook']}</a>
        </div>
      </div>
    </div>
    <div class="rodape__base">
      <span>© {ANO} Beiramar Private · {t('uma frente da Beiramar Imóveis, empresa do Grupo Beiramar.', 'a division of Beiramar Imóveis, a Grupo Beiramar company.')}</span>
      <nav aria-label="{t('Links legais', 'Legal')}"><a href="{b}{rota('privacidade')}">{t('Privacidade e cookies', 'Privacy and cookies')}</a><button type="button" class="gb-cookie-prefs-link" data-cookie-preferences>{t('Preferências de cookies', 'Cookie preferences')}</button></nav>
    </div>
  </div>
</footer>
<a class="whats" href="{wa()}" target="_blank" rel="noopener" aria-label="{t('Falar pelo WhatsApp', 'Chat on WhatsApp')}">{ICONES['whats']}</a>
<script src="{r}js/private.js?v={versao("js/private.js")}" defer></script>
<script src="{r}js/consentimento.js?v={versao("js/consentimento.js")}" defer></script>
</body>
</html>
"""


def card(r, b, x, revelar=True):
    reg = regioes()[x["regiao"]]
    selo = f'<span class="selo">{e(x["status"])}</span>' if x.get("status") else ""
    rev = " revelar" if revelar else ""
    return f"""<article class="card{rev}" data-regiao="{x['regiao']}">
  <div class="card__midia">{selo}<img src="{r}{img_emp(x['slug'], p=True)}" alt="{e(x['nome'])}, {e(reg['rotulo'])}" loading="lazy" decoding="async" draggable="false"></div>
  <div class="card__corpo">
    <span class="card__regiao">{e(reg['nome'])}</span>
    <h3 class="card__nome"><a class="card__link" href="{b}empreendimentos/{x['slug']}/">{e(x['nome'])}</a></h3>
    <p class="card__chamada">{x['chamada']}</p>
    <div class="card__dados"><div><span>{t('Metragem', 'Size')}</span>{e(x['metragem'])}</div><div><span>{t('Dormitórios', 'Bedrooms')}</span>{e(x['dormitorios'])}</div></div>
    <div class="card__mais">{t('Conhecer', 'Discover')} {seta()}</div>
  </div>
</article>"""


def opcoes_interesse(selecionado=""):
    out = ['<option value="" disabled' + ("" if selecionado else " selected") + f'>{t("Selecione", "Select")}</option>']
    for slug, reg in regioes().items():
        out.append(f'<optgroup label="{e(reg["nome"])}">')
        for x in EMPS_PT:
            if x["regiao"] == slug:
                sel = " selected" if x["nome"] == selecionado else ""
                out.append(f'<option{sel}>{e(x["nome"])}</option>')
        out.append("</optgroup>")
    out.append(f'<option>{t("Quero uma indicação da curadoria", "I would like a curated recommendation")}</option>')
    return "".join(out)


def contato(r, b, titulo=None, texto=None, interesse="", origem="Site", claro=False):
    titulo = titulo or t('Vamos encontrar o seu <em>próximo endereço</em>.', 'Let’s find your <em>next address</em>.')
    texto = texto or t("Conte o que você procura. Um especialista Private retorna com opções selecionadas "
                       "para o seu perfil, com discrição e sem compromisso.",
                       "Tell us what you are looking for. A Private specialist will get back to you with options "
                       "selected for your profile, discreetly and with no obligation.")
    tema = " tema-claro" if claro else ""
    if en():
        quartos = ('<option value="">Any</option><option>Studio or 1 bedroom</option><option>2 bedrooms</option>'
                   '<option>3 bedrooms or suites</option><option>4 suites</option><option>Penthouse</option>')
        tel = ('<input id="f-whats" name="whatsapp" type="tel" inputmode="tel" autocomplete="tel" '
               'placeholder="+1 555 123 4567" minlength="8" required>')
    else:
        quartos = ('<option value="">Indiferente</option><option>Studio ou 1 quarto</option><option>2 quartos</option>'
                   '<option>3 quartos ou suítes</option><option>4 suítes</option><option>Cobertura</option>')
        tel = ('<input id="f-whats" name="whatsapp" type="tel" inputmode="tel" autocomplete="tel" '
               'placeholder="(61) 99999-9999" minlength="14" data-mascara="br" required>')
    return f"""<section class="secao{tema}" id="contato">
  <div class="wrap contato">
    <div class="revelar">
      <span class="rotulo rotulo--linha">{t('Atendimento Private', 'Private service')}</span>
      <h2 class="titulo">{titulo}</h2>
      <p class="lead">{texto}</p>
      <div class="contato__canais">
        <a href="{wa()}" target="_blank" rel="noopener"><span><small>WhatsApp</small>{t(WHATS_TXT, WHATS_TXT_INTL)}</span>{seta()}</a>
        <a href="{INSTAGRAM}" target="_blank" rel="noopener"><span><small>Instagram</small>@beiramarprivate</span>{seta()}</a>
      </div>
    </div>
    <form class="form revelar" action="https://api.web3forms.com/submit" method="POST" data-lead data-obrigado="{b}{rota('obrigado')}">
      <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
      <input type="hidden" name="from_name" value="Site Beiramar Private">
      <input type="hidden" name="idioma" value="{t('Português', 'Inglês')}">
      <input type="hidden" name="origem" value="{e(origem)}">
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="campo campo--inteiro"><label for="f-nome">{t('Nome', 'Name')}</label><input id="f-nome" name="nome" type="text" autocomplete="name" placeholder="{t('Como podemos te chamar?', 'Your name')}" required></div>
      <div class="campo"><label for="f-whats">{t('WhatsApp', 'WhatsApp / phone')}</label>{tel}</div>
      <div class="campo"><label for="f-email">E-mail</label><input id="f-email" name="email" type="email" autocomplete="email" placeholder="{t('seu@email.com', 'you@email.com')}" required></div>
      <div class="campo"><label for="f-interesse">{t('Interesse', 'Interest')}</label><select id="f-interesse" name="interesse" required>{opcoes_interesse(interesse)}</select></div>
      <div class="campo"><label for="f-quartos">{t('Dormitórios', 'Bedrooms')}</label><select id="f-quartos" name="quartos">{quartos}</select></div>
      <div class="campo campo--inteiro"><label for="f-msg">{t('Mensagem', 'Message')} <span style="opacity:.6">({t('opcional', 'optional')})</span></label><textarea id="f-msg" name="mensagem" rows="3" placeholder="{t('Conte rapidamente o que você procura.', 'Briefly tell us what you are looking for.')}"></textarea></div>
      <p class="form__aviso">{t('Ao enviar, você concorda com o uso dos seus dados para que a equipe Beiramar Private entre em contato, conforme a', 'By submitting, you agree that the Beiramar Private team may use your data to contact you, as described in our')} <a href="{b}{rota('privacidade')}">{t('Política de Privacidade', 'Privacy Policy')}</a>.</p>
      <div class="form__rodape"><button type="submit" class="btn btn-claro">{t('Enviar', 'Send')} {seta()}</button></div>
      <p class="form__status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
"""


def ecossistema(r, b, claro=True):
    tema = " tema-claro" if claro else ""
    frentes = [
        ("Beiramar Imóveis", t("Imobiliária full service desde 1981: compra, venda, locação e gestão de imóveis em Brasília. A Beiramar Private é a sua frente de alto padrão.",
                               "Full-service real estate firm since 1981: buying, selling, leasing and property management in Brasília. Beiramar Private is its luxury division.")),
        ("BRM Asset", t("Gestão de ativos imobiliários, com atuação nos mercados regionais de maior crescimento do país.",
                        "Real estate asset management, focused on Brazil’s fastest-growing regional markets.")),
        ("BRM IB", t("Investment banking: estrutura operações de equity e crédito no mercado imobiliário.",
                     "Investment banking: structures equity and credit transactions in real estate.")),
        ("BRM Inc", t("Incorporação imobiliária.", "Real estate development.")),
    ]
    itens = "".join(f'<div class="frente{" frente--destaque" if i == 0 else ""}"><h3>{e(n)}</h3><p>{e(d)}</p></div>'
                    for i, (n, d) in enumerate(frentes))
    return f"""<section class="secao{tema}" id="ecossistema">
  <div class="wrap ecossistema">
    <div class="revelar">
      <span class="rotulo rotulo--linha">{t('Ecossistema Beiramar', 'The Beiramar ecosystem')}</span>
      <h2 class="titulo" style="margin:22px 0 28px">{t('Por trás da Private, <em class="sem-quebra">45 anos</em> de Beiramar.', 'Behind Private, <em class="sem-quebra">45 years</em> of Beiramar.')}</h2>
      <p class="lead">{t('A Beiramar Private é a frente de alto padrão da Beiramar Imóveis, que integra o Grupo Beiramar: um ecossistema que une imobiliária, gestão de ativos, investment banking e incorporação. Para quem compra ou investe, isso significa solidez, informação e suporte em cada etapa.', 'Beiramar Private is the luxury division of Beiramar Imóveis, part of Grupo Beiramar: an ecosystem that brings together brokerage, asset management, investment banking and real estate development. For buyers and investors, this means solidity, market intelligence and support at every step.')}</p>
      <a href="{GRUPO}" class="btn btn-claro" target="_blank" rel="noopener" style="margin-top:36px">{t('Conheça o Grupo Beiramar', 'Discover Grupo Beiramar')} {seta()}</a>
    </div>
    <div class="frentes revelar">{itens}</div>
  </div>
</section>
"""


def numeros(r, b):
    n = numeros_dados()
    itens = "".join(f'<div class="numeros__item revelar"><p>{e(a)}</p><span class="bloco-preto">{e(c)}</span></div>' for a, c in n["itens"])
    fonte = f'<p class="numeros__fonte">{t("Fonte", "Source")}: {e(n["fonte"])}</p>' if n.get("fonte") else ""
    destaque = t('O Noroeste<br>já vendeu <em>94%</em> do que lançou.', 'Noroeste<br>has already sold <em>94%</em> of everything launched.')
    return f"""<section class="secao claro" id="numeros">
  <div class="wrap numeros">
    <div class="revelar">
      <span class="rotulo rotulo--linha">{e(n['titulo'])}</span>
      <p class="numeros__destaque" style="margin-top:28px">{destaque}</p>
    </div>
    <div class="numeros__lista">{itens}{fonte}</div>
  </div>
</section>
"""


def visor():
    return f"""<div class="visor" id="visor" role="dialog" aria-modal="true" aria-label="{t('Galeria de fotos', 'Photo gallery')}">
  <img src="" alt="">
  <button class="visor__btn visor__fechar" type="button" aria-label="{t('Fechar', 'Close')}"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  <button class="visor__btn visor__ant" type="button" aria-label="{t('Foto anterior', 'Previous photo')}">{seta()}</button>
  <button class="visor__btn visor__prox" type="button" aria-label="{t('Próxima foto', 'Next photo')}">{seta()}</button>
  <span class="visor__contador"></span>
</div>"""


def raiz_rel(caminho):
    """'../' repetido conforme a profundidade do caminho da página."""
    return "../" * caminho.strip("/").count("/") + ("../" if caminho.strip("/") else "")


def salvar(caminho, html, sitemap=True):
    """caminho completo (com 'en/' quando for o caso), sem barra no início; '' = raiz."""
    c = caminho.strip("/")
    destino = RAIZ / c / "index.html" if c else RAIZ / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    if sitemap:
        geradas.append(c + "/" if c else "")


# ---------------------------------------------------------------- páginas
def pagina_inicio():
    caminho = prefixo()
    r = raiz_rel(caminho)
    b = r + prefixo()
    par = ("", "en/")
    lista = emps()
    cards = "".join(card(r, b, x) for x in lista)
    regs = ""
    for slug, reg in regioes().items():
        qtd = sum(1 for x in lista if x["regiao"] == slug)
        regs += f"""<a class="regiao revelar" href="{b}{slug}/">
  {foto_faixas(r + img_site(reg['imagem']), r + img_site(reg['imagem'], True), reg['nome'], sizes='(max-width: 820px) 100vw, 50vw')}
  <span class="rotulo">Plano Piloto · Brasília</span>
  <h3>{e(reg['nome'])}</h3>
  <p>{e(reg['subtitulo'])}</p>
  <span class="regiao__rodape"><span>{qtd} {t('empreendimentos', 'properties')}</span>{seta()}</span>
</a>"""
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Beiramar Private",
        "url": DOMINIO + "/" + caminho, "logo": DOMINIO + "/apple-touch-icon.png", "image": DOMINIO + "/compartilhamento.jpg",
        "telephone": "+55 61 3142-6671", "areaServed": "Brasília, DF, Brazil",
        "parentOrganization": {"@type": "Organization", "name": "Beiramar Imóveis", "url": BEIRAMAR_IMOVEIS,
                               "parentOrganization": {"@type": "Organization", "name": "Grupo Beiramar", "url": GRUPO}},
        "sameAs": [INSTAGRAM, LINKEDIN, FACEBOOK]}, ensure_ascii=False)
    html = head(r, t("Beiramar Private | Imóveis de alto padrão no Plano Piloto", "Beiramar Private | Luxury real estate in Brasília’s Plano Piloto"),
                t("Curadoria de imóveis de alto padrão no Noroeste e na Quadra 500 do Sudoeste, em Brasília. Atendimento consultivo, discreto e personalizado da Beiramar.",
                  "Curated luxury homes in Noroeste and Quadra 500 Sudoeste, in Brasília’s Plano Piloto. Advisory, discreet and personal service by Beiramar."),
                caminho, par=par, extra=f'<script type="application/ld+json">{jsonld}</script>')
    html += topo(r, b, par)
    html += f"""<main>
<section class="hero">
  {foto_faixas(r + img_site('home-hero'), r + img_site('home-hero', True), t('Piscina privativa de cobertura com vista para o verde', 'Private rooftop pool overlooking the green'), 'hero__midia', eager=True)}
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Beiramar Private · {t('Plano Piloto', 'Brasília, Brazil')}</span>
      <h1 class="display">{t('Viver bem é uma decisão. Nós cuidamos do <em>endereço</em>.', 'Living well is a decision. We take care of the <em>address</em>.')}</h1>
      <p class="lead">{t('Curadoria de imóveis de alto padrão no Noroeste e na Quadra 500 do Sudoeste, com atendimento consultivo, discreto e personalizado.', 'Curated luxury homes in Noroeste and Quadra 500 Sudoeste, in the heart of Brasília’s Plano Piloto, with advisory, discreet and personal service.')}</p>
      <div class="hero__acoes">
        <a href="#empreendimentos" class="btn btn-claro">{t('Ver empreendimentos', 'View properties')} {seta()}</a>
        <a href="#contato" class="btn btn-linha">{t('Falar com um especialista', 'Talk to a specialist')}</a>
      </div>
    </div>
    <div class="hero__rodape">
      <dl class="hero__dados">
        <div><dt>{t('Empreendimentos', 'Properties')}</dt><dd>{len(lista)} {t('selecionados', 'selected')}</dd></div>
        <div><dt>{t('Regiões', 'Neighborhoods')}</dt><dd>{t('Noroeste e Quadra 500', 'Noroeste and Quadra 500')}</dd></div>
        <div><dt>{t('Atendimento', 'Service')}</dt><dd>{t('Consultivo e exclusivo', 'Advisory and exclusive')}</dd></div>
      </dl>
      <a href="#sobre" class="rolar"><span></span>{t('Role', 'Scroll')}</a>
    </div>
  </div>
</section>

<section class="secao tema-claro" id="sobre">
  <div class="wrap sobre">
    <figure class="sobre__foto moldura revelar"><img src="{r}{img_site('sobre')}" srcset="{r}{img_site('sobre', True)} 760w, {r}{img_site('sobre')} 1600w" sizes="(max-width: 900px) 100vw, 50vw" alt="{t('Fachada noturna de empreendimento de alto padrão no Noroeste', 'Night view of a luxury building in Noroeste')}" loading="lazy" decoding="async"></figure>
    <div class="revelar">
      <span class="rotulo rotulo--linha">{t('A Private', 'About Private')}</span>
      <h2 class="titulo">{t('A frente de alto padrão da <em>Beiramar</em>.', 'The luxury division of <em>Beiramar</em>.')}</h2>
      <div class="texto">
        <p>{t('A Beiramar Private é dedicada à curadoria de imóveis exclusivos nas regiões mais valorizadas de Brasília. Atuamos com foco em localização, arquitetura, padrão construtivo e potencial de valorização.', 'Beiramar Private curates exclusive homes in Brasília’s most valued neighborhoods, inside the Plano Piloto, the city’s modernist core and a UNESCO World Heritage Site. We focus on location, architecture, construction standards and appreciation potential.')}</p>
        <p>{t('Nosso atendimento é consultivo, discreto e personalizado, conduzido por especialistas que entendem o tempo, o perfil e as expectativas de quem busca viver ou investir com segurança no alto padrão.', 'Our service is advisory, discreet and personal, led by specialists who understand the timing, profile and expectations of those who want to live or invest safely in the luxury market.')}</p>
      </div>
      <div class="pilares">
        <div><strong>{t('Localização', 'Location')}</strong><p>{t('Endereços escassos, nos bairros que mais se valorizam no Plano Piloto.', 'Scarce addresses in the Plano Piloto neighborhoods with the strongest appreciation.')}</p></div>
        <div><strong>{t('Arquitetura', 'Architecture')}</strong><p>{t('Projetos assinados, com plantas amplas e identidade própria.', 'Signature projects with generous floor plans and a distinct identity.')}</p></div>
        <div><strong>{t('Padrão construtivo', 'Construction')}</strong><p>{t('Incorporadoras de referência e acabamentos de alto padrão.', 'Leading developers and high-end finishes.')}</p></div>
        <div><strong>{t('Valorização', 'Appreciation')}</strong><p>{t('Imóveis escolhidos para morar bem e preservar patrimônio.', 'Homes chosen to live well and preserve wealth.')}</p></div>
      </div>
    </div>
  </div>
</section>

<section class="secao" id="regioes">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">{t('Onde atuamos', 'Where we work')}</span><h2 class="titulo" style="margin-top:22px">{t('Dois endereços. <em>Nenhum</em> comum.', 'Two addresses. <em>Nothing</em> ordinary.')}</h2></div>
    </div>
    <div class="regioes">{regs}</div>
  </div>
</section>

<section class="secao tema-claro" id="empreendimentos">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">{t('Curadoria Private', 'Private selection')}</span><h2 class="titulo" style="margin-top:22px">{t('Empreendimentos <em>selecionados</em>.', '<em>Selected</em> properties.')}</h2></div>
      <div class="filtros" data-filtros="grade-emp" role="group" aria-label="{t('Filtrar por região', 'Filter by neighborhood')}">
        <button class="filtro" type="button" data-filtro="todos" aria-pressed="true">{t('Todos', 'All')}</button>
        <button class="filtro" type="button" data-filtro="noroeste" aria-pressed="false">Noroeste</button>
        <button class="filtro" type="button" data-filtro="quadra-500" aria-pressed="false">Quadra 500</button>
      </div>
    </div>
    <div class="grade" id="grade-emp">{cards}</div>
  </div>
</section>

<section class="secao secao--2" id="como-trabalhamos">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">{t('Como trabalhamos', 'How we work')}</span><h2 class="titulo" style="margin-top:22px">{t('Menos opções. Mais <em>acerto</em>.', 'Fewer options. Better <em>choices</em>.')}</h2></div>
      <p class="lead">{t('Um atendimento pensado para quem valoriza o próprio tempo.', 'A service designed for those who value their time.')}</p>
    </div>
    <div class="processo revelar">
      <div class="etapa"><span class="numero-serif">01</span><h3>{t('Escuta', 'Listening')}</h3><p>{t('Entendemos o seu momento, a sua rotina e o que o próximo endereço precisa entregar.', 'We understand your moment, your routine and what your next address needs to deliver.')}</p></div>
      <div class="etapa"><span class="numero-serif">02</span><h3>{t('Curadoria', 'Curation')}</h3><p>{t('Selecionamos poucas opções, alinhadas ao seu perfil, com as informações de cada projeto.', 'We select a few options aligned with your profile, with the details of each project.')}</p></div>
      <div class="etapa"><span class="numero-serif">03</span><h3>{t('Visita privada', 'Private viewing')}</h3><p>{t('Apresentamos os imóveis com hora marcada e atendimento exclusivo.', 'We show the properties by appointment, with exclusive service.')}</p></div>
      <div class="etapa"><span class="numero-serif">04</span><h3>{t('Negociação', 'Negotiation')}</h3><p>{t('Conduzimos proposta, documentação e fechamento com discrição e segurança.', 'We handle the offer, paperwork and closing with discretion and security.')}</p></div>
    </div>
  </div>
</section>

{ecossistema(r, b, claro=True)}
{contato(r, b, origem=t('Página inicial', 'Home (EN)'))}
</main>
"""
    html += rodape(r, b)
    salvar(caminho, html)


def pagina_regiao(slug):
    caminho = prefixo() + slug + "/"
    r = raiz_rel(caminho)
    b = r + prefixo()
    par = (f"{slug}/", f"en/{slug}/")
    reg = regioes()[slug]
    lista = [x for x in emps() if x["regiao"] == slug]
    cards = "".join(card(r, b, x) for x in lista)
    difs = "".join(f'<div class="diferencial"><span class="numero-serif">{i:02d}</span><h3>{e(a)}</h3><p>{e(d)}</p></div>'
                   for i, (a, d) in enumerate(reg["diferenciais"], 1))
    intro = "".join(f"<p>{e(p)}</p>" for p in reg["intro"])
    nor = slug == "noroeste"
    if en():
        dif_rot = f"Why {reg['rotulo']}"
        tit_emp = f"Properties in <em>{e(reg['rotulo'])}</em>."
        tit_cont = f"Receive the <em>{e(reg['rotulo'])}</em> selection."
    else:
        dif_rot = f"O diferencial {'do' if nor else 'da'} {reg['rotulo']}"
        tit_emp = f"Empreendimentos {'no' if nor else 'na'} <em>{e(reg['rotulo'])}</em>."
        tit_cont = f"Receba a curadoria {'do' if nor else 'da'} <em>{e(reg['rotulo'])}</em>."
    html = head(r, f"{reg['nome']} | Beiramar Private",
                f"{reg['titulo']} {sem_em(reg['titulo_destaque'])} {reg['subtitulo']}", caminho, par=par,
                imagem_og=img_site(reg["imagem"]))
    html += topo(r, b, par, slug)
    html += f"""<main>
<section class="hero">
  {foto_faixas(r + img_site(reg['imagem']), r + img_site(reg['imagem'], True), reg['nome'], 'hero__midia', eager=True)}
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Beiramar Private · Plano Piloto</span>
      <h1 class="display">{e(reg['titulo'])}<br>{reg['titulo_destaque']}</h1>
      <p class="lead">{e(reg['subtitulo'])}</p>
      <div class="hero__acoes">
        <a href="#empreendimentos" class="btn btn-claro">{t('Ver empreendimentos', 'View properties')} {seta()}</a>
        <a href="#contato" class="btn btn-linha">{t('Agendar visita', 'Book a viewing')}</a>
      </div>
    </div>
    <div class="hero__rodape">
      <dl class="hero__dados"><div><dt>{t('Empreendimentos', 'Properties')}</dt><dd>{len(lista)} {t('selecionados', 'selected')}</dd></div><div><dt>{t('Região', 'Neighborhood')}</dt><dd>{e(reg['nome'])}</dd></div></dl>
      <a href="#sobre" class="rolar"><span></span>{t('Role', 'Scroll')}</a>
    </div>
  </div>
</section>

{numeros(r, b) if nor else ""}

<section class="secao{"" if nor else " tema-claro"}" id="sobre">
  <div class="wrap">
    <div class="intro revelar">
      <div><span class="rotulo rotulo--linha">{t('Sobre a região', 'About the neighborhood')}</span><h2 class="titulo" style="margin-top:22px">{e(reg['intro_titulo'])}</h2></div>
      <div class="texto">{intro}</div>
    </div>
    <div class="cabeca revelar" style="margin:clamp(72px,8vw,120px) 0 0"><span class="rotulo rotulo--linha">{e(dif_rot)}</span></div>
    <div class="diferenciais revelar" style="margin-top:28px">{difs}</div>
  </div>
</section>

<section class="secao{" tema-claro" if nor else ""}" id="empreendimentos">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">{t('Curadoria Private', 'Private selection')}</span><h2 class="titulo" style="margin-top:22px">{tit_emp}</h2></div>
    </div>
    <div class="grade">{cards}</div>
  </div>
</section>

{ecossistema(r, b, claro=not nor)}
{contato(r, b, claro=nor, titulo=tit_cont, origem=t('Região ', 'Neighborhood (EN) ') + reg['nome'])}
</main>
"""
    html += rodape(r, b)
    salvar(caminho, html)


def pagina_empreendimento(x, lp=False):
    reg = regioes()[x["regiao"]]
    caminho = "lpamazesunside/" if lp else prefixo() + f"empreendimentos/{x['slug']}/"
    r = raiz_rel(caminho)
    b = r + prefixo()
    par = (f"empreendimentos/{x['slug']}/", f"en/empreendimentos/{x['slug']}/")
    desc = " ".join(x["descricao"])
    desc_meta = (f"{x['nome']}, {reg['nome']}: {x['metragem']}, {x['dormitorios']}. "
                 + desc[:110].rsplit(" ", 1)[0] + "…")
    texto = "".join(f"<p>{e(p)}</p>" for p in x["descricao"])
    assin = ""
    if x.get("incorporadora"):
        assin += f'<div><dt>{t("Incorporação", "Developer")}</dt><dd>{e(x["incorporadora"])}</dd></div>'
    for k, v in x.get("assinaturas", []):
        assin += f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>"
    assin_html = f'<dl class="assinaturas">{assin}</dl>' if assin else ""
    unidades = "".join(f'<div class="unidade"><h3>{e(u["titulo"])}</h3><ul>{"".join(f"<li>{e(i)}</li>" for i in u["itens"])}</ul></div>'
                       for u in x["unidades"])
    nota = f'<div class="nota moldura"><p>{e(x["nota"])}</p></div>' if x.get("nota") else ""

    n = x["galeria"]
    fotos = ""
    for i in range(1, n + 1):
        nome = f"{i:02d}"
        fotos += (f'<button type="button" data-foto="{r}{img_emp(x["slug"], nome)}" aria-label="{t("Ampliar foto", "Enlarge photo")} {i} {t("de", "of")} {n}">'
                  f'<img src="{r}{img_emp(x["slug"], nome, p=True)}" alt="{e(x["nome"])}, {t("foto", "photo")} {i}" loading="lazy" decoding="async"></button>')
    classe_gal = "galeria galeria--curta" if n <= 3 else "galeria"
    video = ""
    if x.get("video"):
        video = (f'<div class="video revelar"><button type="button" class="video__capa" data-video="{e(x["video"])}" '
                 f'data-titulo="{e(x["nome"])}" aria-label="{t("Assistir ao vídeo do", "Watch the video of")} {e(x["nome"])}">'
                 f'<img src="{r}{img_emp(x["slug"])}" alt="" loading="lazy" decoding="async">'
                 f'<span class="video__play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></span>'
                 f'<span class="video__rotulo">{t("Assistir ao vídeo", "Watch the video")}</span></button></div>')

    dados_hero = (f'<div><dt>{t("Metragem", "Size")}</dt><dd>{e(x["metragem"])}</dd></div>'
                  f'<div><dt>{t("Dormitórios", "Bedrooms")}</dt><dd>{e(x["dormitorios"])}</dd></div>')
    if x.get("status"):
        dados_hero += f'<div><dt>Status</dt><dd>{e(x["status"])}</dd></div>'
    elif x.get("incorporadora"):
        dados_hero += f'<div><dt>{t("Incorporação", "Developer")}</dt><dd>{e(x["incorporadora"])}</dd></div>'

    outros = [o for o in emps() if o["slug"] != x["slug"]]
    outros.sort(key=lambda o: o["regiao"] != x["regiao"])
    trilho = "".join(card(r, b, o, revelar=False) for o in outros)
    subnav = "" if lp else f"""<nav class="subnav" aria-label="{t('Nesta página', 'On this page')}">
  <div class="wrap">
    <span class="subnav__nome">{e(x['nome'])}</span>
    <div class="subnav__links">
      <a href="#sobre">{t('Sobre', 'Overview')}</a><a href="#galeria">{t('Galeria', 'Gallery')}</a><a href="#localizacao">{t('Localização', 'Location')}</a><a href="#outros">{t('Outros empreendimentos', 'Other properties')}</a>
    </div>
  </div>
</nav>"""
    outros_html = "" if lp else f"""<section class="secao" id="outros">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">{t('Curadoria Private', 'Private selection')}</span><h2 class="titulo" style="margin-top:22px">{t('Outros <em>empreendimentos</em>.', 'Other <em>properties</em>.')}</h2></div>
      <div class="trilho-nav" data-trilho="trilho-outros"><button type="button" data-dir="-1" aria-label="{t('Anteriores', 'Previous')}">{seta()}</button><button type="button" data-dir="1" aria-label="{t('Próximos', 'Next')}">{seta()}</button></div>
    </div>
    <div class="trilho" id="trilho-outros" tabindex="0" aria-label="{t('Outros empreendimentos', 'Other properties')}">{trilho}</div>
    <div class="trilho-progresso" aria-hidden="true"><span></span></div>
  </div>
</section>"""

    if en():
        conheca = f"Discover {x['nome']}"
        tit_cont = f"Receive details on <em>{e(x['nome'])}</em>."
        conhecer_reg = f"Discover {reg['rotulo']}"
    else:
        conheca = f"Conheça o {x['nome']}"
        tit_cont = f"Receba as informações do <em>{e(x['nome'])}</em>."
        conhecer_reg = f"Conhecer {'o' if x['regiao'] == 'noroeste' else 'a'} {reg['rotulo']}"
    titulo_pagina = f"{x['nome']} | {reg['rotulo']} | Beiramar Private"
    html = head(r, titulo_pagina, desc_meta, caminho, par=None if lp else par, imagem_og=img_emp(x["slug"]),
                canonical=f"{DOMINIO}/empreendimentos/{x['slug']}/" if lp else None)
    html += topo(r, b, par, "", lp=lp)
    html += f"""<main>
<section class="hero emp-hero">
  {foto_faixas(r + img_emp(x['slug']), r + img_emp(x['slug'], p=True), f"{x['nome']}, {reg['nome']}", 'hero__midia', eager=True)}
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Beiramar Private · {e(reg['rotulo'])}</span>
      <h1 class="display">{e(x['nome'])}</h1>
      <p class="chamada">{x['chamada']}</p>
      <div class="hero__acoes">
        <a href="#contato" class="btn btn-claro">{t('Receber informações', 'Request information')} {seta()}</a>
        <a href="#galeria" class="btn btn-linha">{t('Ver fotos', 'View photos')}</a>
      </div>
    </div>
    <div class="hero__rodape">
      <dl class="hero__dados">{dados_hero}</dl>
      <a href="#sobre" class="rolar"><span></span>{t('Role', 'Scroll')}</a>
    </div>
  </div>
</section>
{subnav}
<section class="secao tema-claro" id="sobre">
  <div class="wrap ficha">
    <div class="revelar">
      <span class="rotulo rotulo--linha">{e(conheca)}</span>
      <h2 class="titulo">{e(x['metragem'])} · <em>{e(x['dormitorios'])}</em></h2>
      <div class="texto">{texto}</div>
      {assin_html}
    </div>
    <div class="revelar">
      <div class="unidades">{unidades}</div>
      {nota}
    </div>
  </div>
</section>

<section class="secao secao--compacta secao--2" id="galeria">
  <div class="wrap">
    <div class="cabeca revelar"><div class="cabeca__texto"><span class="rotulo rotulo--linha">{t('Galeria', 'Gallery')}</span><h2 class="titulo" style="margin-top:22px">{t('Para <em>imaginar</em> a vida aqui.', 'To <em>imagine</em> life here.')}</h2></div></div>
    {video}
    <div class="{classe_gal} revelar">{fotos}</div>
  </div>
</section>

<section class="secao tema-claro" id="localizacao">
  <div class="wrap local">
    <div class="local__cartao moldura revelar">
      <span class="rotulo rotulo--linha">{t('Localização', 'Location')}</span>
      <p class="local__endereco">{e(x['endereco'])}<br><span style="font-size:.6em;color:var(--cinza)">Brasília · DF</span></p>
      <a href="{e(x['mapa'])}" class="btn btn-linha" target="_blank" rel="noopener">{t('Como chegar', 'Get directions')} {seta()}</a>
    </div>
    <a class="revelar" href="{b}{x['regiao']}/" style="display:block">
      {foto_faixas(r + img_site(reg['imagem']), r + img_site(reg['imagem'], True), reg['nome'], 'local__foto', sizes='(max-width: 900px) 100vw, 50vw')}
      <span class="regiao__rodape" style="margin-top:18px;border-top:0;padding-top:0">{e(conhecer_reg)} {seta()}</span>
    </a>
  </div>
</section>

{outros_html}
{ecossistema(r, b, claro=True)}
{contato(r, b, titulo=tit_cont, texto=t("Plantas, valores e disponibilidade atualizados. Um especialista Private entra em contato com você.", "Floor plans, prices and up-to-date availability. A Private specialist will contact you."), interesse=x['nome'], origem=("Landing page " if lp else t("Página ", "Page (EN) ")) + x['nome'])}
</main>
{visor()}
"""
    html += rodape(r, b)
    salvar(caminho, html, sitemap=not lp)


def pagina_obrigado():
    caminho = prefixo() + rota("obrigado")
    r = raiz_rel(caminho)
    b = r + prefixo()
    par = (rota("obrigado", "pt"), "en/" + rota("obrigado", "en"))
    html = head(r, t("Obrigado | Beiramar Private", "Thank you | Beiramar Private"),
                t("Recebemos o seu contato. Um especialista Beiramar Private vai falar com você em breve.",
                  "We have received your message. A Beiramar Private specialist will contact you shortly."),
                caminho, par=par, noindex=True)
    html += topo(r, b, par, eco_local=False)
    html += f"""<main>
<section class="hero" style="min-height:100svh">
  {foto_faixas(r + img_site('home-hero'), r + img_site('home-hero', True), '', 'hero__midia', eager=True)}
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">{t('Contato recebido', 'Message received')}</span>
      <h1 class="display">{t('Obrigado. Seu próximo endereço <em>começa aqui</em>.', 'Thank you. Your next address <em>starts here</em>.')}</h1>
      <p class="lead">{t('Um especialista Beiramar Private vai entrar em contato com você em breve. Se preferir, continue agora pelo WhatsApp.', 'A Beiramar Private specialist will contact you shortly. If you prefer, continue the conversation on WhatsApp now.')}</p>
      <div class="hero__acoes">
        <a href="{wa()}" data-whats-obrigado class="btn btn-claro" target="_blank" rel="noopener">{t('Continuar no WhatsApp', 'Continue on WhatsApp')} {seta()}</a>
        <a href="{b}" class="btn btn-linha">{t('Voltar ao site', 'Back to the website')}</a>
      </div>
    </div>
  </div>
</section>
</main>
"""
    html += rodape(r, b)
    salvar(caminho, html, sitemap=False)


POST_SLUG = "brasilia-onde-a-arquitetura-nao-apenas-abriga-ela-emociona"
POST_TITULO = "Brasília: onde a arquitetura não apenas abriga, ela emociona."
POST_RESUMO = "Do legado de Lúcio Costa e Niemeyer à Quadra 500 do Sudoeste: como a arquitetura de Brasília inspira o novo alto padrão."


def pagina_blog():
    """Blog apenas em português."""
    caminho = "blog/"
    r = raiz_rel(caminho)
    b = r
    par = ("blog/", None)
    html = head(r, "Blog | Beiramar Private", "Arquitetura, bairros e o mercado de alto padrão em Brasília, pelo olhar da curadoria Beiramar Private.", caminho)
    html += topo(r, b, par, "blog", eco_local=False)
    html += f"""<main>
<section class="pagina-topo"><div class="wrap">
  <span class="rotulo rotulo--linha">Blog</span>
  <h1 class="titulo">Para escolher <em>onde morar</em> em Brasília.</h1>
  <p class="lead">Arquitetura, bairros e o mercado de alto padrão, pelo olhar da curadoria Private.</p>
</div></section>
<section class="secao secao--compacta tema-claro"><div class="wrap">
  <div class="grade">
    <article class="card revelar">
      <div class="card__midia"><img src="{r}{img_site('quadra-500-b', True)}" alt="Vista aérea da Quadra 500 do Sudoeste" loading="lazy"></div>
      <div class="card__corpo">
        <span class="card__regiao">Arquitetura · Quadra 500</span>
        <h2 class="card__nome" style="text-transform:none;font-weight:400;font-size:24px"><a class="card__link" href="{POST_SLUG}/">{e(POST_TITULO)}</a></h2>
        <p class="card__chamada">{e(POST_RESUMO)}</p>
        <div class="card__mais">Ler artigo {seta()}</div>
      </div>
    </article>
  </div>
</div></section>
{contato(r, b, origem='Blog')}
</main>
"""
    html += rodape(r, b)
    salvar(caminho, html)

    caminho = f"blog/{POST_SLUG}/"
    r = raiz_rel(caminho)
    b = r
    par = (caminho, None)
    corpo = (RAIZ / "dados" / "blog" / f"{POST_SLUG}.html").read_text(encoding="utf-8")
    html = head(r, f"{POST_TITULO} | Beiramar Private", POST_RESUMO, caminho, imagem_og=img_site("quadra-500-b"))
    html += topo(r, b, par, "blog", eco_local=False)
    html += f"""<main>
<section class="pagina-topo"><div class="wrap">
  <a href="../" class="rotulo rotulo--linha">Blog</a>
  <h1 class="titulo">Brasília: onde a arquitetura não apenas abriga, <em>ela emociona</em>.</h1>
  <p class="lead">{e(POST_RESUMO)}</p>
</div></section>
<section class="secao secao--compacta tema-claro"><div class="wrap">
  {foto_faixas(r + img_site('quadra-500-b'), r + img_site('quadra-500-b', True), 'Vista aérea da Quadra 500 do Sudoeste', 'faixas--base', sizes='100vw').replace('class="faixas faixas--base"', 'class="faixas faixas--base" style="aspect-ratio:21/9;margin-bottom:clamp(48px,6vw,80px)"')}
  <article class="artigo">{corpo}</article>
</div></section>
{contato(r, b, titulo='Conheça a <em>Quadra 500</em> com a curadoria Private.', origem='Blog: ' + POST_TITULO)}
</main>
"""
    html += rodape(r, b)
    salvar(caminho, html)


def pagina_privacidade():
    caminho = prefixo() + rota("privacidade")
    r = raiz_rel(caminho)
    b = r + prefixo()
    par = (rota("privacidade", "pt"), "en/" + rota("privacidade", "en"))
    corpo = (RAIZ / "dados" / t("privacidade.html", "privacidade-en.html")).read_text(encoding="utf-8")
    html = head(r, t("Privacidade e cookies | Beiramar Private", "Privacy and cookies | Beiramar Private"),
                t("Como a Beiramar Private trata os dados pessoais de quem visita o site e entra em contato, conforme a LGPD.",
                  "How Beiramar Private handles the personal data of website visitors and contacts, under Brazil’s LGPD."),
                caminho, par=par)
    html += topo(r, b, par, eco_local=False)
    html += f"""<main>
<section class="pagina-topo"><div class="wrap">
  <span class="rotulo rotulo--linha">{t('Documentos legais', 'Legal')}</span>
  <h1 class="titulo">{t('Privacidade e <em>cookies</em>.', 'Privacy and <em>cookies</em>.')}</h1>
  <p class="lead">{t('Como tratamos os dados pessoais de quem visita este site e entra em contato conosco, conforme a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).', 'How we handle the personal data of those who visit this website and contact us, under Brazil’s General Data Protection Law (Law no. 13,709/2018).')}</p>
</div></section>
<section class="secao secao--compacta tema-claro"><div class="wrap"><article class="artigo legal">{corpo}</article></div></section>
</main>
"""
    html += rodape(r, b)
    salvar(caminho, html)


def redirecionar(antigo, novo_rel, novo_abs):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>Beiramar Private</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{novo_abs}">
<meta http-equiv="refresh" content="0; url={novo_rel}">
<script>location.replace("{novo_rel}" + location.search + location.hash);</script>
</head><body style="background:#131415;color:#FDFDFD;font-family:sans-serif">
<p>Esta página mudou de endereço: <a href="{novo_rel}" style="color:#FDFDFD">{novo_abs}</a></p>
</body></html>
"""
    destino = RAIZ / antigo / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    return antigo


def pagina_404():
    # Servida em qualquer endereço inexistente: usa caminhos absolutos a partir da raiz do domínio.
    r = "/"
    html = head(r, "Página não encontrada | Beiramar Private", "Esta página não existe ou mudou de endereço.", "404.html", noindex=True)
    html += topo(r, r, ("", "en/"), eco_local=False)
    html += f"""<main>
<section class="pagina-topo" style="min-height:80svh;display:flex;align-items:center"><div class="wrap">
  <span class="rotulo rotulo--linha">Erro 404 · Page not found</span>
  <h1 class="titulo">Este endereço <em>não existe</em>.</h1>
  <p class="lead">Mas temos outros que valem a visita. · This page does not exist, but our properties do.</p>
  <div class="hero__acoes"><a href="/" class="btn btn-claro">Ir para o início {seta()}</a><a href="/en/" class="btn btn-linha">English version</a></div>
</div></section>
</main>
"""
    html += rodape(r, r)
    (RAIZ / "404.html").write_text(html, encoding="utf-8")


def main():
    global LANG
    # limpa redirecionamentos antigos gerados anteriormente
    reg_arquivo = RAIZ / "dados" / ".redirecionamentos"
    if reg_arquivo.exists():
        for p in reg_arquivo.read_text().split():
            alvo = RAIZ / p
            if alvo.is_dir() and (alvo / "index.html").exists() and "location.replace" in (alvo / "index.html").read_text():
                shutil.rmtree(alvo)
    if (RAIZ / "en").exists():
        shutil.rmtree(RAIZ / "en")

    for LANG in ("pt", "en"):
        pagina_inicio()
        for slug in REG_PT:
            pagina_regiao(slug)
        for x in emps():
            pagina_empreendimento(x)
        pagina_obrigado()
        pagina_privacidade()
    LANG = "pt"
    if any(x["slug"] == "amaze-sunside" for x in EMPS_PT):
        pagina_empreendimento(next(x for x in EMPS_PT if x["slug"] == "amaze-sunside"), lp=True)
    pagina_blog()
    pagina_404()

    # endereços antigos do WordPress → novos
    redirs = []
    for x in EMPS_PT:
        for antigo in x.get("antigos", []):
            redirs.append(redirecionar(antigo, f"../empreendimentos/{x['slug']}/", f"{DOMINIO}/empreendimentos/{x['slug']}/"))
    redirs.append(redirecionar("quadra500", "../quadra-500/", f"{DOMINIO}/quadra-500/"))
    redirs.append(redirecionar(POST_SLUG, f"../blog/{POST_SLUG}/", f"{DOMINIO}/blog/{POST_SLUG}/"))
    reg_arquivo.write_text("\n".join(redirs) + "\n")

    urls = "".join(f"  <url><loc>{DOMINIO}/{c}</loc></url>\n" for c in geradas)
    (RAIZ / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (RAIZ / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (RAIZ / ".nojekyll").write_text("")
    print(f"{len(geradas)} páginas geradas (pt + en), {len(redirs)} redirecionamentos.")


if __name__ == "__main__":
    main()
