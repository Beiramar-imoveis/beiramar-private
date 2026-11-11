// Beiramar Private — comportamento das páginas (português e inglês)
// Menu do celular (mesmo modelo dos sites do Grupo Beiramar e da BRM Asset), cabeçalho ao rolar,
// animações de entrada, filtros, carrossel, galeria com visualizador e formulário de contato
// (registra o lead por e-mail e leva para a página de obrigado, que oferece seguir no WhatsApp).
(function () {
  var doc = document.documentElement;
  var EN = (doc.lang || '').toLowerCase().indexOf('en') === 0;
  var T = EN ? {
    abrir: 'Open menu', fechar: 'Close menu', enviando: 'Sending...',
    erro: 'We could not send your message right now. Please try again or ',
    erroLink: 'chat on WhatsApp', ola: 'Hello! My name is ', interesse: 'I am interested in: ', busca: 'Looking for: '
  } : {
    abrir: 'Abrir menu', fechar: 'Fechar menu', enviando: 'Enviando...',
    erro: 'Não conseguimos enviar agora. Tente de novo ou ',
    erroLink: 'fale pelo WhatsApp', ola: 'Olá! Sou ', interesse: 'Tenho interesse em: ', busca: 'Busco: '
  };
  var WHATS = 'https://wa.me/556132621200?text=';

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
    var iconeFechar = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    var setMenu = function (aberto) {
      topo.classList.toggle('aberto', aberto);
      doc.classList.toggle('menu-aberto', aberto);
      toggle.innerHTML = aberto ? iconeFechar : iconeAbrir;
      toggle.setAttribute('aria-expanded', String(aberto));
      toggle.setAttribute('aria-label', aberto ? T.fechar : T.abrir);
    };
    toggle.addEventListener('click', function () { setMenu(!topo.classList.contains('aberto')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && topo.classList.contains('aberto')) { setMenu(false); toggle.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 960 && topo.classList.contains('aberto')) setMenu(false); });
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
    var ant = navT.querySelector('[data-dir="-1"]'), prox = navT.querySelector('[data-dir="1"]');
    var barra = trilho.parentNode.querySelector('.trilho-progresso span');
    var cards = function () { return Array.prototype.slice.call(trilho.children); };

    // posição de cada card relativa ao início do trilho
    var posicoes = function () {
      var base = trilho.getBoundingClientRect().left - trilho.scrollLeft;
      return cards().map(function (c) { return Math.round(c.getBoundingClientRect().left - base); });
    };
    var maximo = function () { return trilho.scrollWidth - trilho.clientWidth; };
    var irPara = function (dir) {
      var pos = posicoes(), x = trilho.scrollLeft, alvo;
      if (dir > 0) alvo = pos.filter(function (p) { return p > x + 4; })[0];
      else alvo = pos.filter(function (p) { return p < x - 4; }).pop();
      if (alvo === undefined) alvo = dir > 0 ? maximo() : 0;
      trilho.scrollTo({ left: Math.min(alvo, maximo()), behavior: 'smooth' });
    };
    var atualizar = function () {
      var max = maximo(), x = trilho.scrollLeft;
      ant.disabled = x <= 4;
      prox.disabled = x >= max - 4;
      if (barra) {
        var visivel = trilho.clientWidth / trilho.scrollWidth;
        barra.style.width = (visivel * 100) + '%';
        barra.style.left = (max > 0 ? (x / max) * (1 - visivel) * 100 : 0) + '%';
      }
    };
    ant.addEventListener('click', function () { irPara(-1); });
    prox.addEventListener('click', function () { irPara(1); });
    trilho.addEventListener('scroll', function () { window.requestAnimationFrame(atualizar); }, { passive: true });
    window.addEventListener('resize', atualizar);
    trilho.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); irPara(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); irPara(-1); }
    });

    // arrastar com o mouse (no toque, a rolagem nativa já funciona)
    var arrasto = null;
    trilho.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      arrasto = { x: e.clientX, inicio: trilho.scrollLeft, moveu: false };
    });
    window.addEventListener('pointermove', function (e) {
      if (!arrasto) return;
      var dx = e.clientX - arrasto.x;
      if (!arrasto.moveu && Math.abs(dx) > 6) { arrasto.moveu = true; trilho.classList.add('arrastando'); }
      if (arrasto.moveu) trilho.scrollLeft = arrasto.inicio - dx;
    });
    window.addEventListener('pointerup', function () {
      if (!arrasto) return;
      var moveu = arrasto.moveu, dx = trilho.scrollLeft - arrasto.inicio;
      arrasto = null;
      if (!moveu) return;
      trilho.classList.remove('arrastando');
      // encaixa no card mais próximo na direção do arrasto
      var pos = posicoes(), x = trilho.scrollLeft;
      var alvo = dx > 0 ? pos.filter(function (p) { return p >= x - 4; })[0] : pos.filter(function (p) { return p <= x + 4; }).pop();
      trilho.scrollTo({ left: Math.min(alvo === undefined ? x : alvo, maximo()), behavior: 'smooth' });
      // evita abrir o card ao soltar o mouse depois de arrastar
      var bloq = function (ev) { ev.preventDefault(); ev.stopPropagation(); };
      trilho.addEventListener('click', bloq, true);
      setTimeout(function () { trilho.removeEventListener('click', bloq, true); }, 60);
    });
    atualizar();
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

  /* ---------- vídeo: troca a capa pelo player do YouTube só quando o visitante clica ---------- */
  document.querySelectorAll('.video__capa').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(btn.getAttribute('data-video')) + '?autoplay=1&rel=0&modestbranding=1';
      f.title = btn.getAttribute('data-titulo') || 'Vídeo';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      btn.parentNode.replaceChild(f, btn);
    });
  });

  /* ---------- formulário de contato ---------- */
  // Máscara de telefone brasileiro, só nos campos marcados (a versão em inglês aceita números internacionais)
  document.querySelectorAll('input[data-mascara="br"]').forEach(function (inp) {
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
      dados.set('subject', 'Novo contato · Beiramar Private' + (EN ? ' (EN)' : '') + ' · ' + interesse);
      dados.set('pagina', location.href);

      // Mensagem pronta para seguir a conversa no WhatsApp
      var partes = [T.ola + (dados.get('nome') || '') + '.', T.interesse + interesse + '.'];
      if (dados.get('quartos')) partes.push(T.busca + dados.get('quartos') + '.');
      if (dados.get('mensagem')) partes.push(dados.get('mensagem'));
      var msg = partes.join(' ');

      btn.disabled = true; btn.textContent = T.enviando;
      if (status) status.textContent = '';
      fetch(form.action, { method: 'POST', body: dados, headers: { Accept: 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error('falha'); return r.json(); })
        .then(function () {
          if (window.gtag) window.gtag('event', 'generate_lead', { interesse: interesse, idioma: EN ? 'en' : 'pt' });
          var destino = form.getAttribute('data-obrigado') || 'obrigado/';
          location.href = destino + '?msg=' + encodeURIComponent(msg);
        })
        .catch(function () {
          btn.disabled = false; btn.innerHTML = original;
          if (status) status.innerHTML = T.erro + '<a href="' + WHATS + encodeURIComponent(msg) + '" target="_blank" rel="noopener" style="text-decoration:underline">' + T.erroLink + '</a>.';
        });
    });
  });

  /* ---------- barra de navegação do empreendimento: destaca a seção em leitura ---------- */
  var subnav = document.querySelector('.subnav');
  if (subnav && 'IntersectionObserver' in window) {
    var links = Array.prototype.slice.call(subnav.querySelectorAll('.subnav__links a'));
    var faixa = subnav.querySelector('.subnav__links');
    var spy = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (l) {
          var ativo = l.getAttribute('href') === '#' + en.target.id;
          l.classList.toggle('ativo', ativo);
          if (ativo && faixa.scrollWidth > faixa.clientWidth) faixa.scrollTo({ left: l.offsetLeft - 20, behavior: 'smooth' });
        });
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    links.forEach(function (l) { var alvo = document.querySelector(l.getAttribute('href')); if (alvo) spy.observe(alvo); });
  }

  /* ---------- página de obrigado: botão do WhatsApp com a mensagem do formulário ---------- */
  var botaoWhats = document.querySelector('[data-whats-obrigado]');
  if (botaoWhats) {
    var m = new URLSearchParams(location.search).get('msg');
    if (m) botaoWhats.href = WHATS + encodeURIComponent(m);
  }
})();
