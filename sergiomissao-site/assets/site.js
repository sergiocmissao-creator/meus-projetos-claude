(() => {
  'use strict';
  const button = document.getElementById('menu-button');
  const nav = document.getElementById('nav');
  function closeMenu() { nav.classList.remove('open'); button.setAttribute('aria-expanded', 'false'); }
  button?.addEventListener('click', () => { const open = nav.classList.toggle('open'); button.setAttribute('aria-expanded', String(open)); });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav?.classList.contains('open')) { closeMenu(); button.focus(); } });
  const year = document.getElementById('ano');
  if (year) year.textContent = new Date().getFullYear();
  // Old campaign and article links retain their destinations.
  const legacy = {
    mentoria:'/mentoria/', avaliacao:'/mentoria/#avaliacao', entrevistas:'/mentoria/#entrevistas',
    'preparacao-entrevistas':'/mentoria/#entrevistas', consultoria:'/consultoria/', treinamentos:'/treinamentos/',
    palestras:'/palestras/', 'palestras-detalhe':'/palestras/', 'palestra-burnout':'/palestras/burnout-sem-lados/',
    'palestra-desaprenda':'/palestras/desaprenda-a-liderar/', 'palestra-dono':'/palestras/a-experiencia-do-dono/',
    sobre:'/sobre/', contato:'/contato/', artigos:'/artigos/', posts:'/posts/', ladob:'/artigos/',
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
})();
