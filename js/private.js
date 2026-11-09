// Beiramar Private — comportamento das páginas
// Menu do celular, cabeçalho ao rolar, animações de entrada, filtros, carrossel,
// galeria com visualizador e formulário de contato (registra o lead por e-mail e
// leva para a página de obrigado, que oferece seguir a conversa pelo WhatsApp).
(function () {
  var doc = document.documentElement;

  /* ---------- cabeçalho e menu ---------- */
  var topo = document.getElementById('topo');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (topo) {
    var onScroll = function () { topo.classList.toggle('rolado', window.scrollY > 24); };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }
  if (topo && toggle && nav) {
    var iconeAbrir = toggle.innerHTML;
    var iconeFechar = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    var setMenu = function (aberto) {
      topo.classList.toggle('aberto', aberto);
      doc.classList.toggle('menu-aberto', aberto);
      toggle.innerHTML = aberto ? iconeFechar : iconeAbrir;
      toggle.setAttribute('aria-expanded', String(aberto));
      toggle.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
    };
    toggle.addEventListener('click', function () { setMenu(!topo.classList.contains('aberto')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && topo.classList.contains('aberto')) { setMenu(false); toggle.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 960) setMenu(false); });
    window.addEventListener('pageshow', function () { setMenu(false); });
  }

  /* ---------- animações de entrada ---------- */
  var revelar = document.querySelectorAll('.revelar');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('visivel'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revelar.forEach(function (el) { io.observe(el); });
  } else revelar.forEach(function (el) { el.classList.add('visivel'); });

  /* ---------- filtros por região ---------- */
  document.querySelectorAll('[data-filtros]').forEach(function (grupo) {
    var alvo = document.getElementById(grupo.getAttribute('data-filtros'));
    if (!alvo) return;
    grupo.addEventListener('click', function (e) {
      var b = e.target.closest('.filtro'); if (!b) return;
      grupo.querySelectorAll('.filtro').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var f = b.getAttribute('data-filtro');
      alvo.querySelectorAll('.card').forEach(function (c) { c.hidden = f !== 'todos' && c.getAttribute('data-regiao') !== f; });
    });
  });

  /* ---------- carrossel ---------- */
  document.querySelectorAll('[data-trilho]').forEach(function (navT) {
    var trilho = document.getElementById(navT.getAttribute('data-trilho'));
    if (!trilho) return;
    var passo = function () { var c = trilho.firstElementChild; return c ? c.getBoundingClientRect().width + 28 : 320; };
    navT.querySelector('[data-dir="-1"]').addEventListener('click', function () { trilho.scrollBy({ left: -passo(), behavior: 'smooth' }); });
    navT.querySelector('[data-dir="1"]').addEventListener('click', function () { trilho.scrollBy({ left: passo(), behavior: 'smooth' }); });
  });

  /* ---------- galeria + visualizador ---------- */
  var visor = document.getElementById('visor');
  if (visor) {
    var fotos = Array.prototype.slice.call(document.querySelectorAll('[data-foto]'));
    var img = visor.querySelector('img'), cont = visor.querySelector('.visor__contador');
    var atual = 0, origem = null;
    var mostrar = function (i) {
      atual = (i + fotos.length) % fotos.length;
      img.src = fotos[atual].getAttribute('data-foto');
      img.alt = fotos[atual].querySelector('img') ? fotos[atual].querySelector('img').alt : '';
      cont.textContent = (atual + 1) + ' / ' + fotos.length;
    };
    var abrir = function (i) { origem = document.activeElement; mostrar(i); visor.classList.add('aberto'); doc.classList.add('menu-aberto'); visor.querySelector('.visor__fechar').focus(); };
    var fechar = function () { visor.classList.remove('aberto'); doc.classList.remove('menu-aberto'); if (origem) origem.focus(); };
    fotos.forEach(function (f, i) { f.addEventListener('click', function () { abrir(i); }); });
    visor.querySelector('.visor__fechar').addEventListener('click', fechar);
    visor.querySelector('.visor__ant').addEventListener('click', function () { mostrar(atual - 1); });
    visor.querySelector('.visor__prox').addEventListener('click', function () { mostrar(atual + 1); });
    visor.addEventListener('click', function (e) { if (e.target === visor) fechar(); });
    document.addEventListener('keydown', function (e) {
      if (!visor.classList.contains('aberto')) return;
      if (e.key === 'Escape') fechar();
      else if (e.key === 'ArrowLeft') mostrar(atual - 1);
      else if (e.key === 'ArrowRight') mostrar(atual + 1);
    });
    var x0 = null;
    visor.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    visor.addEventListener('touchend', function (e) {
      if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 50) mostrar(atual + (dx < 0 ? 1 : -1));
    });
  }

  /* ---------- formulário de contato ---------- */
  // Máscara simples de telefone: (61) 99999-9999
  document.querySelectorAll('input[type="tel"]').forEach(function (inp) {
    inp.addEventListener('input', function () {
      var d = inp.value.replace(/\D/g, '').slice(0, 11);
      var r = d;
      if (d.length > 2) r = '(' + d.slice(0, 2) + ') ' + d.slice(2);
      if (d.length > 7) r = '(' + d.slice(0, 2) + ') ' + d.slice(2, d.length - 4) + '-' + d.slice(-4);
      inp.value = r;
    });
  });

  document.querySelectorAll('form[data-lead]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var btn = form.querySelector('button[type="submit"]');
      var status = form.querySelector('.form__status');
      var original = btn.innerHTML;
      var dados = new FormData(form);
      var interesse = dados.get('interesse') || 'Beiramar Private';
      dados.set('subject', 'Novo contato · Beiramar Private · ' + interesse);
      dados.set('pagina', location.href);

      // Mensagem pronta para seguir a conversa no WhatsApp
      var partes = ['Olá! Sou ' + (dados.get('nome') || '') + '.', 'Tenho interesse em: ' + interesse + '.'];
      if (dados.get('quartos')) partes.push('Busco: ' + dados.get('quartos') + '.');
      if (dados.get('mensagem')) partes.push(dados.get('mensagem'));
      var msg = partes.join(' ');

      btn.disabled = true; btn.textContent = 'Enviando...';
      if (status) status.textContent = '';
      fetch(form.action, { method: 'POST', body: dados, headers: { Accept: 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error('falha'); return r.json(); })
        .then(function () {
          if (window.gtag) window.gtag('event', 'generate_lead', { interesse: interesse });
          var destino = form.getAttribute('data-obrigado') || 'obrigado/';
          location.href = destino + '?msg=' + encodeURIComponent(msg);
        })
        .catch(function () {
          btn.disabled = false; btn.innerHTML = original;
          if (status) status.innerHTML = 'Não conseguimos enviar agora. Tente de novo ou <a href="https://wa.me/556131426671?text=' + encodeURIComponent(msg) + '" target="_blank" rel="noopener" style="text-decoration:underline">fale pelo WhatsApp</a>.';
        });
    });
  });

  /* ---------- página de obrigado: botão do WhatsApp com a mensagem do formulário ---------- */
  var botaoWhats = document.querySelector('[data-whats-obrigado]');
  if (botaoWhats) {
    var m = new URLSearchParams(location.search).get('msg');
    if (m) botaoWhats.href = 'https://wa.me/556131426671?text=' + encodeURIComponent(m);
  }
})();
