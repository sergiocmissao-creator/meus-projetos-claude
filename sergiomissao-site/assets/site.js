(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const button = document.getElementById('menu-button');
  const nav = document.getElementById('nav');
  function closeMenu() { nav?.classList.remove('open'); button?.setAttribute('aria-expanded', 'false'); }
  button?.addEventListener('click', () => { const open = nav.classList.toggle('open'); button.setAttribute('aria-expanded', String(open)); if (open) nav.querySelector('a')?.focus(); });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav?.classList.contains('open')) { closeMenu(); button.focus(); } });
  const year = document.getElementById('ano');
  if (year) year.textContent = new Date().getFullYear();

  // Links antigos de campanha e de artigos continuam chegando ao destino certo.
  const legacy = {
    mentoria:'/mentoria/', avaliacao:'/mentoria/#avaliacao', entrevistas:'/mentoria/#entrevistas',
    'preparacao-entrevistas':'/mentoria/#entrevistas', consultoria:'/consultoria/', treinamentos:'/treinamentos/',
    palestras:'/palestras/', 'palestras-detalhe':'/palestras/', 'palestra-burnout':'/palestras/burnout-sem-lados/',
    'palestra-desaprenda':'/palestras/desaprenda-a-liderar/', 'palestra-dono':'/palestras/a-experiencia-do-dono/',
    sobre:'/sobre/', contato:'/contato/', artigos:'/artigos/', posts:'/posts/', ladob:'/artigos/', cooperativas:'/cooperativismo/',
    duvidas:'/contato/#duvidas', 'como-funciona':'/contato/', destaques:'/palestras/burnout-sem-lados/'
  };
  function restoreLegacyLink() {
    if (!['/', '/index.html'].includes(location.pathname)) return;
    const hash = location.hash.slice(1);
    if (legacy[hash]) location.replace(legacy[hash]);
    else if (/^artigo-[a-z0-9-]+$/.test(hash)) location.replace('/artigos/' + hash.slice(7) + '/');
    else if (hash === 'topo') window.scrollTo(0,0);
  }
  restoreLegacyLink();
  window.addEventListener('hashchange', restoreLegacyLink);

  // Ficha das palestras: imprimir ou salvar em PDF.
  document.querySelectorAll('.js-print').forEach(b => { b.hidden = false; b.addEventListener('click', () => window.print()); });

  // Conteúdos: filtro por texto, formato e tema. Sem JS, a lista completa continua visível.
  const list = document.getElementById('lista');
  const filters = document.querySelector('.filters');
  if (list && filters) {
    filters.hidden = false;
    const q = document.getElementById('busca'), fmt = document.getElementById('f-formato'), tema = document.getElementById('f-tema');
    const count = document.querySelector('.c-count'), empty = document.querySelector('.c-empty');
    const items = [...list.querySelectorAll('.c-item')];
    const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    items.forEach(li => { li.dataset.busca = norm(li.textContent); });
    const params = new URLSearchParams(location.search);
    if (params.get('q')) q.value = params.get('q');
    if (params.get('tema')) tema.value = params.get('tema');
    if (params.get('formato')) fmt.value = params.get('formato');
    function apply() {
      const words = norm(q.value.trim()).split(/\s+/).filter(Boolean);
      let shown = 0;
      items.forEach(li => {
        const ok = (!fmt.value || li.dataset.formato === fmt.value) && (!tema.value || li.dataset.tema === tema.value) && words.every(w => li.dataset.busca.includes(w));
        li.hidden = !ok; if (ok) shown++;
      });
      count.textContent = shown === items.length ? `${items.length} conteúdos` : `${shown} de ${items.length} conteúdos`;
      empty.hidden = shown !== 0;
    }
    [q, fmt, tema].forEach(el => el.addEventListener('input', apply));
    filters.addEventListener('submit', e => e.preventDefault());
    filters.addEventListener('reset', () => setTimeout(apply, 0));
    apply();
  }

  // Microanimações suaves ao rolar, respeitando prefers-reduced-motion.
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const els = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) { els.forEach(el => el.classList.add('in')); return; }
  const io = new IntersectionObserver(entries => entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -8% 0px' });
  els.forEach(el => io.observe(el));
})();
