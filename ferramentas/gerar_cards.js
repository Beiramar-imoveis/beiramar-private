/*
 * Gera os cards de compartilhamento (og:image, 1200 x 630) de todas as páginas.
 * São as imagens que aparecem quando um link do site é colado no WhatsApp,
 * no LinkedIn, no Facebook etc.
 *
 * Uso (na raiz do repositório):
 *   python3 ferramentas/gerar_site.py     → atualiza dados/cards-compartilhamento.json
 *   node ferramentas/gerar_cards.js       → gera imagens/compartilhar/*.jpg
 *
 * Requer o Playwright (npm i -D playwright, se não estiver instalado).
 * O layout usa o próprio css/private.css, com DM Sans, Didot Italic e o degradê em faixas.
 */
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..');
const url = (rel) => pathToFileURL(path.join(RAIZ, rel)).href;
const cards = JSON.parse(fs.readFileSync(path.join(RAIZ, 'dados/cards-compartilhamento.json'), 'utf8'));
const SAIDA = path.join(RAIZ, 'imagens/compartilhar');
fs.mkdirSync(SAIDA, { recursive: true });

const pagina = (c) => `<!DOCTYPE html><html lang="${c.idioma === 'en' ? 'en' : 'pt-BR'}"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=block" rel="stylesheet">
<link rel="stylesheet" href="${url('css/private.css')}">
<style>
  @font-face{font-family:"Didot Private";src:url("${url('fontes/didot-italic.woff2')}") format("woff2");font-style:italic;font-display:block}
  html,body{width:1200px;height:630px;margin:0;overflow:hidden;background:var(--preto);color:var(--branco)}
  .og{position:relative;width:1200px;height:630px}
  .og .faixas{position:absolute;top:0;right:0;bottom:0;width:780px}
  .og .faixas img{--f1:9%;--f2:18%;--f3:27%;--f4:36%;--f5:45%}
  .og__sombra{position:absolute;inset:0;background:linear-gradient(90deg,rgba(19,20,21,.92) 0,rgba(19,20,21,.55) 52%,rgba(19,20,21,0) 78%),
    linear-gradient(0deg,rgba(19,20,21,.6) 0,rgba(19,20,21,0) 45%)}
  .og__logo{position:absolute;top:52px;left:72px;height:80px;width:auto}
  .og__texto{position:absolute;left:72px;bottom:64px;width:700px}
  .og .rotulo{font-size:14px;letter-spacing:.32em;color:var(--branco);opacity:.85;margin-bottom:22px}
  .og__titulo{font-size:58px;font-weight:300;line-height:1.06;letter-spacing:-.022em;margin:0}
  .og__titulo--nome{text-transform:uppercase;font-weight:500;letter-spacing:-.01em;font-size:84px;line-height:1}
  .og__sub{font-size:27px;font-weight:300;line-height:1.3;margin-top:18px;max-width:640px}
  .og__meta{margin-top:24px;padding-top:18px;border-top:1px solid rgba(253,253,253,.28);font-size:15px;letter-spacing:.2em;text-transform:uppercase;font-weight:500;opacity:.85}
</style></head><body>
<div class="og">
  <div class="faixas"><img src="${url(c.foto)}" alt=""></div>
  <div class="og__sombra"></div>
  <img class="og__logo" src="${url('imagens/site/logo-beiramar-private.png')}" alt="">
  <div class="og__texto">
    <span class="rotulo rotulo--linha">${c.rotulo}</span>
    <h1 class="og__titulo${c.sub && c.meta ? ' og__titulo--nome' : ''}">${c.titulo}</h1>
    ${c.sub ? `<p class="og__sub">${c.sub}</p>` : ''}
    ${c.meta ? `<div class="og__meta">${c.meta}</div>` : ''}
  </div>
</div></body></html>`;

(async () => {
  const navegador = await chromium.launch();
  const aba = await navegador.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  const tmp = path.join(SAIDA, '.card.html');
  for (const c of cards) {
    fs.writeFileSync(tmp, pagina(c));
    await aba.goto(pathToFileURL(tmp).href, { waitUntil: 'networkidle' });
    await aba.evaluate(() => document.fonts.ready);
    await aba.screenshot({ path: path.join(SAIDA, `${c.arquivo}.jpg`), type: 'jpeg', quality: 84 });
  }
  fs.unlinkSync(tmp);
  // remove cards de páginas que não existem mais
  const validos = new Set(cards.map((c) => `${c.arquivo}.jpg`));
  for (const f of fs.readdirSync(SAIDA)) if (f.endsWith('.jpg') && !validos.has(f)) fs.unlinkSync(path.join(SAIDA, f));
  await navegador.close();
  console.log(`${cards.length} cards gerados em imagens/compartilhar/`);
})();
