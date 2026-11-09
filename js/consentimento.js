// Consentimento de cookies (LGPD) — Beiramar Private (mesmo componente do site do Grupo Beiramar)
// - Na primeira visita, mostra o aviso com "Aceitar", "Rejeitar" e "Personalizar".
// - Guarda a escolha por 12 meses no navegador (localStorage "gb-consent").
// - Google Analytics e Microsoft Clarity SÓ carregam para quem autorizou "Análise".
//   Os códigos das ferramentas ficam abaixo (GA_ID e CLARITY_ID). Não cole os scripts delas no <head>.
//   Enquanto os dois estiverem vazios, nenhuma ferramenta é carregada e o aviso não aparece.
// - Qualquer elemento com o atributo data-cookie-preferences abre o painel de preferências.
// - Ao incluir uma nova ferramenta, liste-a também na tabela de cookies de privacidade.html.
(function () {
  var KEY = 'bp-consent';
  var VERSION = 1;
  var MAX_AGE = 365 * 24 * 60 * 60 * 1000;
  var GA_ID = '';       // ex.: 'G-XXXXXXXXXX' (propriedade do Google Analytics da Private)
  var CLARITY_ID = '';  // ex.: 'abcd1234ef' (projeto do Microsoft Clarity da Private)
  var SCRIPT = document.currentScript && document.currentScript.src;
  var BASE = SCRIPT ? SCRIPT.replace(/js\/consentimento\.js.*$/, '') : '/';
  var POLICY = BASE + 'privacidade/#cookies';
  var ATIVO = !!(GA_ID || CLARITY_ID);
  var loaded = false;

  function read() {
    try {
      var c = JSON.parse(localStorage.getItem(KEY));
      if (c && c.v === VERSION && Date.now() - c.date < MAX_AGE) return c;
    } catch (e) {}
    return null;
  }

  function save(analytics) {
    var c = { v: VERSION, date: Date.now(), necessary: true, analytics: !!analytics };
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
    return c;
  }

  // Carrega Google Analytics e Microsoft Clarity (somente após consentimento)
  function loadAnalytics() {
    if (loaded || !ATIVO) return;
    loaded = true;

    if (GA_ID) {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', GA_ID);
      var ga = document.createElement('script');
      ga.async = true;
      ga.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
      document.head.appendChild(ga);
    }
    if (!CLARITY_ID) return;

    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_ID);
    window.clarity('consent');
  }

  // Apaga os cookies de análise quando o visitante retira a autorização
  function clearAnalytics() {
    var host = location.hostname;
    var domains = ['', host, '.' + host, '.' + host.replace(/^www\./, '')];
    document.cookie.split(';').forEach(function (part) {
      var name = part.split('=')[0].trim();
      if (!/^(_ga|_gid|_gat|_clck|_clsk)/.test(name)) return;
      domains.forEach(function (d) {
        document.cookie = name + '=; Max-Age=0; path=/' + (d ? '; domain=' + d : '');
      });
    });
  }

  var banner, dialog, toast;

  function build() {
    banner = document.createElement('div');
    banner.className = 'gb-cookie';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Sua privacidade');
    banner.hidden = true;
    banner.innerHTML =
      '<p class="gb-cookie__eyebrow">Sua privacidade</p>' +
      '<p class="gb-cookie__text">Usamos cookies necessários para o site funcionar. Com a sua permissão, também usamos cookies de análise para entender como o site é usado e melhorá-lo. ' +
      '<a href="' + POLICY + '">Saiba mais</a></p>' +
      '<div class="gb-cookie__actions">' +
      '<button type="button" class="gb-btn gb-btn--link" data-cookie-action="customize">Personalizar</button>' +
      '<button type="button" class="gb-btn gb-btn--outline" data-cookie-action="reject">Rejeitar</button>' +
      '<button type="button" class="gb-btn gb-btn--solid" data-cookie-action="accept">Aceitar</button>' +
      '</div>';

    dialog = document.createElement('dialog');
    dialog.className = 'gb-cookie-dialog';
    dialog.setAttribute('aria-labelledby', 'gb-cookie-title');
    dialog.innerHTML =
      '<form method="dialog" class="gb-cookie-dialog__form">' +
      '<div class="gb-cookie-dialog__head"><div><p class="gb-cookie__eyebrow">Beiramar Private</p>' +
      '<h2 id="gb-cookie-title">Preferências de cookies</h2></div>' +
      '<button type="button" class="gb-cookie-close" data-cookie-action="close" aria-label="Fechar">' +
      '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg></button></div>' +
      '<p class="gb-cookie-dialog__intro">Escolha o que o site pode usar. Os cookies necessários ficam sempre ativos.</p>' +
      '<div class="gb-cookie-row"><div><strong>Necessários</strong><p>Funcionamento e segurança do site e o registro das suas escolhas de cookies.</p></div>' +
      '<span class="gb-cookie-always">Sempre ativos</span></div>' +
      '<div class="gb-cookie-row"><div><strong>Análise</strong><p>Google Analytics e Microsoft Clarity: mostram, de forma agregada, como o site é usado para que possamos melhorá-lo.</p></div>' +
      '<label class="gb-switch"><input type="checkbox" name="analytics" aria-label="Cookies de análise"><span aria-hidden="true"></span></label></div>' +
      '<p class="gb-cookie-dialog__link"><a href="' + POLICY + '">Política de Privacidade e Cookies</a></p>' +
      '<div class="gb-cookie-dialog__actions">' +
      '<button type="button" class="gb-btn gb-btn--outline" data-cookie-action="reject">Rejeitar</button>' +
      '<button type="button" class="gb-btn gb-btn--outline" data-cookie-action="save">Salvar escolha</button>' +
      '<button type="button" class="gb-btn gb-btn--solid" data-cookie-action="accept">Aceitar</button>' +
      '</div></form>';

    toast = document.createElement('div');
    toast.className = 'gb-cookie-toast';
    toast.setAttribute('role', 'status');
    toast.textContent = 'Preferências salvas.';

    document.body.appendChild(banner);
    document.body.appendChild(dialog);
    document.body.appendChild(toast);
  }

  function showBanner(show) { banner.hidden = !show; }

  function open() {
    var c = read();
    dialog.querySelector('input[name="analytics"]').checked = !!(c && c.analytics);
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
  }

  function close() {
    if (typeof dialog.close === 'function') dialog.close(); else dialog.removeAttribute('open');
  }

  function done(analytics) {
    var before = read();
    save(analytics);
    showBanner(false);
    close();
    if (analytics) {
      loadAnalytics();
    } else if (loaded || (before && before.analytics)) {
      // Autorização retirada: apaga os cookies e recarrega para encerrar as ferramentas já ativas
      clearAnalytics();
      location.reload();
      return;
    }
    toast.classList.add('is-visible');
    setTimeout(function () { toast.classList.remove('is-visible'); }, 2600);
  }

  function init() {
    build();
    var current = read();
    if (current) { if (current.analytics) loadAnalytics(); } else if (ATIVO) showBanner(true);

    document.addEventListener('click', function (e) {
      var opener = e.target.closest('[data-cookie-preferences]');
      if (opener) { e.preventDefault(); open(); return; }
      var btn = e.target.closest('[data-cookie-action]');
      if (!btn) return;
      var action = btn.dataset.cookieAction;
      if (action === 'accept') done(true);
      else if (action === 'reject') done(false);
      else if (action === 'customize') open();
      else if (action === 'close') close();
      else if (action === 'save') done(dialog.querySelector('input[name="analytics"]').checked);
    });
    dialog.addEventListener('click', function (e) { if (e.target === dialog) close(); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  window.GBConsent = { get: read, open: function () { if (dialog) open(); } };
})();
