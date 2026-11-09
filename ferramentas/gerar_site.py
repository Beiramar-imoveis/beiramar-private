#!/usr/bin/env python3
"""Gera as páginas do site da Beiramar Private a partir de dados/empreendimentos.json.

Uso (na pasta do projeto):
    python3 ferramentas/gerar_site.py

O script recria todas as páginas HTML (início, regiões, empreendimentos, blog,
privacidade, obrigado), os redirecionamentos dos endereços antigos do WordPress,
o sitemap.xml e o robots.txt. Não precisa instalar nada além do Python 3.

Todos os links internos são relativos, então o site funciona tanto no domínio
próprio quanto na prévia do GitHub Pages (usuario.github.io/beiramar-private/).
"""
import json
import os
import shutil
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = json.loads((RAIZ / "dados" / "empreendimentos.json").read_text(encoding="utf-8"))

DOMINIO = "https://beiramarprivate.com.br"
WHATS_NUM = "556131426671"
WHATS_TXT = "(61) 3142-6671"
WHATS_MSG = "Olá! Quero falar com um especialista Beiramar Private."
INSTAGRAM = "https://www.instagram.com/beiramarprivate/"
LINKEDIN = "https://www.linkedin.com/company/beiramarimoveis/"
FACEBOOK = "https://www.facebook.com/BeiramarImoveis"
GRUPO = "https://grupobeiramar.com.br/"
# Formulário: Web3Forms (mesmo serviço do site do Grupo). A chave define o e-mail que recebe os contatos.
WEB3FORMS_KEY = "3d4ebba9-bbea-4efb-b910-c1501ea4f2af"
ANO = "2026"

REGIOES = {r["slug"]: r for r in DADOS["regioes"]}
EMPS = [e for e in DADOS["empreendimentos"] if e.get("ativo", True)]
EMP = {e["slug"]: e for e in EMPS}

LOGO_SVG = (RAIZ / "imagens" / "site" / "logo-beiramar.svg").read_text(encoding="utf-8")
LOGO_VIEWBOX = LOGO_SVG.split('viewBox="')[1].split('"')[0]
LOGO_PATH = LOGO_SVG.split(' d="')[1].split('"')[0]

geradas = []  # caminhos para o sitemap


# ---------------------------------------------------------------- utilidades
def e(t):
    return escape(str(t), quote=True)


def wa(msg=WHATS_MSG):
    from urllib.parse import quote
    return f"https://wa.me/{WHATS_NUM}?text={quote(msg)}"


def seta():
    return ('<svg class="seta" viewBox="0 0 64 12" aria-hidden="true">'
            '<path d="M0 6h62M57 1l5 5-5 5"/></svg>')


def logo(classe=""):
    return (f'<svg class="{classe}" viewBox="{LOGO_VIEWBOX}" role="img" aria-label="Beiramar">'
            f'<use href="#logo-beiramar"/></svg>')


def assinatura(extra=""):
    """Logo Beiramar dentro da moldura (grafismo 1)."""
    return f'<span class="assinatura moldura {extra}">{logo()}</span>'


ICONES = {
    "whats": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.69.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.04 21.8h-.01a9.8 9.8 0 0 1-5-1.37l-.36-.21-3.72.98 1-3.63-.24-.37a9.8 9.8 0 0 1-1.5-5.22c0-5.42 4.41-9.83 9.84-9.83a9.77 9.77 0 0 1 6.95 2.88 9.77 9.77 0 0 1 2.88 6.95c0 5.43-4.41 9.83-9.84 9.83zm8.37-18.2A11.75 11.75 0 0 0 12.04.13C5.5.13.18 5.45.18 11.99c0 2.09.55 4.13 1.59 5.93L.08 24l6.23-1.63a11.82 11.82 0 0 0 5.72 1.46h.01c6.54 0 11.86-5.32 11.86-11.86 0-3.17-1.23-6.15-3.47-8.39z"/></svg>',
    "insta": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.72 3.72 0 0 1-1.38-.9 3.72 3.72 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.13 1.38A5.9 5.9 0 0 0 .63 4.14C.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.3.79.72 1.46 1.38 2.13a5.9 5.9 0 0 0 2.13 1.38c.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56a5.9 5.9 0 0 0 2.13-1.38 5.9 5.9 0 0 0 1.38-2.13c.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91a5.9 5.9 0 0 0-1.38-2.13A5.9 5.9 0 0 0 19.86.63C19.1.33 18.22.13 16.95.07 15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.62 23.1 24 18.1 24 12.07"/></svg>',
}
MENU_ICONE = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>')


def img_emp(slug, nome="capa", p=False):
    return f"imagens/empreendimentos/{slug}/{nome}{'-p' if p else ''}.webp"


def img_site(nome, p=False):
    return f"imagens/site/{nome}{'-p' if p else ''}.webp"


def foto_faixas(src_rel, src_p_rel, alt, classe="", sizes="(max-width: 820px) 100vw, 68vw", eager=False):
    """Foto com o degradê em faixas (grafismo 2)."""
    carrega = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="faixas {classe}"><img src="{src_rel}" srcset="{src_p_rel} 760w, {src_rel} 1600w" '
            f'sizes="{sizes}" alt="{e(alt)}" {carrega} decoding="async"></div>')


# ---------------------------------------------------------------- blocos comuns
def head(r, titulo, descricao, caminho, imagem_og="compartilhamento.jpg", noindex=False, canonical=None, extra=""):
    url = f"{DOMINIO}/{caminho}"
    can = canonical or url
    og_img = imagem_og if imagem_og.startswith("http") else f"{DOMINIO}/{imagem_og}"
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{e(can)}">
{robots}
<meta name="theme-color" content="#131415">
<script>document.documentElement.classList.add("js")</script>
<link rel="icon" type="image/png" sizes="64x64" href="{r}favicon.png">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
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
<link rel="stylesheet" href="{r}css/consentimento.css">
<link rel="stylesheet" href="{r}css/private.css">
{extra}
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="logo-beiramar" viewBox="{LOGO_VIEWBOX}"><path fill-rule="evenodd" fill="currentColor" d="{LOGO_PATH}"/></symbol></svg>
"""


def topo(r, atual="", lp=False):
    if lp:
        nav = (f'<nav class="nav" id="nav" aria-label="Principal">'
               f'<a href="#contato" class="nav-cta">Falar com um especialista</a></nav>')
    else:
        itens = [("noroeste", f"{r}noroeste/", "Noroeste"), ("quadra-500", f"{r}quadra-500/", "Quadra 500"),
                 ("empreendimentos", f"{r}#empreendimentos", "Empreendimentos"), ("private", f"{r}#sobre", "A Private"),
                 ("blog", f"{r}blog/", "Blog")]
        links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == atual else ""}>{t}</a>' for k, h, t in itens)
        nav = (f'<nav class="nav" id="nav" aria-label="Principal">{links}'
               f'<a href="#contato" class="nav-cta">Falar com um especialista</a></nav>')
    toggle = "" if lp else (f'<button class="nav-toggle" type="button" aria-controls="nav" aria-expanded="false" '
                            f'aria-label="Abrir menu">{MENU_ICONE}</button>')
    return f"""<header class="topo" id="topo">
  <div class="wrap">
    <a href="{r}" class="marca" aria-label="Beiramar Private — início">{assinatura()}<span class="marca__nome">Private</span></a>
    {nav}
    {toggle}
  </div>
</header>
"""


def rodape(r):
    noroeste = "".join(f'<li><a href="{r}empreendimentos/{x["slug"]}/">{e(x["nome"])}</a></li>' for x in EMPS if x["regiao"] == "noroeste")
    q500 = "".join(f'<li><a href="{r}empreendimentos/{x["slug"]}/">{e(x["nome"])}</a></li>' for x in EMPS if x["regiao"] == "quadra-500")
    return f"""<footer class="rodape">
  <div class="wrap">
    <div class="rodape__topo">
      <div>
        <a href="{r}" aria-label="Beiramar Private — início">{assinatura()}</a>
        <p class="rodape__frase">A frente de alto padrão da <em>Beiramar</em> no Plano Piloto.</p>
      </div>
      <div><h4>Noroeste</h4><ul>{noroeste}</ul></div>
      <div><h4>Quadra 500</h4><ul>{q500}</ul></div>
      <div>
        <h4>Contato</h4>
        <ul>
          <li><a href="{wa()}" target="_blank" rel="noopener">WhatsApp {WHATS_TXT}</a></li>
          <li><a href="{r}blog/">Blog</a></li>
          <li><a href="{GRUPO}" target="_blank" rel="noopener">Grupo Beiramar</a></li>
        </ul>
        <div class="redes" style="margin-top:22px">
          <a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram da Beiramar Private">{ICONES['insta']}</a>
          <a href="{LINKEDIN}" target="_blank" rel="noopener" aria-label="LinkedIn da Beiramar">{ICONES['linkedin']}</a>
          <a href="{FACEBOOK}" target="_blank" rel="noopener" aria-label="Facebook da Beiramar">{ICONES['facebook']}</a>
        </div>
      </div>
    </div>
    <div class="rodape__base">
      <span>© {ANO} Beiramar Private · uma frente da Beiramar Imóveis, empresa do Grupo Beiramar.</span>
      <nav aria-label="Links legais"><a href="{r}privacidade/">Privacidade e cookies</a><button type="button" class="gb-cookie-prefs-link" data-cookie-preferences>Preferências de cookies</button></nav>
    </div>
  </div>
</footer>
<a class="whats" href="{wa()}" target="_blank" rel="noopener" aria-label="Falar pelo WhatsApp">{ICONES['whats']}</a>
<script src="{r}js/private.js" defer></script>
<script src="{r}js/consentimento.js" defer></script>
</body>
</html>
"""


def card(r, x):
    reg = REGIOES[x["regiao"]]
    selo = f'<span class="selo">{e(x["status"])}</span>' if x.get("status") else ""
    return f"""<article class="card revelar" data-regiao="{x['regiao']}">
  <div class="card__midia">{selo}<img src="{r}{img_emp(x['slug'], p=True)}" alt="{e(x['nome'])}, {e(reg['rotulo'])}" loading="lazy" decoding="async"></div>
  <div class="card__corpo">
    <span class="card__regiao">{e(reg['nome'])}</span>
    <h3 class="card__nome"><a class="card__link" href="{r}empreendimentos/{x['slug']}/">{e(x['nome'])}</a></h3>
    <p class="card__chamada">{x['chamada']}</p>
    <div class="card__dados"><div><span>Metragem</span>{e(x['metragem'])}</div><div><span>Dormitórios</span>{e(x['dormitorios'])}</div></div>
    <div class="card__mais">Conhecer {seta()}</div>
  </div>
</article>"""


def opcoes_interesse(selecionado=""):
    out = ['<option value="" disabled' + ("" if selecionado else " selected") + '>Selecione</option>']
    for slug, reg in REGIOES.items():
        out.append(f'<optgroup label="{e(reg["nome"])}">')
        for x in EMPS:
            if x["regiao"] == slug:
                sel = " selected" if x["nome"] == selecionado else ""
                out.append(f'<option{sel}>{e(x["nome"])}</option>')
        out.append("</optgroup>")
    out.append('<option>Quero uma indicação da curadoria</option>')
    return "".join(out)


def contato(r, titulo='Vamos encontrar o seu <em>próximo endereço</em>.', texto=None, interesse="", origem="Site"):
    texto = texto or ("Conte o que você procura. Um especialista Private retorna com opções selecionadas "
                      "para o seu perfil, com discrição e sem compromisso.")
    return f"""<section class="secao" id="contato">
  <div class="wrap contato">
    <div class="revelar">
      <span class="rotulo rotulo--linha">Atendimento Private</span>
      <h2 class="titulo">{titulo}</h2>
      <p class="lead">{texto}</p>
      <div class="contato__canais">
        <a href="{wa()}" target="_blank" rel="noopener"><span><small>WhatsApp</small>{WHATS_TXT}</span>{seta()}</a>
        <a href="{INSTAGRAM}" target="_blank" rel="noopener"><span><small>Instagram</small>@beiramarprivate</span>{seta()}</a>
      </div>
    </div>
    <form class="form revelar" action="https://api.web3forms.com/submit" method="POST" data-lead data-obrigado="{r}obrigado/">
      <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
      <input type="hidden" name="from_name" value="Site Beiramar Private">
      <input type="hidden" name="origem" value="{e(origem)}">
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="campo campo--inteiro"><label for="f-nome">Nome</label><input id="f-nome" name="nome" type="text" autocomplete="name" placeholder="Como podemos te chamar?" required></div>
      <div class="campo"><label for="f-whats">WhatsApp</label><input id="f-whats" name="whatsapp" type="tel" inputmode="tel" autocomplete="tel" placeholder="(61) 99999-9999" minlength="14" required></div>
      <div class="campo"><label for="f-email">E-mail</label><input id="f-email" name="email" type="email" autocomplete="email" placeholder="seu@email.com" required></div>
      <div class="campo"><label for="f-interesse">Interesse</label><select id="f-interesse" name="interesse" required>{opcoes_interesse(interesse)}</select></div>
      <div class="campo"><label for="f-quartos">Dormitórios</label><select id="f-quartos" name="quartos"><option value="">Indiferente</option><option>Studio ou 1 quarto</option><option>2 quartos</option><option>3 quartos ou suítes</option><option>4 suítes</option><option>Cobertura</option></select></div>
      <div class="campo campo--inteiro"><label for="f-msg">Mensagem <span style="opacity:.6">(opcional)</span></label><textarea id="f-msg" name="mensagem" rows="3" placeholder="Conte rapidamente o que você procura."></textarea></div>
      <p class="form__aviso">Ao enviar, você concorda com o uso dos seus dados para que a equipe Beiramar Private entre em contato, conforme a <a href="{r}privacidade/">Política de Privacidade</a>.</p>
      <div class="form__rodape"><button type="submit" class="btn btn-claro">Enviar {seta()}</button></div>
      <p class="form__status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
"""


def institucional(r):
    return f"""<section class="secao secao--compacta secao--2">
  <div class="wrap institucional revelar">
    {assinatura()}
    <div>
      <span class="rotulo rotulo--linha">Beiramar Private</span>
      <p class="subtitulo" style="margin:20px 0 18px;max-width:760px">A frente de alto padrão da Beiramar, dedicada à curadoria de imóveis exclusivos nas regiões mais valorizadas de Brasília.</p>
      <p class="texto" style="max-width:720px">Nosso atendimento é consultivo, discreto e personalizado, conduzido por especialistas que entendem o tempo, o perfil e as expectativas de quem busca viver ou investir com segurança no alto padrão.</p>
    </div>
  </div>
</section>
"""


def numeros(r, com_link=True):
    n = DADOS["numeros_noroeste"]
    itens = "".join(f'<div class="numeros__item revelar"><p>{e(a)}</p><span class="bloco-preto">{e(b)}</span></div>' for a, b in n["itens"])
    fonte = f'<p class="numeros__fonte">Fonte: {e(n["fonte"])}</p>' if n.get("fonte") else ""
    link = (f'<a href="{r}noroeste/" class="btn btn-linha" style="margin-top:40px">Conhecer o Noroeste {seta()}</a>'
            if com_link else "")
    return f"""<section class="secao claro" id="numeros">
  <div class="listras" aria-hidden="true"></div>
  <div class="wrap numeros">
    <div class="revelar">
      <span class="rotulo rotulo--linha">{e(n['titulo'])}</span>
      <p class="numeros__destaque" style="margin-top:28px">O Noroeste<br>já vendeu <em>94%</em> do que lançou.</p>
      {link}
    </div>
    <div class="numeros__lista">{itens}{fonte}</div>
  </div>
</section>
"""


def visor():
    return f"""<div class="visor" id="visor" role="dialog" aria-modal="true" aria-label="Galeria de fotos">
  <img src="" alt="">
  <button class="visor__btn visor__fechar" type="button" aria-label="Fechar"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  <button class="visor__btn visor__ant" type="button" aria-label="Foto anterior">{seta()}</button>
  <button class="visor__btn visor__prox" type="button" aria-label="Próxima foto">{seta()}</button>
  <span class="visor__contador"></span>
</div>"""


def salvar(caminho, html, sitemap=True):
    destino = RAIZ / caminho / "index.html" if caminho else RAIZ / "index.html"
    if caminho.endswith(".html"):
        destino = RAIZ / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    if sitemap:
        geradas.append(caminho if caminho.endswith(".html") or not caminho else caminho + "/")


# ---------------------------------------------------------------- páginas
def pagina_inicio():
    r = ""
    n_emp = len(EMPS)
    cards = "".join(card(r, x) for x in EMPS)
    regioes = ""
    for slug, reg in REGIOES.items():
        qtd = sum(1 for x in EMPS if x["regiao"] == slug)
        regioes += f"""<a class="regiao revelar" href="{slug}/">
  {foto_faixas(img_site(reg['imagem']), img_site(reg['imagem'], True), reg['nome'], sizes='(max-width: 820px) 100vw, 50vw')}
  <span class="rotulo">Plano Piloto</span>
  <h3>{e(reg['nome'])}</h3>
  <p>{e(reg['subtitulo'])}</p>
  <span class="regiao__rodape"><span>{qtd} empreendimentos</span>{seta()}</span>
</a>"""
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Beiramar Private",
        "url": DOMINIO + "/", "logo": DOMINIO + "/apple-touch-icon.png", "image": DOMINIO + "/compartilhamento.jpg",
        "telephone": "+55 61 3142-6671", "areaServed": "Brasília, DF",
        "parentOrganization": {"@type": "Organization", "name": "Grupo Beiramar", "url": GRUPO},
        "sameAs": [INSTAGRAM, LINKEDIN, FACEBOOK]}, ensure_ascii=False)
    html = head(r, "Beiramar Private | Imóveis de alto padrão no Plano Piloto",
                "Curadoria de imóveis de alto padrão no Noroeste e na Quadra 500 do Sudoeste, em Brasília. Atendimento consultivo, discreto e personalizado da Beiramar.",
                "", extra=f'<script type="application/ld+json">{jsonld}</script>')
    html += topo(r)
    html += f"""<main>
<section class="hero">
  {foto_faixas(img_site('home-hero'), img_site('home-hero', True), 'Piscina privativa de cobertura com vista para o verde', 'hero__midia', eager=True)}
  <div class="listras" aria-hidden="true"></div>
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Beiramar Private · Plano Piloto</span>
      <h1 class="display">Viver bem é uma decisão. Nós cuidamos do <em>endereço</em>.</h1>
      <p class="lead">Curadoria de imóveis de alto padrão no Noroeste e na Quadra 500 do Sudoeste, com atendimento consultivo, discreto e personalizado.</p>
      <div class="hero__acoes">
        <a href="#empreendimentos" class="btn btn-claro">Ver empreendimentos {seta()}</a>
        <a href="#contato" class="btn btn-linha">Falar com um especialista</a>
      </div>
    </div>
    <div class="hero__rodape">
      <dl class="hero__dados">
        <div><dt>Empreendimentos</dt><dd>{n_emp} selecionados</dd></div>
        <div><dt>Regiões</dt><dd>Noroeste e Quadra 500</dd></div>
        <div><dt>Atendimento</dt><dd>Consultivo e exclusivo</dd></div>
      </dl>
      <a href="#sobre" class="rolar"><span></span>Role</a>
    </div>
  </div>
</section>

<section class="secao" id="sobre">
  <div class="wrap sobre">
    <figure class="sobre__foto moldura revelar"><img src="{img_site('sobre')}" srcset="{img_site('sobre', True)} 760w, {img_site('sobre')} 1600w" sizes="(max-width: 900px) 100vw, 50vw" alt="Fachada noturna de empreendimento de alto padrão no Noroeste" loading="lazy" decoding="async"></figure>
    <div class="revelar">
      <span class="rotulo rotulo--linha">A Private</span>
      <h2 class="titulo">A frente de alto padrão da <em>Beiramar</em>.</h2>
      <div class="texto">
        <p>A Beiramar Private é dedicada à curadoria de imóveis exclusivos nas regiões mais valorizadas de Brasília. Atuamos com foco em localização, arquitetura, padrão construtivo e potencial de valorização.</p>
        <p>Nosso atendimento é consultivo, discreto e personalizado, conduzido por especialistas que entendem o tempo, o perfil e as expectativas de quem busca viver ou investir com segurança no alto padrão.</p>
      </div>
      <div class="pilares">
        <div><strong>Localização</strong><p>Endereços escassos, nos bairros que mais se valorizam no Plano Piloto.</p></div>
        <div><strong>Arquitetura</strong><p>Projetos assinados, com plantas amplas e identidade própria.</p></div>
        <div><strong>Padrão construtivo</strong><p>Incorporadoras de referência e acabamentos de alto padrão.</p></div>
        <div><strong>Valorização</strong><p>Imóveis escolhidos para morar bem e preservar patrimônio.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="secao secao--compacta" id="regioes" style="padding-top:0">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">Onde atuamos</span><h2 class="titulo" style="margin-top:22px">Dois endereços. <em>Nenhum</em> comum.</h2></div>
    </div>
    <div class="regioes">{regioes}</div>
  </div>
</section>

{numeros(r)}

<section class="secao" id="empreendimentos">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">Curadoria Private</span><h2 class="titulo" style="margin-top:22px">Empreendimentos <em>selecionados</em>.</h2></div>
      <div class="filtros" data-filtros="grade-emp" role="group" aria-label="Filtrar por região">
        <button class="filtro" type="button" data-filtro="todos" aria-pressed="true">Todos</button>
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
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">Como trabalhamos</span><h2 class="titulo" style="margin-top:22px">Menos opções. Mais <em>acerto</em>.</h2></div>
      <p class="lead">Um atendimento pensado para quem valoriza o próprio tempo.</p>
    </div>
    <div class="processo revelar">
      <div class="etapa"><span class="numero-serif">01</span><h3>Escuta</h3><p>Entendemos o seu momento, a sua rotina e o que o próximo endereço precisa entregar.</p></div>
      <div class="etapa"><span class="numero-serif">02</span><h3>Curadoria</h3><p>Selecionamos poucas opções, alinhadas ao seu perfil, com as informações de cada projeto.</p></div>
      <div class="etapa"><span class="numero-serif">03</span><h3>Visita privada</h3><p>Apresentamos os imóveis com hora marcada e atendimento exclusivo.</p></div>
      <div class="etapa"><span class="numero-serif">04</span><h3>Negociação</h3><p>Conduzimos proposta, documentação e fechamento com discrição e segurança.</p></div>
    </div>
  </div>
</section>

{contato(r, origem='Página inicial')}
</main>
"""
    html += rodape(r)
    salvar("", html)


def pagina_regiao(slug):
    reg = REGIOES[slug]
    r = "../"
    emps = [x for x in EMPS if x["regiao"] == slug]
    cards = "".join(card(r, x) for x in emps)
    difs = "".join(f'<div class="diferencial"><span class="numero-serif">{i:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>'
                   for i, (t, d) in enumerate(reg["diferenciais"], 1))
    intro = "".join(f"<p>{e(p)}</p>" for p in reg["intro"])
    html = head(r, f"{reg['nome']} | Beiramar Private",
                f"{reg['titulo']} {reg['titulo_destaque'].replace('<em>','').replace('</em>','')} {reg['subtitulo']}", f"{slug}/",
                imagem_og=img_site(reg["imagem"]))
    html += topo(r, slug)
    html += f"""<main>
<section class="hero">
  {foto_faixas(r + img_site(reg['imagem']), r + img_site(reg['imagem'], True), reg['nome'], 'hero__midia', eager=True)}
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Beiramar Private · Plano Piloto</span>
      <h1 class="display">{e(reg['titulo'])}<br>{reg['titulo_destaque']}</h1>
      <p class="lead">{e(reg['subtitulo'])}</p>
      <div class="hero__acoes">
        <a href="#empreendimentos" class="btn btn-claro">Ver empreendimentos {seta()}</a>
        <a href="#contato" class="btn btn-linha">Agendar visita</a>
      </div>
    </div>
    <div class="hero__rodape">
      <dl class="hero__dados"><div><dt>Empreendimentos</dt><dd>{len(emps)} selecionados</dd></div><div><dt>Região</dt><dd>{e(reg['nome'])}</dd></div></dl>
      <a href="#sobre" class="rolar"><span></span>Role</a>
    </div>
  </div>
</section>

<section class="secao" id="sobre">
  <div class="wrap">
    <div class="intro revelar">
      <div><span class="rotulo rotulo--linha">Sobre a região</span><h2 class="titulo" style="margin-top:22px">{e(reg['intro_titulo'])}</h2></div>
      <div class="texto">{intro}</div>
    </div>
    <div class="cabeca revelar" style="margin:clamp(72px,8vw,120px) 0 0"><span class="rotulo rotulo--linha">O diferencial {"do" if slug == "noroeste" else "da"} {e(reg['rotulo'])}</span></div>
    <div class="diferenciais revelar" style="margin-top:28px">{difs}</div>
  </div>
</section>

{numeros(r, com_link=False) if slug == "noroeste" else ""}

<section class="secao{" secao--2" if slug != "noroeste" else ""}" id="empreendimentos">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">Curadoria Private</span><h2 class="titulo" style="margin-top:22px">Empreendimentos {"no" if slug == "noroeste" else "na"} <em>{e(reg['rotulo'])}</em>.</h2></div>
    </div>
    <div class="grade">{cards}</div>
  </div>
</section>

{institucional(r)}
{contato(r, titulo=f'Receba a curadoria {"do" if slug == "noroeste" else "da"} <em>{e(reg["rotulo"])}</em>.', origem=f'Região {reg["nome"]}')}
</main>
"""
    html += rodape(r)
    salvar(slug, html)


def pagina_empreendimento(x, lp=False):
    reg = REGIOES[x["regiao"]]
    r = "../" if lp else "../../"
    caminho = "lpamazesunside" if lp else f"empreendimentos/{x['slug']}"
    desc = " ".join(x["descricao"])
    desc_meta = (f"{x['nome']}, {reg['nome']}: {x['metragem']}, {x['dormitorios']}. "
                 + desc[:110].rsplit(" ", 1)[0] + "…")
    texto = "".join(f"<p>{e(p)}</p>" for p in x["descricao"])
    assin = ""
    if x.get("incorporadora"):
        assin += f'<div><dt>Incorporação</dt><dd>{e(x["incorporadora"])}</dd></div>'
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
        fotos += (f'<button type="button" data-foto="{r}{img_emp(x["slug"], nome)}" aria-label="Ampliar foto {i} de {n}">'
                  f'<img src="{r}{img_emp(x["slug"], nome, p=True)}" alt="{e(x["nome"])}, foto {i}" loading="lazy" decoding="async"></button>')
    classe_gal = "galeria galeria--curta" if n <= 3 else "galeria"

    dados_hero = f'<div><dt>Metragem</dt><dd>{e(x["metragem"])}</dd></div><div><dt>Dormitórios</dt><dd>{e(x["dormitorios"])}</dd></div>'
    if x.get("status"):
        dados_hero += f'<div><dt>Status</dt><dd>{e(x["status"])}</dd></div>'
    elif x.get("incorporadora"):
        dados_hero += f'<div><dt>Incorporação</dt><dd>{e(x["incorporadora"])}</dd></div>'

    outros = [o for o in EMPS if o["slug"] != x["slug"]]
    outros.sort(key=lambda o: o["regiao"] != x["regiao"])
    trilho = "".join(card(r, o) for o in outros)
    outros_html = "" if lp else f"""<section class="secao" id="outros">
  <div class="wrap">
    <div class="cabeca revelar">
      <div class="cabeca__texto"><span class="rotulo rotulo--linha">Curadoria Private</span><h2 class="titulo" style="margin-top:22px">Outros <em>empreendimentos</em>.</h2></div>
      <div class="trilho-nav" data-trilho="trilho-outros"><button type="button" data-dir="-1" aria-label="Anteriores">{seta()}</button><button type="button" data-dir="1" aria-label="Próximos">{seta()}</button></div>
    </div>
    <div class="trilho" id="trilho-outros">{trilho}</div>
  </div>
</section>"""

    titulo_pagina = f"{x['nome']} | {reg['rotulo']} | Beiramar Private"
    html = head(r, titulo_pagina, desc_meta, caminho + "/", imagem_og=img_emp(x["slug"]),
                canonical=f"{DOMINIO}/empreendimentos/{x['slug']}/" if lp else None)
    html += topo(r, "", lp=lp)
    html += f"""<main>
<section class="hero emp-hero">
  {foto_faixas(r + img_emp(x['slug']), r + img_emp(x['slug'], p=True), f"{x['nome']}, {reg['nome']}", 'hero__midia', eager=True)}
  <div class="listras" aria-hidden="true"></div>
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Beiramar Private · {e(reg['nome'])}</span>
      <h1 class="display">{e(x['nome'])}</h1>
      <p class="chamada">{x['chamada']}</p>
      <div class="hero__acoes">
        <a href="#contato" class="btn btn-claro">Receber informações {seta()}</a>
        <a href="#galeria" class="btn btn-linha">Ver fotos</a>
      </div>
    </div>
    <div class="hero__rodape">
      <dl class="hero__dados">{dados_hero}</dl>
      <a href="#sobre" class="rolar"><span></span>Role</a>
    </div>
  </div>
</section>

<section class="secao" id="sobre">
  <div class="wrap ficha">
    <div class="revelar">
      <span class="rotulo rotulo--linha">Conheça o {e(x['nome'])}</span>
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
    <div class="cabeca revelar"><div class="cabeca__texto"><span class="rotulo rotulo--linha">Galeria</span><h2 class="titulo" style="margin-top:22px">Para <em>imaginar</em> a vida aqui.</h2></div></div>
    <div class="{classe_gal} revelar">{fotos}</div>
  </div>
</section>

<section class="secao" id="localizacao">
  <div class="wrap local">
    <div class="local__cartao moldura revelar">
      <span class="rotulo rotulo--linha">Localização</span>
      <p class="local__endereco">{e(x['endereco'])}</p>
      <a href="{e(x['mapa'])}" class="btn btn-linha" target="_blank" rel="noopener">Como chegar {seta()}</a>
    </div>
    <a class="revelar" href="{r}{x['regiao']}/" style="display:block">
      {foto_faixas(r + img_site(reg['imagem']), r + img_site(reg['imagem'], True), reg['nome'], 'local__foto', sizes='(max-width: 900px) 100vw, 50vw')}
      <span class="regiao__rodape" style="margin-top:18px;border-top:0;padding-top:0">Conhecer {"o" if x['regiao'] == 'noroeste' else "a"} {e(reg['rotulo'])} {seta()}</span>
    </a>
  </div>
</section>

{outros_html}
{institucional(r)}
{contato(r, titulo=f'Receba as informações do <em>{e(x["nome"])}</em>.', texto="Plantas, valores e disponibilidade atualizados. Um especialista Private entra em contato com você.", interesse=x['nome'], origem=("Landing page " if lp else "Página ") + x['nome'])}
</main>
{visor()}
"""
    html += rodape(r)
    salvar(caminho, html, sitemap=not lp)


def pagina_obrigado():
    r = "../"
    html = head(r, "Obrigado | Beiramar Private", "Recebemos o seu contato. Um especialista Beiramar Private vai falar com você em breve.", "obrigado/", noindex=True)
    html += topo(r)
    html += f"""<main>
<section class="hero" style="min-height:100svh">
  {foto_faixas(r + img_site('home-hero'), r + img_site('home-hero', True), '', 'hero__midia', eager=True)}
  <div class="wrap" style="position:relative;z-index:2">
    <div class="hero__conteudo">
      <span class="rotulo rotulo--linha">Contato recebido</span>
      <h1 class="display">Obrigado. Seu próximo endereço <em>começa aqui</em>.</h1>
      <p class="lead">Um especialista Beiramar Private vai entrar em contato com você em breve. Se preferir, continue agora pelo WhatsApp.</p>
      <div class="hero__acoes">
        <a href="{wa()}" data-whats-obrigado class="btn btn-claro" target="_blank" rel="noopener">Continuar no WhatsApp {seta()}</a>
        <a href="{r}" class="btn btn-linha">Voltar ao site</a>
      </div>
    </div>
  </div>
</section>
</main>
"""
    html += rodape(r)
    salvar("obrigado", html, sitemap=False)


POST_SLUG = "brasilia-onde-a-arquitetura-nao-apenas-abriga-ela-emociona"
POST_TITULO = "Brasília: onde a arquitetura não apenas abriga, ela emociona."
POST_RESUMO = "Do legado de Lúcio Costa e Niemeyer à Quadra 500 do Sudoeste: como a arquitetura de Brasília inspira o novo alto padrão."


def pagina_blog():
    r = "../"
    html = head(r, "Blog | Beiramar Private", "Arquitetura, bairros e o mercado de alto padrão em Brasília, pelo olhar da curadoria Beiramar Private.", "blog/")
    html += topo(r, "blog")
    html += f"""<main>
<section class="pagina-topo"><div class="wrap">
  <span class="rotulo rotulo--linha">Blog</span>
  <h1 class="titulo">Para escolher <em>onde morar</em> em Brasília.</h1>
  <p class="lead">Arquitetura, bairros e o mercado de alto padrão, pelo olhar da curadoria Private.</p>
</div></section>
<section class="secao secao--compacta"><div class="wrap">
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
{contato(r, origem='Blog')}
</main>
"""
    html += rodape(r)
    salvar("blog", html)

    r = "../../"
    corpo = (RAIZ / "dados" / "blog" / f"{POST_SLUG}.html").read_text(encoding="utf-8")
    html = head(r, f"{POST_TITULO} | Beiramar Private", POST_RESUMO, f"blog/{POST_SLUG}/", imagem_og=img_site("quadra-500-b"))
    html += topo(r, "blog")
    html += f"""<main>
<section class="pagina-topo"><div class="wrap">
  <a href="../" class="rotulo rotulo--linha">Blog</a>
  <h1 class="titulo">Brasília: onde a arquitetura não apenas abriga, <em>ela emociona</em>.</h1>
  <p class="lead">{e(POST_RESUMO)}</p>
</div></section>
<section class="secao secao--compacta"><div class="wrap">
  {foto_faixas(r + img_site('quadra-500-b'), r + img_site('quadra-500-b', True), 'Vista aérea da Quadra 500 do Sudoeste', 'faixas--base', sizes='100vw').replace('class="faixas faixas--base"', 'class="faixas faixas--base" style="aspect-ratio:21/9;margin-bottom:clamp(48px,6vw,80px)"')}
  <article class="artigo">{corpo}</article>
</div></section>
{contato(r, titulo='Conheça a <em>Quadra 500</em> com a curadoria Private.', interesse='', origem='Blog: ' + POST_TITULO)}
</main>
"""
    html += rodape(r)
    salvar(f"blog/{POST_SLUG}", html)


def pagina_privacidade():
    r = "../"
    corpo = (RAIZ / "dados" / "privacidade.html").read_text(encoding="utf-8")
    html = head(r, "Privacidade e cookies | Beiramar Private", "Como a Beiramar Private trata os dados pessoais de quem visita o site e entra em contato, conforme a LGPD.", "privacidade/")
    html += topo(r)
    html += f"""<main>
<section class="pagina-topo"><div class="wrap">
  <span class="rotulo rotulo--linha">Documentos legais</span>
  <h1 class="titulo">Privacidade e <em>cookies</em>.</h1>
  <p class="lead">Como tratamos os dados pessoais de quem visita este site e entra em contato conosco, conforme a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).</p>
</div></section>
<section class="secao secao--compacta"><div class="wrap"><article class="artigo legal">{corpo}</article></div></section>
</main>
"""
    html += rodape(r)
    salvar("privacidade", html)


def redirecionar(antigo, novo_rel, novo_abs):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>Beiramar Private</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{novo_abs}">
<meta http-equiv="refresh" content="0; url={novo_rel}">
<script>location.replace("{novo_rel}" + location.search + location.hash);</script>
</head><body style="background:#131415;color:#fff;font-family:sans-serif">
<p>Esta página mudou de endereço: <a href="{novo_rel}" style="color:#fff">{novo_abs}</a></p>
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
    html += topo(r)
    html += f"""<main>
<section class="pagina-topo" style="min-height:80svh;display:flex;align-items:center"><div class="wrap">
  <span class="rotulo rotulo--linha">Erro 404</span>
  <h1 class="titulo">Este endereço <em>não existe</em>.</h1>
  <p class="lead">Mas temos outros que valem a visita.</p>
  <div class="hero__acoes"><a href="/" class="btn btn-claro">Ir para o início {seta()}</a><a href="/#empreendimentos" class="btn btn-linha">Ver empreendimentos</a></div>
</div></section>
</main>
"""
    html += rodape(r)
    (RAIZ / "404.html").write_text(html, encoding="utf-8")


def main():
    # limpa redirecionamentos antigos gerados anteriormente
    reg_arquivo = RAIZ / "dados" / ".redirecionamentos"
    if reg_arquivo.exists():
        for p in reg_arquivo.read_text().split():
            alvo = RAIZ / p
            if alvo.is_dir() and (alvo / "index.html").exists() and "location.replace" in (alvo / "index.html").read_text():
                shutil.rmtree(alvo)

    pagina_inicio()
    for slug in REGIOES:
        pagina_regiao(slug)
    for x in EMPS:
        pagina_empreendimento(x)
    if "amaze-sunside" in EMP:
        pagina_empreendimento(EMP["amaze-sunside"], lp=True)
    pagina_obrigado()
    pagina_blog()
    pagina_privacidade()
    pagina_404()

    # endereços antigos do WordPress → novos
    redirs = []
    for x in EMPS:
        for antigo in x.get("antigos", []):
            redirs.append(redirecionar(antigo, f"../empreendimentos/{x['slug']}/", f"{DOMINIO}/empreendimentos/{x['slug']}/"))
    redirs.append(redirecionar("quadra500", "../quadra-500/", f"{DOMINIO}/quadra-500/"))
    redirs.append(redirecionar(POST_SLUG, f"../blog/{POST_SLUG}/", f"{DOMINIO}/blog/{POST_SLUG}/"))
    reg_arquivo.write_text("\n".join(redirs) + "\n")

    urls = "".join(f"  <url><loc>{DOMINIO}/{c}</loc></url>\n" for c in geradas)
    (RAIZ / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (RAIZ / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (RAIZ / ".nojekyll").write_text("")
    print(f"{len(geradas)} páginas geradas, {len(redirs)} redirecionamentos.")


if __name__ == "__main__":
    main()
