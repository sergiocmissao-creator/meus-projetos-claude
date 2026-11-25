"""Gerador do site sergiomissao.com.br.

Uso: python3 scripts/build_site.py            (produção)
     SITE_PREVIEW=1 python3 scripts/build_site.py   (prévia: mostra blocos "a preencher")

Conteúdo editorial (artigos e posts) vem de sergiomissao-site/data/editorial.json.
Cada item aceita o campo "tema" (um dos TEMAS abaixo); sem ele, entra em "Liderança e gestão".
"""
from pathlib import Path
import re, json, html, os
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sergiomissao-site'
OUT.mkdir(exist_ok=True)
E = html.escape
BASE = 'https://sergiomissao.com.br'
PREVIEW = os.environ.get('SITE_PREVIEW') == '1'
pages = {}          # path -> title (entram no sitemap)
noindex_pages = set()

WA_NUMBER = '5511916556521'
AGENDA = 'https://calendar.app.google/P4hFoDGgfbcVtn9u8'
EMAIL = 'mailto:contato@sergiomissao.com.br'
BURNEI = 'https://burnei.com.br'
LIVRO = 'BURNEI! E agora?'

def write(path, text):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def wa_text(text):
    return 'https://wa.me/' + WA_NUMBER + '?text=' + quote(text)

def wa(service):
    return wa_text('Olá! Gostaria de conversar sobre ' + service + '. Vim pelo site sergiomissao.com.br.')

def cta(service, label='Solicitar proposta'):
    return '<a class="button" href="'+E(wa(service))+'">'+E(label)+'</a>'

def pair(service, msg_label='Enviar mensagem', book_label='Agendar'):
    """Dois botões: mensagem por WhatsApp e agendamento (agenda com datas pré-definidas)."""
    return ('<a class="button" href="'+E(wa(service))+'">'+E(msg_label)+'</a>'
            '<a class="button secondary" href="'+AGENDA+'" target="_blank" rel="noopener">'+E(book_label)+'</a>')

def talk_pair(service):
    """Palestras: mensagem por WhatsApp ou e-mail."""
    return ('<a class="button" href="'+E(wa(service))+'">Enviar mensagem pelo WhatsApp</a>'
            '<a class="button secondary" href="'+EMAIL+'?subject='+quote('Palestra: '+service.replace('a palestra ',''))+'">Enviar e-mail</a>')

def closing(title, text, service):
    return section(title, '<p class="reading">'+E(text)+'</p><div class="actions">'+pair(service)+'</div>')

def link(url, label, cls='text-link', ext=False):
    extra = ' target="_blank" rel="noopener"' if ext else ''
    return f'<a class="{cls}" href="{E(url)}"{extra}>{E(label)}</a>'

def livro_link(label=None):
    """Toda menção ao livro leva ao site próprio (pedido de 25/11/2026)."""
    return '<a class="text-link" href="'+BURNEI+'" target="_blank" rel="noopener">'+E(label or LIVRO)+'</a>'

def ul(items):
    return '<ul>'+''.join('<li>'+E(x)+'</li>' for x in items)+'</ul>'

def ol(items):
    return '<ol class="steps">'+''.join('<li><strong>'+E(t)+'</strong>'+(('<span>'+E(d)+'</span>') if d else '')+'</li>' for t,d in items)+'</ol>'

def section(title, content, id='', cls=''):
    return (f'<section class="section{(" "+cls) if cls else ""}"'+(f' id="{id}"' if id else '')
            +f'><div class="wrap"><h2>{E(title)}</h2>{content}</div></section>')

def hero(tag, title, intro, action='', img='', crumb=''):
    return ('<section class="page-hero"><div class="wrap">'+crumb+'<div class="hero-grid"><div><p class="eyebrow">'+E(tag)
            +'</p><h1>'+E(title)+'</h1><p class="lead">'+E(intro)+'</p><div class="actions">'+action+'</div></div>'+img+'</div></div></section>')

RESPONSIVE = {}  # imagens com versão -800 para celular
for f in (OUT/'images/cooperativismo').glob('coop-*-800.jpg'):
    RESPONSIVE['images/cooperativismo/'+f.name.replace('-800.jpg','.jpg')] = 'images/cooperativismo/'+f.name

def image(src, alt, cls='', eager=False, sizes='(max-width: 700px) 100vw, 50vw'):
    extra = ''
    if src in RESPONSIVE:
        extra = f' srcset="/{RESPONSIVE[src]} 800w, /{src} 1672w" sizes="{sizes}" width="1672" height="941"'
    return f'<img class="{cls}" src="/{src}" alt="{E(alt)}"{extra} loading="'+('eager' if eager else 'lazy')+'" decoding="async"'+(' fetchpriority="high"' if eager else '')+'>'

def ilus(src, alt, cls='', eager=False, note='Imagem ilustrativa', sizes='(max-width: 700px) 100vw, 50vw'):
    """Imagens ilustrativas ficam identificadas como tal."""
    return '<figure class="ilus '+cls+'">'+image(src, alt, '', eager, sizes)+'<figcaption>'+E(note)+'</figcaption></figure>'

def preview_only(html_):
    return html_ if PREVIEW else ''

def depoimento():
    return preview_only('<aside class="todo" aria-label="Pendência da prévia"><strong>Depoimento real – a preencher</strong><p>Bloco visível só na prévia. Entra no site quando houver depoimento autorizado, com nome, cargo e cooperativa ou empresa.</p></aside>')

def crumbs(items):
    """items: [(url, label), ..., (None, página atual)]"""
    parts = []
    for url, label in items:
        parts.append(link(url, label, 'crumb') if url else '<span aria-current="page">'+E(label)+'</span>')
    return '<nav class="breadcrumb" aria-label="Você está em">'+' <span aria-hidden="true">›</span> '.join(parts)+'</nav>'

def faq(items):
    return '<div class="faq">'+''.join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>' for q,a in items)+'</div>'

NAV = [('palestras','Palestras'),('mentoria','Mentoria'),('consultoria','Consultoria'),('cooperativismo','Cooperativismo'),('conteudos','Conteúdos'),('sobre','Sobre')]
CONTEUDO_PATHS = ('artigos','posts','quem-voce-contrataria','decisor-por-um-dia','como-funciona-simulacao-entrevista','conteudos')

def current_section(path):
    top = path.split('/')[0] if path else ''
    if top in CONTEUDO_PATHS: return 'conteudos'
    return top

def header_html(path=''):
    cur = current_section(path)
    menu = ''.join(f'<a href="/{slug}/"'+(' aria-current="page"' if cur==slug else '')+f'>{name}</a>' for slug,name in NAV)
    return (f'<a class="skip" href="#conteudo">Pular para o conteúdo</a><header class="site-header"><div class="wrap topbar">'
            f'<a class="brand" href="/" aria-label="Sérgio Missão, página inicial"><img class="logo" src="/logo-sm.png" alt="" width="40" height="40"><span>Sérgio Missão<small>Palestrante, mentor e consultor</small></span></a>'
            f'<nav id="nav" aria-label="Principal">{menu}</nav>'
            f'<a class="button header-cta" href="/contato/">Conversar<span class="long">&nbsp;com Sérgio</span></a>'
            f'<button id="menu-button" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span class="mtxt">Menu </span><span aria-hidden="true">☰</span></button></div></header>')

def footer_html():
    col = lambda title, items: '<div><strong>'+title+'</strong>'+''.join(f'<a href="{E(u)}"'+(' target="_blank" rel="noopener"' if u.startswith('http') and 'wa.me' not in u else '')+f'>{E(l)}</a>' for u,l in items)+'</div>'
    return ('<footer class="site-footer"><div class="wrap footer-grid"><div><a class="brand" href="/">Sérgio Missão</a><p>Palestras, mentoria e consultoria em liderança, comunicação, governança e cultura.</p><p>Para profissionais, empresas e cooperativas.</p></div>'
            + col('Serviços', [('/palestras/','Palestras'),('/mentoria/','Mentoria'),('/consultoria/','Consultoria'),('/treinamentos/','Treinamentos'),('/cooperativismo/','Cooperativismo')])
            + col('Para quem contrata', [('/organizadores/','Para organizadores'),('/palestras/#fichas','Fichas das palestras'),('/contato/','Contato e propostas')])
            + col('Conteúdos', [('/conteudos/','Todos os conteúdos'),('/artigos/','O Lado B da Liderança'),('/posts/','Posts'),('/quem-voce-contrataria/','Quem você contrataria?'),('/decisor-por-um-dia/','Decisor por um Dia')])
            + col('Contato', [(wa('uma proposta'),'WhatsApp: +55 11 91655-6521'),('mailto:contato@sergiomissao.com.br','contato@sergiomissao.com.br'),('https://www.linkedin.com/in/missao','LinkedIn'),('https://www.instagram.com/sergio.missao','Instagram')])
            + '</div><p class="wrap copyright">© <span id="ano">2026</span> Sérgio Missão · #NaMissão</p></footer>')

def page(path, title, desc, body, og='foto-palco.jpg', theme='', noindex=False, og_alt=''):
    url = BASE + ('/'+path+'/' if path else '/')
    schema = {'@context':'https://schema.org','@type':'WebPage','name':title,'description':desc,'url':url,'inLanguage':'pt-BR'}
    if not path:
        schema = {'@context':'https://schema.org','@type':'Person','name':'Sérgio Missão','jobTitle':'Palestrante, mentor e consultor','url':BASE,'image':BASE+'/foto-palco.jpg','sameAs':['https://www.linkedin.com/in/missao','https://www.instagram.com/sergio.missao']}
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    markup = (f'<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
              f'<title>{E(title)} | Sérgio Missão</title><meta name="description" content="{E(desc)}">{robots}<link rel="canonical" href="{url}"><link rel="icon" href="/logo-sm.png">'
              f'<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Sérgio Missão">'
              f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">'
              f'<meta property="og:image" content="{BASE}/{og}"><meta property="og:image:alt" content="{E(og_alt or title)}"><meta name="twitter:card" content="summary_large_image">'
              f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">'
              f'<link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head>'
              f'<body{(" class=\"theme-"+theme+"\"") if theme else ""}>\n{header_html(path)}\n<main id="conteudo">{body}</main>{footer_html()}</body></html>')
    write((path+'/' if path else '')+'index.html', markup)
    if noindex: noindex_pages.add(path)
    else: pages[path] = title

# ---------------------------------------------------------------- formulários (Netlify Forms)
def field(name, label, required=False, kind='text', placeholder='', options=None, hint=''):
    req = ' required aria-required="true"' if required else ''
    mark = ' <span class="req" aria-hidden="true">*</span>' if required else ' <span class="opt">(opcional)</span>'
    fid = 'f-'+name
    hint_html = f'<small id="{fid}-dica">{E(hint)}</small>' if hint else ''
    desc = f' aria-describedby="{fid}-dica"' if hint else ''
    if kind == 'textarea':
        ctl = f'<textarea id="{fid}" name="{name}" rows="4"{req}{desc}></textarea>'
    elif kind == 'select':
        ctl = f'<select id="{fid}" name="{name}"{req}{desc}><option value="">Selecione</option>'+''.join(f'<option>{E(o)}</option>' for o in options)+'</select>'
    else:
        ctl = f'<input id="{fid}" name="{name}" type="{kind}"'+(f' placeholder="{E(placeholder)}"' if placeholder else '')+f'{req}{desc}>'
    return f'<div class="field"><label for="{fid}">{E(label)}{mark}</label>{ctl}{hint_html}</div>'

def form(name, fields, submit, purpose):
    return (f'<form class="form" name="{name}" method="POST" action="/obrigado/" data-netlify="true" netlify-honeypot="bot-field">'
            f'<input type="hidden" name="form-name" value="{name}">'
            '<p class="honeypot" hidden><label>Não preencha este campo: <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>'
            '<p class="form-note">Campos com <span class="req">*</span> são obrigatórios. '+E(purpose)+'</p>'
            + ''.join(fields) + f'<button class="button" type="submit">{E(submit)}</button></form>')

def coop_form():
    return form('cooperativismo', [
        field('nome','Nome',True),
        field('cooperativa','Cooperativa',True),
        field('cargo','Cargo'),
        field('retorno','E-mail ou telefone para retorno',True,hint='Usado só para responder a este pedido.'),
        field('publico','Público',kind='select',options=['Associados','Núcleo, coordenadores e delegados','Conselho','Diretoria','Equipes e colaboradores','Mais de um público']),
        field('objetivo','Objetivo',True,'textarea',hint='Conte a situação: evento, assembleia, programa, visita ou outra necessidade.'),
        field('periodo','Data ou período'),
        field('participantes','Número aproximado de participantes',kind='number'),
    ], 'Enviar pedido', 'As informações servem para preparar a resposta e uma proposta. Não são usadas para outra finalidade.')

def contato_form():
    return form('contato', [
        field('nome','Nome',True),
        field('retorno','E-mail ou telefone para retorno',True,hint='Usado só para responder a esta mensagem.'),
        field('interesse','Assunto',kind='select',options=['Palestra','Mentoria','Consultoria','Treinamento','Cooperativismo','Livro BURNEI! E agora?','Ainda não sei qual serviço']),
        field('organizacao','Empresa ou cooperativa'),
        field('mensagem','O que você precisa resolver?',True,'textarea',hint='Inclua público, data e cidade, se houver evento.'),
    ], 'Enviar mensagem', 'As informações servem para responder ao seu contato. Não são usadas para outra finalidade.')

# ---------------------------------------------------------------- palestras
talks = [
 {'slug':'burnout-sem-lados','title':'Burnout Sem Lados','tag':'Pessoas, pressão e responsabilidade','intro':'Empresa e empregado na mesma conversa sobre pressão, limites e responsabilidade.',
  'public':'Lideranças, RH, executivos e equipes que precisam conversar sobre as relações de trabalho e a pressão por resultados.',
  'short':'Lideranças, RH e equipes',
  'when':'SIPAT, encontros de liderança, eventos corporativos e ações de desenvolvimento que abordam cultura, limites e responsabilidade nas relações de trabalho.',
  'proposal':'Uma conversa sobre cultura, liderança, limites, protagonismo e produtividade sustentável. O ponto de partida é olhar o papel da organização e de quem trabalha nela, com espaço para discutir escolhas do dia a dia.',
  'discuss':'Como a pressão por resultado vira adoecimento, e o que cabe à empresa, à liderança e a cada pessoa.',
  'topics':['Pressão por desempenho e expectativas de trabalho','O papel da liderança e dos colaboradores','Limites e comunicação nas relações profissionais','Cultura e responsabilidade compartilhada','Bem-estar e continuidade dos resultados'],
  'learning':['Reconhecer situações que merecem uma conversa sobre pressão e limites','Distinguir responsabilidades da liderança e da equipe','Formular perguntas para discutir práticas de trabalho e expectativas'],
  'duration':'60 a 90 minutos, ajustável à programação do evento.',
  'formats':'Palestra para eventos corporativos, SIPAT, convenções e encontros de liderança. Também há versão para cooperativas, “Quem cuida de quem cuida”.',
  'img':'img/palestras/burnout-sem-lados.jpg','alt':'Burnout Sem Lados: o equilíbrio entre resultados, saúde e responsabilidade compartilhada'},
 {'slug':'desaprenda-a-liderar','title':'Desaprenda a Liderar','tag':'Liderança além do cargo','intro':'O que trouxe você até a liderança pode estar dificultando o seu próximo passo como líder.',
  'public':'Diretores, gerentes, coordenadores, líderes recém-promovidos, futuros sucessores e profissionais de RH e educação corporativa.',
  'short':'Gestores e novos líderes',
  'when':'Encontros de gestores, programas de sucessão e momentos em que a organização precisa desenvolver autonomia e confiança nas equipes.',
  'proposal':'Uma pausa para rever hábitos de gestão. Quem chegou à liderança por executar bem precisa aprender a desenvolver outras pessoas, delegar e deixar espaço para respostas que não sejam apenas as suas.',
  'discuss':'Quais hábitos de quem executa bem atrapalham quem precisa formar equipe e sucessores.',
  'topics':['Das respostas prontas às perguntas certas','Feedback que desenvolve','Delegar sem abandonar','Vulnerabilidade e autoridade','Formação de sucessores'],
  'learning':['Identificar hábitos de controle que limitam a autonomia','Preparar perguntas e feedbacks com foco no desenvolvimento','Relacionar delegação, confiança e formação de sucessores'],
  'duration':'60 a 90 minutos, ajustável à programação do evento.',
  'formats':'Palestra para encontros de gestores, convenções e programas de desenvolvimento de lideranças.',
  'img':'ilus/desaprenda.svg','alt':'Ilustração da palestra Desaprenda a Liderar'},
 {'slug':'a-experiencia-do-dono','title':'A Experiência do Dono','tag':'Cooperativismo na prática','intro':'Aqui o cliente é dono. Mas ele realmente se sente assim?',
  'public':'Colaboradores, coordenadores, conselheiros, lideranças e associados de cooperativas, especialmente quem atua no relacionamento e na experiência dos associados.',
  'short':'Cooperativas: equipes e associados',
  'when':'Convenções, encontros de cooperativas, assembleias e ações de desenvolvimento voltadas a pertencimento, relacionamento e experiência do associado.',
  'proposal':'Uma reflexão sobre como o propósito cooperativista aparece no atendimento e nas decisões cotidianas. O trabalho conecta pertencimento, protagonismo, cultura e experiência percebida pelo associado.',
  'discuss':'Por que o associado nem sempre se sente dono, e quais pequenos momentos constroem ou destroem o pertencimento.',
  'topics':['O dono que não sabe que é dono','Os pequenos momentos que constroem ou destroem o pertencimento','O papel de cada colaborador na experiência do associado','Cultura, relacionamento e confiança','Conexão com novas gerações de associados'],
  'learning':['Distinguir atendimento ao cliente e reconhecimento do associado como dono','Identificar atitudes que reforçam pertencimento','Relacionar cultura interna e experiência percebida pelo associado'],
  'duration':'60 a 90 minutos. Há versão de 30 minutos para assembleias.',
  'formats':'Palestra para encontros, convenções e assembleias de cooperativas. Compare com as outras palestras cooperativistas em Cooperativismo.',
  'img':'img/palestras/a-experiencia-do-dono.jpg','alt':'A Experiência do Dono: legado não se comemora, legado se mede na experiência de quem é dono'}
]
REQUISITOS = 'Projetor ou tela com entrada HDMI e microfone sem fio. Som, palco e transmissão são combinados com a organização.'
COMBINADO = ['Data, horário e duração final dentro da programação','Cidade e local, ou modalidade online','Perfil e número estimado de participantes','Exemplos e situações do setor que devem entrar na conversa','Condições comerciais e logística de deslocamento']

def talkcards(compact=False):
    out = '<div class="grid three">'
    for t in talks:
        out += ('<article class="card talk-card">'+image(t['img'], t.get('alt',''), 'card-image')+'<p class="eyebrow">'+E(t['tag'])+'</p><h3>'+E(t['title'])+'</h3><p>'+E(t['intro'])+'</p>'
                +'<dl class="mini"><dt>Para quem</dt><dd>'+E(t['short'])+'</dd><dt>A plateia vai discutir</dt><dd>'+E(t['discuss'])+'</dd></dl>'
                +link('/palestras/'+t['slug']+'/', 'Abrir a ficha da palestra →')+'</article>')
    return out+'</div>'

def ficha(t):
    rows = [('Tema',t['intro']),('Para quem',t['public']),('Quando faz sentido',t['when']),('Duração',t['duration']),('Formatos',t['formats']),('Requisitos técnicos',REQUISITOS),('Contato','WhatsApp +55 11 91655-6521 · contato@sergiomissao.com.br')]
    return ('<div class="ficha" id="ficha"><p class="eyebrow">Ficha da palestra</p><h2>'+E(t['title'])+' — resumo para encaminhar</h2><dl>'
            + ''.join('<dt>'+E(a)+'</dt><dd>'+E(b)+'</dd>' for a,b in rows)
            + '</dl><div class="actions no-print"><button class="button secondary js-print" type="button" hidden>Imprimir ou salvar em PDF</button>'+link('/organizadores/','Biografia e fotos para divulgação →')+'</div></div>')

for t in talks:
    service = 'a palestra '+t['title']
    body = hero('Palestra', t['title'], t['intro'], talk_pair(service)+'<a class="button secondary" href="#ficha">Ver a ficha para encaminhar</a>', image(t['img'],t.get('alt',''),'hero-art',True), crumbs([('/palestras/','Palestras'),(None,t['title'])]))
    body += section('A proposta','<p class="reading">'+E(t['proposal'])+'</p><div class="grid two"><article><h3>Para quem</h3><p>'+E(t['public'])+'</p></article><article><h3>Quando faz sentido</h3><p>'+E(t['when'])+'</p></article></div>')
    body += section('O que a plateia vai discutir','<p class="reading">'+E(t['discuss'])+'</p><div class="grid two"><article class="card"><h3>Temas abordados</h3>'+ul(t['topics'])+'</article><article class="card"><h3>Aprendizagens esperadas</h3>'+ul(t['learning'])+'</article></div>')
    if t['slug']=='burnout-sem-lados':
        body += section('A conversa também está no livro','<div class="feature-grid"><div class="reading"><p>O livro '+livro_link()+' aborda o burnout na visão de um executivo que viveu os dois lados. O livro e a palestra compartilham essa perspectiva sobre trabalho, liderança e responsabilidade.</p><p>Lançamento, novidades e leituras sobre burnout estão no site do livro.</p><div class="actions">'+link(BURNEI,'Conhecer o livro em burnei.com.br','button secondary',True)+link(wa('informações sobre o livro '+LIVRO),'Perguntar sobre o livro pelo WhatsApp →')+'</div></div><a href="'+BURNEI+'" target="_blank" rel="noopener" aria-label="Site do livro '+E(LIVRO)+'">'+image('ilus/burnei-capa.jpg','Capa do livro BURNEI! E agora? O burnout na visão de um executivo que viveu os dois lados','book')+'</a></div>')
        body += section('Versão para cooperativas','<p class="reading">Em cooperativas, a palestra integra o kit Cooperativa que Cuida, com o título “Quem cuida de quem cuida”, exemplares do livro para as lideranças e uma roda de conversa.</p>'+link('/cooperativismo/cooperativa-que-cuida/','Conhecer a Cooperativa que Cuida →'))
    if t['slug']=='a-experiencia-do-dono':
        body += section('Aplicação em cooperativas','<p class="reading">A palestra faz parte do núcleo de Cooperativismo, ao lado de Do Núcleo ao Conselho e O Legado de Amstad. A comparação entre as três, com roteiro e versões de duração, está na página de palestras cooperativistas.</p><div class="actions">'+link('/cooperativismo/palestras/','Comparar as palestras cooperativistas','button secondary')+link('/cooperativismo/','Conhecer o núcleo de Cooperativismo →')+'</div>')
    body += section('Ficha para o comitê', ficha(t), cls='section-ficha')
    body += section('O que será combinado','<p class="reading">Algumas informações dependem do evento. Elas são definidas na conversa inicial e registradas na proposta:</p>'+ul(COMBINADO))
    body += section('Leve esta conversa ao seu evento','<p class="reading">Conte o objetivo do encontro, o perfil do público, a data prevista e a cidade ou modalidade.</p><div class="actions">'+talk_pair(service)+link('/organizadores/','Materiais para organizadores')+'</div>')
    page('palestras/'+t['slug'],t['title'],t['intro']+' Palestra de Sérgio Missão: público, duração, formatos e contato.',body,og=t['img'] if t['img'].endswith('.jpg') else 'foto-palco.jpg')

cmp_rows = ''.join('<tr><th scope="row">'+link('/palestras/'+t['slug']+'/',t['title'])+'</th><td>'+E(t['intro'])+'</td><td>'+E(t['short'])+'</td><td>'+E(t['discuss'])+'</td><td>'+E(t['duration'])+'</td></tr>' for t in talks)
body = hero('Palestras','Conversas que continuam depois do evento.','Liderança, relações de trabalho e cooperativismo, conectados às situações que o seu público vive. Compare os temas e abra a ficha para encaminhar ao comitê.',talk_pair('palestras para nosso evento'),image('foto-palco.jpg','Sérgio Missão falando ao microfone para uma plateia','hero-art photo',True))
body += section('Escolha a conversa para o seu público',talkcards(),'escolher')
body += section('Compare lado a lado','<div class="table-wrap"><table class="compare"><caption class="sr-only">Comparação entre as palestras</caption><thead><tr><th scope="col">Palestra</th><th scope="col">Tema</th><th scope="col">Para quem</th><th scope="col">O que a plateia vai discutir</th><th scope="col">Duração</th></tr></thead><tbody>'+cmp_rows+'</tbody></table></div>')
body += section('Fichas para encaminhar','<p class="reading">Cada palestra tem uma ficha com tema, público, duração, formatos, requisitos técnicos e contato, pronta para imprimir ou salvar em PDF.</p><div class="actions">'+''.join(link('/palestras/'+t['slug']+'/#ficha','Ficha: '+t['title'],'button secondary') for t in talks)+'</div><p>Biografia e fotos para divulgação estão na '+link('/organizadores/','página para organizadores')+'.</p>','fichas')
body += section('Para cooperativas','<p class="reading">A Experiência do Dono, Do Núcleo ao Conselho e O Legado de Amstad formam o conjunto de palestras cooperativistas, com versões para assembleias e datas do cooperativismo.</p>'+link('/cooperativismo/palestras/','Comparar as palestras cooperativistas →'))
body += section('Do contexto à proposta','<div class="grid three"><article><span class="number">01</span><h3>Seu evento</h3><p>Objetivo, público, data e local ajudam a definir o foco.</p></article><article><span class="number">02</span><h3>O conteúdo</h3><p>A palestra é alinhada ao momento da organização e às perguntas do público.</p></article><article><span class="number">03</span><h3>A contratação</h3><p>Escopo, formato, duração e condições são definidos na proposta.</p></article></div>')
body += section('Leve uma palestra ao seu evento','<p class="reading">Conte o objetivo, o público, a data e a cidade ou modalidade.</p><div class="actions">'+talk_pair('palestras para nosso evento')+'</div>')
page('palestras','Palestras para empresas e cooperativas','Compare Burnout Sem Lados, Desaprenda a Liderar e A Experiência do Dono: tema, público, duração e ficha para encaminhar.',body)


def serie_quem():
    return ('<div class="feature-grid serie"><div><p class="eyebrow">Série no LinkedIn</p><h2>Quem você contrataria?</h2>'
            '<p class="lead">Personagens famosos disputando uma vaga. Todos têm talento, todos têm riscos. Qual você escolheria?</p>'
            '<p>Do outro lado da mesa, alguém também vai pesar os seus talentos e os seus riscos.</p><div class="actions">'
            + link('/quem-voce-contrataria/','Ver os candidatos','button') + link('/mentoria/#entrevistas','Preparar minha entrevista','button secondary')
            + '</div></div>' + image('img/series/quem-voce-contrataria-mesa.jpg','Mesa de reunião vazia com o título Quem você contrataria?','serie-art') + '</div>')


# ---- treinamentos (texto preservado)
programs = [
 ('lideranca','Liderança e gestão de pessoas','Gestores, líderes recém-promovidos e profissionais que se preparam para assumir equipes.','Desenvolver uma atuação mais clara na orientação, delegação e acompanhamento de pessoas.',['Papel do líder e prioridades','Delegação e acompanhamento','Conversas de desenvolvimento','Autonomia, confiança e sucessão'],'Discussão de situações de gestão trazidas pela organização e preparação de ações para a rotina da equipe.'),
 ('comunicacao','Comunicação e feedback','Líderes e equipes que precisam alinhar expectativas ou conduzir conversas difíceis.','Organizar a mensagem, ouvir com atenção e tornar os acordos mais claros.',['Clareza e escuta','Expectativas entre áreas','Preparação de feedbacks','Conversas difíceis e acordos'],'O trabalho parte de conversas reais do contexto profissional, com organização da mensagem e discussão de formas de abordagem.'),
 ('negociacao','Negociação','Profissionais e gestores que negociam prioridades, recursos e acordos no trabalho.','Preparar conversas de negociação com objetivos, argumentos e limites claros.',['Compreensão do contexto','Interesses e prioridades','Argumentos e escuta','Construção de acordos'],'Análise de situações de negociação do dia a dia e preparação da abordagem para cada interlocutor.'),
 ('cultura','Cultura e engajamento','Lideranças e equipes que precisam fortalecer a responsabilidade pelo trabalho em conjunto.','Relacionar o discurso da organização às atitudes, decisões e relações cotidianas.',['Comportamentos e cultura','Responsabilidade individual e coletiva','Confiança e cooperação','Alinhamento de expectativas'],'Discussão de situações da organização, identificando comportamentos a manter e pontos que precisam de novos acordos.'),
 ('cooperativismo','Cooperação e cooperativismo','Equipes e lideranças de cooperativas e profissionais ligados ao relacionamento com associados.','Traduzir propósito cooperativista em atitudes de cooperação e reconhecimento do associado.',['Pertencimento e protagonismo','Experiência do associado','Cooperação entre equipes','Cultura e relacionamento'],'Reflexão sobre situações de atendimento e gestão, conectando os temas à realidade da cooperativa.')
]
body=hero('Treinamentos corporativos','Desenvolvimento com espaço para aplicar.','Programas para trabalhar liderança, comunicação, negociação e cooperação a partir da realidade da sua organização.',cta('treinamentos para nossa equipe'))
for slug,title,public,goal,topics,method in programs:
    body+=section(title,'<div class="grid two"><div><p class="eyebrow">Público</p><p>'+E(public)+'</p><h3>Objetivo</h3><p>'+E(goal)+'</p></div><div><h3>Conteúdo do programa</h3>'+ul(topics)+'</div></div><div class="method"><h3>Forma de aplicação</h3><p>'+E(method)+'</p>'+cta('o treinamento '+title)+'</div>',slug)
body+=section('Formato alinhado à necessidade','<div class="grid three"><article class="card"><h3>Intensivo</h3><p>1 a 2 dias para aprofundar um tema.</p></article><article class="card"><h3>Imersão</h3><p>5 dias dedicados ao desenvolvimento da equipe.</p></article><article class="card"><h3>Programa sob medida</h3><p>Encontros ao longo de semanas ou meses, conforme o escopo combinado.</p></article></div><p>Turmas fechadas para organizações. A composição do programa e as condições de realização são alinhadas antes da contratação.</p>')
page('treinamentos','Treinamentos corporativos', 'Programas de liderança, comunicação e feedback, negociação, cultura e cooperativismo para desenvolver equipes.',body)

# Como funciona a simulação de entrevista (destino do botão AGENDAR ENTREVISTA da série)
def step(n, t, d):
    return '<article class="card"><p class="eyebrow">Passo '+n+'</p><h3>'+E(t)+'</h3><p>'+E(d)+'</p></article>'
body=hero('Simulação de entrevista','Como funciona a simulação de entrevista.','Você conta sua trajetória, responde em voz alta a quem está no papel de entrevistador e sai com feedback para chegar seguro à conversa de verdade.',pair('a simulação de entrevista','Dúvidas','Agendar'))
body+=section('Passo a passo','<div class="grid two">'+step('1','Agendamento','Você escolhe um horário disponível na agenda. As datas e horários oferecidos seguem as regras definidas previamente.')+step('2','Contexto','Você informa a vaga, a empresa e o momento da carreira para a simulação partir de uma situação real.')+step('3','Simulação','Sérgio assume o papel de entrevistador e conduz a conversa com perguntas da vaga, inclusive as incômodas.')+step('4','Feedback e nova rodada','Você recebe retorno sobre clareza, exemplos e postura, e pratica de novo os pontos que pedem ajuste.')+'</div>','passos')
body+=section('Antes de agendar','<ul><li>Separe a descrição da vaga e o seu currículo.</li><li>Pense em duas ou três experiências que você quer destacar.</li><li>Anote as perguntas que mais o preocupam.</li></ul><p class="reading">Formato, duração e valores são alinhados no contato inicial. Ficou com alguma dúvida? Envie uma mensagem.</p>')
body+=closing('Pronto para treinar?','Tire dúvidas por mensagem ou agende a sua simulação.','a simulação de entrevista')
body+=section('Conheça também','<div class="actions">'+link('/quem-voce-contrataria/','Série Quem você contrataria?','button secondary')+link('/decisor-por-um-dia/#entrevistas','O método Decisor por um Dia','button secondary')+link('/mentoria/#entrevistas','Preparação para entrevistas','button secondary')+'</div>')
page('como-funciona-simulacao-entrevista','Como funciona a simulação de entrevista','Veja como funciona a simulação de entrevista com Sérgio Missão no papel de entrevistador, tire dúvidas por WhatsApp e agende seu horário.',body)

def door(id_, title, who, criteria, questions, extra=''):
    return section(title,'<div class="grid two"><div><p class="eyebrow">Quem decide</p><p>'+E(who)+'</p><h3>Critérios que costumam pesar</h3>'+ul(criteria)+'</div><div><h3>Perguntas para praticar</h3>'+ul(questions)+'</div></div>'+extra,id_)

serie_door = ('<a class="card serie-card" href="/quem-voce-contrataria/">'+image('img/series/quem-voce-contrataria-mesa.jpg','Mesa de reunião vazia com o título Quem você contrataria?','serie-thumb')
              +'<div><p class="eyebrow">Para treinar o olhar</p><h3>Quem você contrataria?</h3><p>Na série, candidatos famosos disputam uma vaga. Escolha quem você contrataria e compare seus critérios com os de outras pessoas →</p></div></a>')

body=hero('Método · Entrevistas, avaliação de desempenho e negociação','Prepare-se pensando como quem decide.','O Decisor por um Dia coloca você na cadeira de quem avalia. Critérios, perguntas e respostas definidos antes da conversa que importa.',pair('o método Decisor por um Dia')+link('#metodo','Ver o método em 4 etapas','button secondary'))
body+=section('Por que inverter a cadeira','<p class="reading">Muita gente se prepara ensaiando respostas. Quem decide, do outro lado, compara evidências com critérios. Quando você sabe o que essa pessoa precisa ver para dizer sim, a preparação deixa de ser decorar frases e passa a ser escolher boas provas.</p><p class="reading">É o mesmo raciocínio em uma entrevista, em uma avaliação de desempenho ou em uma negociação: alguém vai pesar o que você entrega, o que você pede e o risco de dizer sim.</p>')
body+=section('O método em 4 etapas','<div class="grid two"><article class="card"><p class="eyebrow">Etapa 1</p><h3>Critérios</h3><p>Se você fosse decidir, o que precisaria ver para dizer sim? Liste de 3 a 5 critérios para aquela conversa.</p></article><article class="card"><p class="eyebrow">Etapa 2</p><h3>Perguntas</h3><p>Que perguntas você faria para checar cada critério? Inclua a mais incômoda, aquela que você preferiria não ouvir.</p></article><article class="card"><p class="eyebrow">Etapa 3</p><h3>Respostas</h3><p>Para cada pergunta, escolha uma evidência real sua. Separe a resposta que convence da que apenas soa bem.</p></article><article class="card"><p class="eyebrow">Etapa 4</p><h3>Veredito</h3><p>Avalie suas respostas como decisor: sim, sim com ressalvas ou não. Onde ficou ressalva, volte à etapa 3.</p></article></div>','metodo')
body+=section('Três conversas, um mesmo raciocínio','<p class="reading">As etapas são as mesmas. Mudam quem decide e os critérios que pesam.</p><div class="actions">'+link('#entrevistas','Entrevistas','button secondary')+link('#avaliacao','Avaliação de desempenho','button secondary')+link('#negociacao','Negociação','button secondary')+'</div>')
body+=door('entrevistas','Entrevistas','Recrutador, gestor da vaga ou comitê de seleção.',['Entregas comparáveis ao que a vaga exige','Exemplos concretos, e não apenas intenção','Como você lida com erro, pressão e conflito','Encaixe com a equipe e com o momento da empresa'],['Qual resultado pode ser confirmado por uma referência?','O que mudou na equipe depois que você passou por ela?','Conte uma decisão que você tomaria diferente hoje.'],serie_door+link('/mentoria/#entrevistas','Conhecer a preparação para entrevistas →'))
body+=door('avaliacao','Avaliação de desempenho','Seu gestor e, em muitas empresas, um comitê de calibração.',['Resultados do período, com números ou fatos','Evidências de como o resultado foi alcançado','Impacto além da própria tarefa','Plano de desenvolvimento e próximos passos'],['O que você entregou que ninguém precisou cobrar?','Qual feedback você recebeu e o que fez com ele?','Que responsabilidade você está pronto para assumir?'],link('/mentoria/#avaliacao','Conhecer a preparação para avaliação de desempenho →'))
body+=door('negociacao','Negociação','A outra parte: gestor, cliente, fornecedor ou área parceira.',['Interesse real por trás do pedido','Valor que a proposta gera para quem decide','Risco percebido de aceitar','Alternativas de cada lado'],['O que a outra parte ganha se disser sim?','Qual objeção virá primeiro e qual é a resposta preparada?','Até onde é possível ir e o que pode ser oferecido em troca?'],link('/mentoria/#negociacao','Conhecer a preparação para negociação →'))
body+=section('Exercício para começar hoje','<p class="reading">Escolha uma conversa que você terá nos próximos dias e responda por escrito:</p>'+ul(['Quem vai decidir e o que essa pessoa teme errar?','Quais seriam os 3 critérios no lugar dessa pessoa?','Que pergunta testaria cada critério?','Que evidência responde a cada pergunta?','Com base no que foi escrito, a decisão seria sim, sim com ressalvas ou não?']))
body+=section('Treinar com acompanhamento','<p class="reading">Na mentoria, o método é aplicado à situação real de cada profissional. A simulação coloca o mentor no papel de quem decide, com feedback e nova rodada de prática. A decisão final continua sendo de quem avalia; o objetivo é chegar à conversa com mais clareza e evidências.</p><p>Formato, frequência e valores são alinhados no contato inicial.</p>'+cta('o método Decisor por um Dia na mentoria','Consultar disponibilidade e valores')+link('/mentoria/','Conhecer a mentoria →'))
body+=closing('Quer treinar com acompanhamento?','Tire dúvidas por mensagem ou agende uma simulação em um horário disponível.','o método Decisor por um Dia')
page('decisor-por-um-dia','Decisor por um Dia: prepare entrevistas, avaliações e negociações','Método para se preparar para entrevistas, avaliação de desempenho e negociação pensando como quem decide: critérios, perguntas, respostas e veredito.',body)

def rich(text):
    out=[]
    for paragraph in re.split(r'\n\s*\n',text.strip()):
        if paragraph.startswith('## '): out.append('<h2>'+E(paragraph[3:])+'</h2>')
        elif paragraph.startswith('> '): out.append('<blockquote>'+E(paragraph[2:])+'</blockquote>')
        elif paragraph.startswith('- '): out.append(ul([x[2:] for x in paragraph.splitlines() if x.startswith('- ')]))
        else: out.append('<p>'+E(paragraph).replace('\n','<br>')+'</p>')
    # **texto** vira negrito (marcação herdada do LinkedIn; as palavras não mudam)
    return re.sub(r'\*\*(\S(?:.*?\S)?)\*\*', r'<strong>\1</strong>', ''.join(out))

# ---------------------------------------------------------------- mentoria
dirigentes_txt = 'Acompanhamento individual de presidentes, diretores e conselheiros recém-eleitos de cooperativas, para organizar o papel, as relações com conselho e diretoria e as primeiras decisões no cargo.'
body = hero('Mentoria','Clareza para as decisões e conversas da sua carreira.','Mentoria executiva, mentoria de dirigentes e preparação para entrevistas, avaliação de desempenho e negociação, a partir da situação real de cada pessoa.',pair('disponibilidade e valores da mentoria executiva'),image('foto-retrato.jpg','Sérgio Missão, de blazer bege e camisa branca','portrait',True))
body += section('Escolha pelo objetivo','<div class="grid three goal-grid">'+''.join('<a class="card goal" href="#'+i+'"><h3>'+E(t)+'</h3><p>'+E(d)+'</p><span class="text-link">Ver detalhes →</span></a>' for i,t,d in [
    ('mentoria','Mentoria executiva','Para quem assumiu mais responsabilidade ou precisa decidir os próximos passos.'),
    ('dirigentes','Mentoria de dirigentes','Para presidentes, diretores e conselheiros recém-eleitos de cooperativas.'),
    ('entrevistas','Preparação para entrevistas','Para chegar à entrevista com trajetória clara e prática com simulação.'),
    ('avaliacao','Avaliação de desempenho','Para apresentar entregas e discutir desenvolvimento com o gestor.'),
    ('negociacao','Negociação','Para preparar salário, promoção, escopo ou acordos com clientes e áreas.')])+'</div>','objetivos')
body += section('Quem costuma procurar','<div class="grid two"><div><p class="reading">Profissionais que assumiram uma equipe, foram promovidos, mudaram de empresa, estão diante de uma decisão de carreira ou têm uma conversa importante marcada. Também dirigentes de cooperativa no início de mandato.</p></div><div><p class="reading">A mentoria parte da trajetória de Sérgio Missão como diretor em multinacional e como presidente e conselheiro de cooperativa de crédito. A experiência entra como referência para as perguntas, não como receita pronta.</p></div></div>')
body+=section('Mentoria executiva','<div class="grid two"><div><h3>Para quem faz sentido</h3><p>Profissionais que assumiram uma equipe, ganharam novas responsabilidades, estão diante de uma decisão de carreira ou precisam organizar os próximos passos.</p><p>O acompanhamento trabalha desafios ao longo do tempo. Frequência, formato e valores são alinhados no contato inicial.</p></div><div><h3>O que podemos trabalhar</h3>'+ul(['Liderança e gestão de pessoas','Comunicação e relacionamento profissional','Decisões e desafios da carreira','Preparação para novas responsabilidades','Prioridades e próximos passos'])+'</div></div><div class="actions">'+pair('disponibilidade e valores da mentoria executiva')+'</div>','mentoria')
body+=section('Mentoria de dirigentes','<div class="grid two"><div><p class="reading">'+E(dirigentes_txt)+'</p><p>Para quem chega ao cargo vindo do quadro social ou do núcleo, o trabalho ajuda a separar representação, decisão e gestão.</p></div><div><h3>O que costuma entrar</h3>'+ul(['Papel do conselho e da diretoria','Relação com associados, núcleos e colaboradores','Decisões difíceis e como comunicá-las','Preparação para assembleias e reuniões de conselho','Sucessão e preparação de quem vem depois'])+'</div></div><div class="actions">'+cta('a mentoria de dirigentes para cooperativas','Consultar disponibilidade e valores')+link('/cooperativismo/programas/#mentoria-de-dirigentes','Ver no núcleo de Cooperativismo →')+'</div>','dirigentes')
body+=section('Preparação para entrevistas','<p class="reading">Organização da trajetória para entrevistas de emprego, processos internos e posições de liderança. Inclui simulação de entrevista, com Sérgio no papel de entrevistador, feedback e nova rodada de prática.</p><div class="grid two"><div><h3>Antes da conversa</h3>'+ul(['Compreender a vaga e suas exigências','Escolher experiências relevantes','Estruturar respostas com exemplos reais'])+'</div><div><h3>Durante a preparação</h3>'+ul(['Responder em voz alta e receber feedback','Trabalhar clareza, objetividade e postura','Preparar perguntas para o entrevistador'])+'</div></div><div class="actions">'+cta('disponibilidade e valores da preparação para entrevistas','Consultar disponibilidade e valores')+link('/como-funciona-simulacao-entrevista/','Como funciona a simulação de entrevista →')+'</div><a class="card serie-card" href="/quem-voce-contrataria/">'+image('img/series/quem-voce-contrataria-mesa.jpg','Mesa de reunião vazia com o título Quem você contrataria?','serie-thumb')+'<div><p class="eyebrow">Do outro lado da mesa</p><h3>Quem você contrataria?</h3><p>Candidatos famosos, uma vaga só. Teste seu olhar de recrutador →</p></div></a>','entrevistas')
body+=section('Preparação para avaliação de desempenho','<p class="reading">Sessões para chegar à avaliação com as ideias organizadas, sabendo apresentar entregas e discutir pontos de desenvolvimento. A avaliação continua sendo conduzida pela empresa e pelo gestor.</p>'+ul(['Organização das entregas e resultados do período','Evidências e exemplos concretos','Preparação da autoavaliação','Como receber e discutir feedbacks','Perguntas sobre expectativas e próximos passos'])+cta('disponibilidade e valores da preparação para avaliação de desempenho','Consultar disponibilidade e valores'),'avaliacao')
body+=section('Preparação para negociação','<p class="reading">Sessões para preparar negociações de salário, promoção, escopo e condições de trabalho, além de acordos com clientes e áreas parceiras. O trabalho organiza objetivos, argumentos, limites e alternativas, e inclui simulação da conversa com feedback.</p>'+ul(['Objetivos, limites e alternativas de cada lado','Interesses da outra parte e valor da proposta','Argumentos apoiados em evidências','Respostas às objeções mais prováveis','Próximos passos após a conversa'])+'<div class="actions">'+cta('disponibilidade e valores da preparação para negociação','Consultar disponibilidade e valores')+link('/decisor-por-um-dia/#negociacao','Ver o método aplicado à negociação →')+'</div>','negociacao')
body+=section('Como começa e como se define o trabalho',ol([('Primeiro contato','Mensagem pelo WhatsApp ou horário na agenda. Basta contar o objetivo em poucas linhas.'),('Conversa inicial','Entendimento da situação, do prazo e do que precisa estar diferente ao final.'),('Definição','Formato, número de sessões, frequência e valores são combinados antes de começar.'),('Sessões','Encontros com preparação, prática e feedback. Na preparação pontual, o trabalho termina com a conversa real.')]))
body+=section('Mentoria ou consultoria?','<div class="grid two"><div class="card"><h3>Mentoria</h3><p>O foco é uma pessoa: suas decisões, conversas e próximos passos.</p></div><div class="card"><h3>Consultoria</h3><p>O foco é a organização ou a equipe: um problema que se repete entre pessoas e áreas.</p>'+link('/consultoria/','Conhecer a consultoria →')+'</div></div>')
body+=closing('Vamos conversar?','Tire dúvidas por mensagem ou agende direto um horário disponível na agenda.','mentoria executiva e preparação individual')
page('mentoria','Mentoria executiva e preparação individual','Mentoria executiva, mentoria de dirigentes de cooperativas e preparação para entrevistas, avaliação de desempenho e negociação.',body)

# ---------------------------------------------------------------- consultoria
body = hero('Consultoria','Entender o contexto. Definir o foco. Agir.','Apoio a diretorias, RH, conselhos e gestores quando um problema de liderança, comunicação ou cultura se repete na equipe ou entre áreas.',cta('consultoria para nossa organização','Conversar sobre o desafio'))
body += section('Quem costuma procurar','<p class="reading">Diretorias, áreas de RH e conselhos de empresas e cooperativas que já tentaram resolver uma situação com conversas isoladas e perceberam que ela volta. A consultoria parte da experiência de gestão em multinacional e de governança em cooperativa de crédito.</p>')
body += section('Situações em que a consultoria apoia','<div class="grid three"><article class="card"><h3>Relações entre áreas</h3><p>Expectativas pouco claras, conversas que não avançam e dificuldades de cooperação.</p></article><article class="card"><h3>Desafios da liderança</h3><p>Necessidade de rever práticas de gestão e desenvolver quem assume mais responsabilidade.</p></article><article class="card"><h3>Cultura no cotidiano</h3><p>Distância entre o que a organização diz e o que as pessoas vivem no trabalho.</p></article></div>')
body += section('Três formatos de trabalho','<div class="grid three">'
    '<article class="card" id="diagnostico"><p class="eyebrow">Formato 1</p><h3>Diagnóstico</h3><p>Escuta das pessoas envolvidas e leitura do contexto para separar o problema dos sintomas.</p><p><strong>A organização recebe:</strong> uma devolutiva com a leitura da situação e as prioridades sugeridas.</p></article>'
    '<article class="card" id="acompanhamento"><p class="eyebrow">Formato 2</p><h3>Acompanhamento</h3><p>Encontros periódicos com a liderança para apoiar a aplicação das prioridades combinadas e ajustar o rumo.</p><p><strong>A organização recebe:</strong> apoio na condução das mudanças ao longo do período definido.</p></article>'
    '<article class="card" id="treinamento"><p class="eyebrow">Formato 3</p><h3>Treinamento</h3><p>Programas para grupos quando a necessidade é desenvolver uma habilidade em conjunto: liderança, comunicação, negociação, cultura ou cooperação.</p>'+link('/treinamentos/','Ver os programas de treinamento →')+'</article></div>'
    '<p class="reading">Os formatos podem ser contratados separados ou em sequência. O diagnóstico costuma indicar se o caminho é acompanhamento, treinamento ou os dois.</p>')
body += section('Como começa a conversa',ol([('Contato','Mensagem ou formulário com a situação em poucas linhas.'),('Conversa inicial','Entendimento do contexto, das áreas envolvidas e do que precisa mudar.'),('Proposta','Formato, participantes, entregas, prazos e condições definidos por escrito.'),('Execução','Trabalho conforme o formato escolhido, com pontos de revisão combinados.')]))
body += section('Mentoria ou consultoria?','<p class="reading">Se a questão é de uma pessoa, como uma decisão de carreira ou uma conversa difícil, a '+link('/mentoria/','mentoria')+' costuma ser o caminho. Se o problema se repete entre pessoas ou áreas, a consultoria é mais indicada. Na dúvida, a conversa inicial ajuda a definir.</p>')
body += section('Conte o desafio da sua organização','<p class="reading">Descreva a situação, as áreas envolvidas e o que precisa mudar. Essa conversa orienta o escopo.</p><div class="actions">'+cta('consultoria para nossa organização')+link('/contato/#formulario','Prefiro escrever pelo formulário →')+'</div>')
page('consultoria','Consultoria para empresas e cooperativas','Diagnóstico, acompanhamento e treinamento para desafios de liderança, comunicação e cultura em empresas e cooperativas.',body)

# ---------------------------------------------------------------- sobre
bio='Sérgio Missão é executivo, conselheiro, consultor e palestrante, com mais de duas décadas de atuação executiva. Tem trajetória em multinacionais da indústria e atuação em logística, compras, suporte e serviços, programas, treinamento e relacionamento com clientes. No cooperativismo de crédito, foi associado, coordenador de núcleo, conselheiro e presidente de cooperativa. Trabalha com liderança, comunicação, governança e cultura para profissionais, empresas e cooperativas.'
body = hero('Sobre','Experiência para conversar sobre o trabalho real.',bio,link('/contato/','Conversar com Sérgio','button'),image('foto-retrato.jpg','Sérgio Missão, de blazer bege e camisa branca','portrait',True))
body += section('Trajetória','<div class="grid two"><div><h3>Na gestão</h3><p>Carreira construída em multinacionais da indústria, como diretor e líder de equipes e projetos em logística, compras, suporte e serviços, programas, treinamento e relacionamento com clientes.</p></div><div><h3>No cooperativismo de crédito</h3><p>Percurso de associado a presidente: coordenador de núcleo, conselheiro e presidente de cooperativa. Essa vivência conecta as perspectivas de quem é dono, de quem representa e de quem decide.</p>'+link('/cooperativismo/','Conhecer o núcleo de Cooperativismo →')+'</div></div>')
body += section('Onde essa experiência faz diferença','<div class="grid three"><article class="card"><h3>Em eventos</h3><p>Palestras construídas a partir de situações vividas na gestão e no cooperativismo.</p>'+link('/palestras/','Palestras →')+'</article><article class="card"><h3>Na carreira de quem lidera</h3><p>A experiência de direção ajuda a preparar decisões, entrevistas e negociações.</p>'+link('/mentoria/','Mentoria →')+'</article><article class="card"><h3>Nas organizações</h3><p>Gestão em multinacional e governança em cooperativa como referência para diagnóstico e acompanhamento.</p>'+link('/consultoria/','Consultoria →')+'</article></div>')
body += section('O Lado B da Liderança','<p class="reading">Na newsletter, Sérgio escreve sobre decisões, relações de trabalho e situações de liderança que nem sempre aparecem nas apresentações. Também é autor do livro '+livro_link()+'.</p>'+link('/artigos/','Ler artigos e edições da newsletter →'))
body += preview_only(section('Casos (modelo — só na prévia)','<aside class="todo"><strong>A preencher</strong><p>Cada caso precisa de autorização de uso, contexto, participação de Sérgio e resultado documentado. Modelo: <em>Organização (ou setor, se anônimo) · Situação · O que foi feito · O que mudou · Autorização em [data]</em>.</p></aside>','casos'))
body += preview_only(section('Na mídia (modelo — só na prévia)','<aside class="todo"><strong>A preencher</strong><p>Cada item precisa de veículo, título, data e link. Modelo: <em>Veículo · “Título” · dd/mm/aaaa · link</em>.</p></aside>','midia'))
page('sobre','Sobre Sérgio Missão','Trajetória de Sérgio Missão: diretor em multinacionais e, no cooperativismo de crédito, de associado a presidente de cooperativa.',body)

# ---------------------------------------------------------------- organizadores
body=hero('Para organizadores, empresas e agências','O necessário para avaliar a contratação.','Biografias, fotos, fichas das palestras e contato comercial reunidos para encaminhar ao comitê.',cta('uma proposta para nosso evento'))
body+=section('O que está disponível','<div class="table-wrap"><table class="compare status"><thead><tr><th scope="col">Material</th><th scope="col">Situação</th><th scope="col">Onde</th></tr></thead><tbody>'
    '<tr><td>Biografia curta e completa</td><td><span class="badge ok">Disponível</span></td><td>'+link('#biografia','Nesta página')+'</td></tr>'
    '<tr><td>Fotos para divulgação</td><td><span class="badge ok">Para baixar</span></td><td>'+link('#fotos','Nesta página')+'</td></tr>'
    '<tr><td>Fichas das palestras</td><td><span class="badge ok">Para imprimir ou salvar em PDF</span></td><td>'+link('#fichas','Nesta página')+'</td></tr>'
    '<tr><td>Apresentação comercial</td><td><span class="badge wait">Sob pedido</span></td><td>'+link(wa('a apresentação comercial das palestras'),'Pedir pelo WhatsApp')+'</td></tr>'
    '<tr><td>Valores e disponibilidade de agenda</td><td><span class="badge wait">Sob consulta</span></td><td>'+link('/contato/','Contato')+'</td></tr>'
    '</tbody></table></div>')
body+=section('Biografia curta','<div class="reading"><p>Sérgio Missão é executivo, consultor e palestrante, com trajetória em multinacionais da indústria e no cooperativismo de crédito. Atua com liderança, comunicação, governança e cultura para profissionais, empresas e cooperativas.</p></div>','biografia')
body+=section('Biografia completa','<div class="reading"><p>'+bio+'</p><p>Seu portfólio inclui as palestras Burnout Sem Lados, Desaprenda a Liderar e A Experiência do Dono, palestras e programas para cooperativas, treinamentos corporativos, consultoria, mentoria executiva e preparação para entrevistas, avaliação de desempenho e negociação. É autor da newsletter O Lado B da Liderança e do livro '+livro_link()+'.</p></div>')
body+=section('Fichas das palestras','<div class="grid three">'+''.join('<article class="card"><h3>'+E(t['title'])+'</h3><p>'+E(t['duration'])+'</p>'+link('/palestras/'+t['slug']+'/#ficha','Abrir a ficha →')+'</article>' for t in talks)+'</div><p>Para cooperativas: '+link('/cooperativismo/palestras/','fichas de A Experiência do Dono, Do Núcleo ao Conselho e O Legado de Amstad')+'.</p>','fichas')
body+=section('Fotos para divulgação','<p>Fotos já utilizadas neste site, disponíveis para materiais de divulgação da participação de Sérgio Missão.</p><div class="grid two photo-downloads"><figure>'+image('foto-retrato.jpg','Retrato de Sérgio Missão')+'<figcaption><a download href="/foto-retrato.jpg">Baixar retrato (JPG)</a></figcaption></figure><figure>'+image('foto-palco.jpg','Sérgio Missão falando ao microfone para uma plateia')+'<figcaption><a download href="/foto-palco.jpg">Baixar foto em evento (JPG)</a></figcaption></figure></div>','fotos')
body+=section('Informações para a proposta',ul(['Nome da organização e objetivo do evento','Palestra ou serviço de interesse','Perfil e estimativa de público','Data prevista e cidade ou modalidade','Contato da pessoa responsável'])+'<div class="actions">'+cta('uma proposta para nosso evento')+link('/contato/#formulario','Enviar pelo formulário →')+'</div>')
page('organizadores','Materiais para organizadores','Biografias, fotos, fichas das palestras e contato para contratação de Sérgio Missão.',body)

# ---------------------------------------------------------------- contato e confirmação
offers=[('Palestra Burnout Sem Lados','a palestra Burnout Sem Lados','Solicitar proposta'),('Palestra Desaprenda a Liderar','a palestra Desaprenda a Liderar','Solicitar proposta'),('Palestra A Experiência do Dono','a palestra A Experiência do Dono','Solicitar proposta'),('Mentoria','disponibilidade e valores da mentoria','Consultar disponibilidade e valores'),('Consultoria','consultoria para nossa organização','Solicitar proposta'),('Treinamentos','treinamentos para nossa equipe','Solicitar proposta'),('Cooperativismo','palestras e programas para nossa cooperativa','Solicitar proposta'),('Entrevistas, avaliação e negociação','a preparação para entrevistas, avaliação de desempenho ou negociação','Consultar disponibilidade e valores')]
body=hero('Contato comercial','Vamos conversar sobre o que você precisa.','Escolha o assunto para abrir o WhatsApp com a mensagem já identificada, ou escreva pelo formulário.')
body+=section('Escolha o assunto da conversa','<div class="grid three">'+''.join('<article class="card"><h3>'+E(t)+'</h3>'+cta(s,l)+'</article>' for t,s,l in offers)+'<article class="card"><h3>Livro '+E(LIVRO)+'</h3><p>Lançamento e novidades em '+livro_link('burnei.com.br')+'.</p>'+cta('o livro '+LIVRO,'Perguntar sobre o livro')+'</article></div>')
body+=section('Prefere escrever?','<div class="form-grid"><div><p class="reading">Se ainda não sabe qual serviço pedir, descreva a situação. A resposta indica o caminho e os próximos passos.</p></div>'+contato_form()+'</div>','formulario')
body+=section('Contato direto','<div class="grid two"><div><h3>WhatsApp e e-mail</h3><p>'+link(wa('uma necessidade profissional'),'+55 11 91655-6521')+'</p><p>'+link('mailto:contato@sergiomissao.com.br','contato@sergiomissao.com.br')+'</p></div><div><h3>Agendamento</h3><p>Use a agenda para consultar os horários oferecidos.</p>'+link(AGENDA,'Consultar agenda →',ext=True)+'</div></div>')
body+=section('Dúvidas frequentes',faq([('Como são definidos os valores?','Serviços corporativos recebem proposta conforme objetivo, público e escopo. Para mentoria e preparação individual, consulte disponibilidade e valores pelo contato comercial.'),('Como escolher a palestra?','Conte o objetivo do evento e o perfil do público. A conversa inicial ajuda a relacionar a necessidade ao portfólio. As fichas das palestras trazem tema, público e duração.'),('Qual a diferença entre mentoria e consultoria?','A mentoria trabalha com uma pessoa e suas decisões. A consultoria trabalha com a organização quando um problema se repete entre pessoas ou áreas.'),('Qual a diferença entre mentoria e preparação individual?','A mentoria acompanha desafios ao longo do tempo. A preparação se concentra em uma situação específica, como entrevista ou avaliação de desempenho.')]),'duvidas')
page('contato','Contato e propostas','Solicite uma proposta de palestra, mentoria, consultoria, treinamento ou programa para cooperativas.',body)
page('obrigado','Mensagem enviada','Confirmação de envio de mensagem pelo site.',hero('Mensagem enviada','Obrigado. Sua mensagem chegou.','A resposta vai para o e-mail ou telefone informado. Se for urgente, use o WhatsApp.',cta('a mensagem que acabei de enviar pelo site','Falar pelo WhatsApp')+link('/','Voltar ao início','button secondary')),noindex=True)

# ---------------------------------------------------------------- cooperativismo
CI = 'images/cooperativismo/'
COOP_TALKS = [
 {'id':'a-experiencia-do-dono','title':'A Experiência do Dono','img':CI+'coop-atendimento.jpg','alt':'Ilustração de atendimento em cooperativa: colaboradora conversa com um associado e uma associada à mesa',
  'hook':'Aqui o cliente é dono. Mas ele realmente se sente assim?','public':'Colaboradores, coordenadores e associados.','duration':'60 a 90 minutos. Há versão de 30 minutos para assembleias.',
  'msgs':['O dono que não sabe que é dono','Os pequenos momentos que constroem ou destroem o pertencimento','O papel de cada colaborador na experiência do associado'],
  'acts':[('Ato 1 — O dono que não sabe que é dono','Por que tanta gente usa a cooperativa como se fosse um banco qualquer.'),('Ato 2 — Os pequenos momentos','As situações do dia a dia que constroem ou destroem o pertencimento.'),('Ato 3 — O papel de cada um','O que cada colaborador pode fazer para o associado se sentir dono.')],
  'versions':'30 minutos (assembleias), 60 minutos ou 90 minutos.','ficha':'/palestras/a-experiencia-do-dono/'},
 {'id':'do-nucleo-ao-conselho','title':'Do Núcleo ao Conselho: liderança em todas as cadeiras','img':CI+'coop-roda-conversa.jpg','alt':'Ilustração de roda de conversa entre associados de diferentes idades em um salão',
  'hook':'Representar, decidir e preparar quem vem depois.','public':'Coordenadores, delegados, conselheiros e novas lideranças.','duration':'60 a 90 minutos.',
  'msgs':['Representar não é mandar','A decisão difícil que ninguém aplaude','Preparar quem vem depois'],
  'acts':[('Ato 1 — Representar não é mandar','O papel de quem fala em nome dos associados no núcleo.'),('Ato 2 — A decisão que ninguém aplaude','O peso das escolhas de conselho e como sustentá-las.'),('Ato 3 — Preparar quem vem depois','Sucessão e formação de novas lideranças. Encerramento com o “compromisso de cadeira”, assinado pela plateia.')],
  'versions':'60 minutos ou 90 minutos.','ficha':None},
 {'id':'o-legado-de-amstad','title':'O Legado de Amstad: o que 20 colonos de 1902 ensinam à cooperativa de hoje','img':CI+'coop-serra-gaucha.jpg','alt':'Ilustração de paisagem da Serra Gaúcha com casa em estilo enxaimel, araucárias e estrada de terra',
  'hook':'Crescer sem perder o que torna a cooperativa diferente.','public':'Todos os públicos e eventos de datas cooperativistas.','duration':'45 a 90 minutos.',
  'msgs':['Crescer sem perder a identidade','Confiança como ativo','O que manter e o que mudar'],
  'acts':[('Ato 1 — 1902','Vinte pessoas, uma ata e a primeira cooperativa de crédito da América Latina.'),('Ato 2 — Confiança como ativo','O que sustentou a cooperativa por mais de um século.'),('Ato 3 — O que manter e o que mudar','A pergunta para a cooperativa de hoje: qual capítulo ela está escrevendo.')],
  'versions':'45 minutos, 60 minutos ou 90 minutos. É a palestra que abre o Cooptour.','ficha':None},
]
def wa_coop(item):
    return wa_text('Olá! Gostaria de conversar sobre '+item+' para minha cooperativa. Vim pelo site sergiomissao.com.br.')

def coop_cta(item, form_anchor='/cooperativismo/#conversa'):
    return '<div class="actions"><a class="button" href="'+E(wa_coop(item))+'">Conversar pelo WhatsApp</a>'+link(form_anchor,'Preencher o formulário','button secondary')+'</div>'

def badge(txt='Sob consulta'):
    return '<span class="badge wait">'+E(txt)+'</span>'

def coop_crumb(name):
    return crumbs([('/cooperativismo/','Cooperativismo'),(None,name)])

def coop_sub(slug, name, title, intro, img, alt, problem, who, steps, fmt, deliver, faqs, item, extra='', og=None, ilus_note='Imagem ilustrativa', end=''):
    body = ('<section class="page-hero coop-hero"><div class="wrap">'+coop_crumb(name)+'<div class="hero-grid"><div><p class="eyebrow">Cooperativismo</p><h1>'+E(title)+'</h1><p class="lead">'+E(intro)+'</p>'
            +coop_cta(item)+'</div>'+ilus(img,alt,'hero-art',True,ilus_note)+'</div></div></section>')
    body += section('O problema que resolve','<p class="reading">'+E(problem)+'</p>')
    body += section('Para quem é','<p class="reading">'+E(who)+'</p>')
    body += extra
    body += section('Como funciona',ol(steps))
    body += section('Formato e duração',fmt if fmt.startswith('<') else '<p class="reading">'+E(fmt)+'</p>')
    body += section('O que a cooperativa recebe',ul(deliver))
    body += section('Perguntas frequentes',faq(faqs))
    dep = depoimento()
    if dep: body += '<section class="section"><div class="wrap">'+dep+'</div></section>'
    body += section('Vamos conversar sobre a sua cooperativa','<p class="reading">Conte o público, o objetivo e o período. A conversa inicial define o formato.</p>'+coop_cta(item)+'<p>'+link('/cooperativismo/','← Voltar ao núcleo de Cooperativismo')+'</p>')
    body += end
    page('cooperativismo/'+slug, name+' | Cooperativismo', intro, body, og=og or img, theme='coop', og_alt=alt)

# ---- página principal
chairs = [('Associado','Entendi o que é ser dono sem saber que era.'),('Coordenador de núcleo','Aprendi que representar não é mandar.'),('Conselheiro','Descobri o peso da decisão que ninguém aplaude.'),('Presidente','Vi que liderar é preparar quem vem depois.'),('Executivo de multinacional','Trouxe a régua de resultado sem perder a de propósito.')]
chairs_html = '<ol class="chairs">'+''.join(f'<li class="reveal"><span class="chair-n" aria-hidden="true">{i}</span><h3>{E(c)}</h3><p>“{E(q)}”</p></li>' for i,(c,q) in enumerate(chairs,1))+'</ol>'
timeline = [('1885','O padre jesuíta suíço Theodor Amstad chega ao Brasil.'),('28/12/1902','Em Linha Imperial, Nova Petrópolis/RS, 20 pessoas assinam a ata de fundação da primeira cooperativa de crédito da América Latina, inspirada no modelo de Friedrich Wilhelm Raiffeisen. Hoje ela é a Sicredi Pioneira RS.'),('2010','Nova Petrópolis recebe, pela Lei Federal 12.205/2010, o título de Capital Nacional do Cooperativismo.'),('2019','Padre Amstad é declarado Patrono do Cooperativismo Brasileiro pela Lei 13.926/2019.'),('Hoje','E a sua cooperativa, qual capítulo está escrevendo?')]
timeline_html = '<ol class="timeline">'+''.join(f'<li class="reveal"><time>{E(y)}</time><p>{E(t)}</p></li>' for y,t in timeline)+'</ol>'
def coop_talk_card(t):
    return ('<article class="card coop-card reveal" id="card-'+t['id']+'">'+ilus(t['img'],t['alt'],'card-photo',sizes='(max-width: 700px) 100vw, 33vw')+'<h3>'+E(t['title'])+'</h3><p class="hook">'+E(t['hook'])+'</p>'
            '<dl class="mini"><dt>Público</dt><dd>'+E(t['public'])+'</dd><dt>Duração</dt><dd>'+E(t['duration'])+'</dd></dl>'+ul(t['msgs'])
            +'<div class="card-actions"><a class="button" href="'+E(wa_text('Olá! Quero a palestra '+t['title'].split(':')[0]+' para minha cooperativa. Vim pelo site sergiomissao.com.br.'))+'">Quero esta palestra</a>'
            +link((t['ficha'] or '/cooperativismo/palestras/')+('#ficha' if t['ficha'] else '#'+t['id']),'Ver detalhes →')+'</div></article>')
programs_main = [('Núcleo Forte','/cooperativismo/nucleo-forte/','Formação e reciclagem de coordenadores de núcleo e delegados, em 3 a 4 encontros.',False),
                 ('Jornada de Liderança Cooperativista','/cooperativismo/programas/#jornada-de-lideranca','De 4 a 6 meses, com módulos mensais, mentoria em grupo, projeto aplicado e imersão final.',True),
                 ('Conselho em Ação','/cooperativismo/programas/#conselho-em-acao','Governança, papel do conselho e da diretoria, decisão, ética e sucessão.',True),
                 ('CoopExperience','/cooperativismo/programas/#coopexperience','Vivência de 1 dia na própria cooperativa para sentir a diferença entre banco e cooperativa.',True)]
solutions = [('Associados',[('A Experiência do Dono','/cooperativismo/palestras/#a-experiencia-do-dono'),('O Legado de Amstad','/cooperativismo/palestras/#o-legado-de-amstad'),('Cooptour','/cooperativismo/cooptour/')]),
             ('Núcleo',[('Núcleo Forte','/cooperativismo/nucleo-forte/'),('Do Núcleo ao Conselho','/cooperativismo/palestras/#do-nucleo-ao-conselho')]),
             ('Conselho',[('Conselho em Ação','/cooperativismo/programas/#conselho-em-acao'),('Assembleia Viva','/cooperativismo/assembleia-viva/')]),
             ('Diretoria',[('Mentoria de Dirigentes','/cooperativismo/programas/#mentoria-de-dirigentes'),('Assembleia Viva','/cooperativismo/assembleia-viva/')]),
             ('Equipes',[('CoopExperience','/cooperativismo/programas/#coopexperience'),('Cooperativa que Cuida','/cooperativismo/cooperativa-que-cuida/'),('A Experiência do Dono','/cooperativismo/palestras/#a-experiencia-do-dono')])]
body = ('<section class="page-hero coop-hero main"><div class="wrap"><div class="hero-grid"><div><p class="eyebrow">Cooperativismo de crédito, visto de todas as cadeiras</p><h1>“Do associado ao conselho, eu já sentei em cada cadeira.”</h1>'
        '<p class="lead">Palestras, programas e experiências para cooperativas que querem crescer sem perder o que as torna diferentes.</p><div class="actions">'
        '<a class="button" href="'+E(wa_coop('palestras e programas'))+'">Vamos conversar</a>'+link('#palestras','Ver palestras','button secondary')+'</div></div>'
        +image('foto-palco.jpg','Sérgio Missão falando ao microfone para uma plateia','portrait photo',True)+'</div></div></section>')
body += section('As cadeiras que ocupei','<div class="split">'+ilus(CI+'coop-cadeiras.jpg','Ilustração de cinco cadeiras diferentes lado a lado: de plástico, de madeira simples, estofada, de madeira entalhada e de escritório','side-photo')+'<p class="reading">Cada cadeira mostra a cooperativa de um ângulo diferente.</p></div>'+chairs_html,'cadeiras')
body += section('O Legado de Amstad','<div class="split">'+ilus(CI+'coop-serra-gaucha.jpg','Ilustração de paisagem da Serra Gaúcha com casa em estilo enxaimel, araucárias e estrada de terra','side-photo')+'<p class="reading">Uma história que começa com 20 pessoas e uma ata.</p></div>'+timeline_html,'legado')
body += section('Palestras para cooperativas','<div class="grid three">'+''.join(coop_talk_card(t) for t in COOP_TALKS)+'</div><p class="also">Também disponível: '+link('/cooperativismo/cooperativa-que-cuida/','Burnout Sem Lados – versão cooperativa')+'</p><p>'+link('/cooperativismo/palestras/','Comparar as três palestras, com roteiro e necessidades técnicas →')+'</p>','palestras')
body += ('<section class="section coop-band" id="cooptour"><div class="wrap split-wide"><div><p class="eyebrow">Destaque</p><h2>Cooptour Berço do Crédito</h2><p class="lead">Leve sua equipe ao lugar onde o cooperativismo de crédito da América Latina começou.</p>'
         +link('/cooperativismo/cooptour/','Conhecer o roteiro','button')+'</div>'+ilus(CI+'coop-mapa-cooptour.jpg','Mapa ilustrado do Cooptour com três paradas: Nova Petrópolis, Parque Aldeia do Imigrante e Linha Imperial, 1902','map',note='Mapa ilustrativo, fora de escala.')+'</div></section>')
body += section('Programas','<div class="grid four">'+''.join('<a class="card program reveal" href="'+u+'"><h3>'+E(n)+'</h3><p>'+E(d)+'</p>'+(badge() if b else '<span class="badge ok">Página própria</span>')+'</a>' for n,u,d,b in programs_main)+'</div>','programas')
steps4 = ['Preparar','Ensaiar','Conduzir','Avaliar']
body += section('Assembleia Viva','<div class="split">'+ilus(CI+'coop-assembleia.jpg','Ilustração de assembleia de cooperativa com associados levantando a mão para votar','side-photo')+'<div><p class="reading">Preparação e condução de assembleias e pré-assembleias, com foco em ritmo, clareza e participação.</p><ol class="flow" aria-label="Etapas da Assembleia Viva">'+''.join(f'<li class="reveal"><span>{i}</span>{s}</li>' for i,s in enumerate(steps4,1))+'</ol>'+link('/cooperativismo/assembleia-viva/','Conhecer a Assembleia Viva','button')+'</div></div>','assembleia')
body += section('Cooperativa que Cuida','<div class="split">'+ilus(CI+'coop-cuida.jpg','Ilustração de conversa entre um homem e uma mulher em um café, com o livro BURNEI! E agora? sobre a mesa','side-photo')+'<div><p class="lead">Antes de virar afastamento, o burnout é uma conversa que ninguém teve.</p><p class="reading">O kit une a palestra Burnout Sem Lados, em versão cooperativa, ao livro '+livro_link()+'.</p><div class="actions">'+link('/cooperativismo/cooperativa-que-cuida/','Conhecer o kit','button')+link(BURNEI,'Sobre o livro','button secondary',True)+'</div></div></div>','cuida')
sol_rows = ''.join('<tr><th scope="row">'+E(p)+'</th><td><ul class="chips">'+''.join('<li>'+link(u,n)+'</li>' for n,u in s)+'</ul></td></tr>' for p,s in solutions)
body += section('Qual solução para qual momento','<div class="table-wrap"><table class="solutions"><caption class="sr-only">Soluções indicadas para cada público da cooperativa</caption><thead><tr><th scope="col">Público</th><th scope="col">Soluções</th></tr></thead><tbody>'+sol_rows+'</tbody></table></div>','solucoes')
body += section('Qual conversa a sua cooperativa precisa ter?','<div class="form-grid"><div><p class="reading">Conte quem é o público, o objetivo e o período. A resposta vem com uma sugestão de formato.</p><a class="button" href="'+E(wa_coop('palestras e programas'))+'">Prefiro conversar pelo WhatsApp</a><p class="small">Ou escreva para '+link('mailto:contato@sergiomissao.com.br','contato@sergiomissao.com.br')+'.</p></div>'+coop_form()+'</div>','conversa')
page('cooperativismo','Cooperativismo: palestras, programas e experiências','Do associado ao conselho: palestras, programas e experiências para cooperativas de crédito que querem crescer sem perder o que as torna diferentes.',body,theme='coop',og=CI+'coop-cadeiras.jpg',og_alt='Cinco cadeiras diferentes lado a lado')

# ---- /cooperativismo/palestras/
def coop_talk_detail(t):
    fic = link(t['ficha'],'Abrir a ficha principal da palestra →') if t['ficha'] else ''
    return ('<article class="talk-detail" id="'+t['id']+'"><div class="split">'+ilus(t['img'],t['alt'],'side-photo')+'<div><h3>'+E(t['title'])+'</h3><p class="hook">'+E(t['hook'])+'</p><dl class="mini"><dt>Público</dt><dd>'+E(t['public'])+'</dd><dt>Versões de duração</dt><dd>'+E(t['versions'])+'</dd><dt>Necessidades técnicas</dt><dd>Projetor e microfone. Demais itens combinados com a cooperativa.</dd></dl></div></div>'
            '<h4>Roteiro resumido</h4>'+ol(t['acts'])+'<div class="actions"><a class="button" href="'+E(wa_text('Olá! Quero a palestra '+t['title'].split(':')[0]+' para minha cooperativa. Vim pelo site sergiomissao.com.br.'))+'">Quero esta palestra</a>'+fic+'</div></article>')
cmp = ''.join('<tr><th scope="row">'+link('#'+t['id'],t['title'].split(':')[0])+'</th><td>'+E(t['public'])+'</td><td>'+E(t['duration'])+'</td><td>'+E('; '.join(t['msgs']))+'</td></tr>' for t in COOP_TALKS)
extra = section('Compare as três palestras','<div class="table-wrap"><table class="compare"><thead><tr><th scope="col">Palestra</th><th scope="col">Público</th><th scope="col">Duração</th><th scope="col">Mensagens</th></tr></thead><tbody>'+cmp+'</tbody></table></div>')
extra += '<section class="section"><div class="wrap"><h2>As palestras em detalhe</h2>'+''.join(coop_talk_detail(t) for t in COOP_TALKS)+'<p class="also">A versão cooperativa de '+link('/palestras/burnout-sem-lados/','Burnout Sem Lados')+', “Quem cuida de quem cuida”, faz parte da '+link('/cooperativismo/cooperativa-que-cuida/','Cooperativa que Cuida')+'.</p></div></section>'
coop_sub('palestras','Palestras','Três palestras, três momentos da cooperativa.','Compare A Experiência do Dono, Do Núcleo ao Conselho e O Legado de Amstad: público, duração, roteiro e necessidades técnicas.',CI+'coop-roda-conversa.jpg','Ilustração de roda de conversa entre associados de diferentes idades em um salão',
  'Eventos de cooperativa reúnem públicos muito diferentes: associados, colaboradores, núcleo e conselho. Uma palestra genérica sobre liderança fala a todos e não chega a ninguém. Cada uma destas palestras parte de uma cadeira da cooperativa.',
  'Organizadores de assembleias, encontros de núcleo, convenções, eventos de datas cooperativistas e ações de desenvolvimento em cooperativas de crédito.',
  [('Conversa inicial','Evento, público, data e objetivo.'),('Escolha da palestra','Com base no público e no momento da cooperativa.'),('Ajuste','Exemplos e duração adaptados ao evento.'),('Palestra','No evento, presencial.'),('Retorno','Conversa com a organização depois do evento.')],
  'De 30 a 90 minutos, conforme a palestra e o evento. Versão de 30 minutos de A Experiência do Dono para assembleias.',
  ['Palestra ajustada ao público e ao evento','Ficha da palestra para divulgação interna','Material de apoio para o organizador, quando previsto na proposta'],
  [('Qual palestra serve para uma assembleia?','A Experiência do Dono tem versão de 30 minutos para assembleias. O Legado de Amstad funciona bem em datas cooperativistas.'),('Dá para combinar uma palestra com um programa?','Sim. Do Núcleo ao Conselho costuma abrir o Núcleo Forte, e O Legado de Amstad abre o Cooptour.'),('Há citação de marcas de cooperativas?','Não. As palestras falam de situações e de história, sem usar logos ou marcas de sistemas cooperativos.')],
  'as palestras para cooperativas', extra)

# ---- núcleo forte
coop_sub('nucleo-forte','Núcleo Forte','Núcleo Forte: formação de coordenadores de núcleo e delegados.','Formação e reciclagem de coordenadores de núcleo e delegados, em 3 a 4 encontros.',CI+'coop-roda-conversa.jpg','Ilustração de roda de conversa entre associados de diferentes idades em um salão',
  'O coordenador de núcleo é a ponte entre o associado e a cooperativa, mas costuma assumir o papel sem preparo para conduzir reuniões, ouvir o quadro social e mobilizar para as assembleias.',
  'Coordenadores de núcleo, delegados e associados que vão assumir essas funções.',
  [('Alinhamento','Conversa com a cooperativa sobre o quadro de núcleos e o momento.'),('Encontros','De 3 a 4 encontros com os temas do programa.'),('Prática','Exercícios a partir das reuniões reais de cada núcleo.'),('Plano','Cada núcleo sai com seu plano de ação.')],
  '<p class="reading">De 3 a 4 encontros. Temas:</p>'+ul(['Papel do coordenador','Condução de reuniões de núcleo','Comunicação com associados','Mobilização e preparação para assembleias','Escuta do quadro social']),
  ['Material de apoio','Roteiro-modelo de reunião de núcleo','Plano de ação por núcleo'],
  [('O programa pode começar com uma palestra?','Sim. Do Núcleo ao Conselho é a palestra indicada para abrir o programa.'),('Serve para reciclagem de quem já é coordenador?','Sim. O programa atende formação e reciclagem.'),('Os encontros podem acontecer em cidades diferentes?','O formato e a logística são definidos na proposta, conforme a distribuição dos núcleos.')],
  'o programa Núcleo Forte')

# ---- assembleia viva
aviso = '<aside class="notice" role="note"><strong>Importante.</strong> “A presidência da assembleia e a condução formal das deliberações seguem o estatuto da cooperativa. Atuo como apresentador e facilitador, cuidando de ritmo, clareza e participação.”</aside>'
coop_sub('assembleia-viva','Assembleia Viva','Assembleia Viva: assembleias com ritmo, clareza e participação.','Preparação e condução de assembleias e pré-assembleias.',CI+'coop-assembleia.jpg','Ilustração de assembleia de cooperativa com associados levantando a mão para votar',
  'Assembleias longas, slides de resultado difíceis de entender e pouca participação afastam o associado do momento mais importante da vida cooperativa.',
  'Presidentes, diretorias, conselhos e áreas de relacionamento que organizam AGO, AGE, pré-assembleias e assembleias de núcleo.',
  [('Preparar','Revisão do roteiro, da pauta e da linguagem dos slides de resultados.'),('Ensaiar','Ensaio com presidente e relatores, com orientação de oratória.'),('Conduzir','Apresentação e facilitação no dia, cuidando de ritmo e participação.'),('Avaliar','Relatório pós-evento com o que funcionou e o que ajustar.')],
  '<p class="reading">Formatos disponíveis:</p>'+ul(['Condução da AGO/AGE','Circuito de pré-assembleias ou assembleias de núcleo','Assembleia com palestra','Pacote completo: revisão de roteiro e pauta, linguagem dos slides de resultados, ensaio com presidente e relatores, orientação de oratória e relatório pós-evento']),
  ['Roteiro revisado','Orientações sobre a linguagem dos slides de resultados','Ensaio com presidente e relatores (no pacote completo)','Relatório pós-evento (no pacote completo)'],
  [('Quem preside a assembleia?','A presidência e a condução formal das deliberações seguem o estatuto da cooperativa. O trabalho é de apresentação e facilitação.'),('Dá para contratar só a palestra?','Sim. A assembleia com palestra é um dos formatos; A Experiência do Dono tem versão de 30 minutos.'),('Atende circuito de pré-assembleias?','Sim. O circuito de pré-assembleias ou assembleias de núcleo é um dos formatos.')],
  'a Assembleia Viva', section('Limites de atuação',aviso))

# ---- cooptour
coop_sub('cooptour','Cooptour','Cooptour Berço do Crédito: uma visita técnica à origem.','Visita técnica de 1 a 2 dias a Nova Petrópolis/RS, onde o cooperativismo de crédito da América Latina começou.',CI+'coop-mapa-cooptour.jpg','Mapa ilustrado do Cooptour com três paradas: Nova Petrópolis, Parque Aldeia do Imigrante e Linha Imperial, 1902',
  'Equipes e associados conhecem a história do cooperativismo por slides. Estar no lugar onde 20 pessoas assinaram a ata de 1902 muda a forma de entender confiança, propósito e identidade.',
  'Grupos de colaboradores, conselheiros, delegados e associados de cooperativas.',
  [('Nova Petrópolis','Chegada e abertura com a palestra O Legado de Amstad.'),('Parque Aldeia do Imigrante','Visita à sede histórica da antiga caixa rural, restaurada em 2019.'),('Linha Imperial','Visita ao local da fundação, em 1902.'),('Compromisso de legado','Dinâmica de grupo e assinatura do “compromisso de legado”, em referência à ata de 1902.')],
  '<p class="reading">De 1 a 2 dias, em Nova Petrópolis/RS. Inclui:</p>'+ul(['A palestra O Legado de Amstad no local','Uma dinâmica de grupo','Um “compromisso de legado” assinado pelo grupo, em referência à ata de 1902'])+'<aside class="notice" role="note">Logística, transporte e hospedagem podem ser organizados com agência parceira.</aside>',
  ['Roteiro da visita','Palestra O Legado de Amstad no local','Dinâmica de grupo','Compromisso de legado assinado pelo grupo'],
  [('Quantos dias dura?','De 1 a 2 dias, conforme o roteiro combinado.'),('Transporte e hospedagem estão incluídos?','Logística, transporte e hospedagem podem ser organizados com agência parceira.'),('O mapa mostra distâncias reais?','Não. O mapa é ilustrativo e está fora de escala.')],
  'o Cooptour Berço do Crédito',
  '<section class="section coop-band"><div class="wrap"><p class="eyebrow">Em breve</p><h2>Cooptour Internacional</h2><p class="reading">Um roteiro seguindo as origens do modelo Raiffeisen na Alemanha.</p></div></section>',
  ilus_note='Mapa ilustrativo, fora de escala.')

# ---- programas
progs = [('jornada-de-lideranca','Jornada de Liderança Cooperativista','De 4 a 6 meses, com módulos mensais, mentoria em grupo, projeto aplicado e imersão final.',None),
         ('conselho-em-acao','Conselho em Ação','Governança, papel do conselho e da diretoria, tomada de decisão, ética e sucessão, para Conselhos de Administração e Fiscal.',None),
         ('coopexperience','CoopExperience','Vivência imersiva de 1 dia na própria cooperativa, para colaboradores novos ou equipes sentirem na prática a diferença entre um banco e uma cooperativa.',CI+'coop-experience.jpg'),
         ('mentoria-de-dirigentes','Mentoria de Dirigentes','Acompanhamento individual de presidentes, diretores e conselheiros recém-eleitos.',None)]
prog_html = '<section class="section"><div class="wrap"><h2>Os programas</h2><div class="grid two">'+''.join(
    '<article class="card program-detail" id="'+i+'">'+(ilus(img,'Ilustração de equipe de cooperativa em dinâmica com notas adesivas na parede','card-photo') if img else '')+'<h3>'+E(n)+'</h3>'+badge()+'<p>'+E(d)+'</p>'
    +('<p>'+link('/mentoria/#dirigentes','Detalhes na página de Mentoria →')+'</p>' if i=='mentoria-de-dirigentes' else '')
    +'<a class="button" href="'+E(wa_coop('o programa '+n))+'">Consultar '+E(n)+'</a></article>' for i,n,d,img in progs)+'</div></div></section>'
coop_sub('programas','Programas','Programas para cada cadeira da cooperativa.','Jornada de Liderança Cooperativista, Conselho em Ação, CoopExperience e Mentoria de Dirigentes. Todos sob consulta.',CI+'coop-experience.jpg','Ilustração de equipe de cooperativa em dinâmica com notas adesivas na parede',
  'Formar lideranças, preparar conselhos e mostrar às equipes o que torna uma cooperativa diferente de um banco exige mais do que um evento isolado.',
  'Diretorias, conselhos, áreas de pessoas e de relacionamento de cooperativas de crédito.',
  [('Conversa inicial','Objetivo, público e momento da cooperativa.'),('Escolha do programa','Com base no público: liderança, conselho, equipes ou dirigentes.'),('Proposta','Escopo, cronograma e entregas definidos por escrito.'),('Execução','Conforme o formato de cada programa.')],
  'Jornada de Liderança Cooperativista: 4 a 6 meses. CoopExperience: 1 dia. Conselho em Ação e Mentoria de Dirigentes: formato definido na proposta. Todos sob consulta.',
  ['Programa desenhado para o público escolhido','Cronograma e entregas definidos na proposta','Para a Jornada: projeto aplicado e imersão final'],
  [('Por que “sob consulta”?','Escopo, duração e condições dependem do público e do momento da cooperativa, e são definidos na proposta.'),('Os programas atendem Conselho Fiscal?','Conselho em Ação é voltado a Conselhos de Administração e Fiscal.'),('A CoopExperience acontece onde?','Na própria cooperativa, em 1 dia.')],
  'os programas para cooperativas', prog_html)

# ---- cooperativa que cuida
cvv = '<aside class="notice care" role="note">Se você está em sofrimento agora, fale com alguém: CVV, ligue 188 (gratuito, 24 horas) ou acesse '+link('https://cvv.org.br','cvv.org.br',ext=True)+'.</aside>'
coop_sub('cooperativa-que-cuida','Cooperativa que Cuida','Cooperativa que Cuida: antes de virar afastamento, o burnout é uma conversa que ninguém teve.','Palestra Burnout Sem Lados em versão cooperativa, livro BURNEI! E agora? para as lideranças e roda de conversa.',CI+'coop-cuida.jpg','Ilustração de conversa entre um homem e uma mulher em um café, com o livro BURNEI! E agora? sobre a mesa',
  'Quem atende o associado também se desgasta. Quando a pressão não vira conversa, ela vira afastamento.',
  'Lideranças e equipes de cooperativas, especialmente áreas de atendimento e gestão de pessoas.',
  [('Palestra','Burnout Sem Lados, versão cooperativa: “Quem cuida de quem cuida”.'),('Livro','Exemplares de BURNEI! E agora? para as lideranças.'),('Roda de conversa','Conversa a partir do livro, com as lideranças.')],
  'Palestra de 60 a 90 minutos e roda de conversa, com datas combinadas na proposta.',
  ['Palestra “Quem cuida de quem cuida”','Exemplares do livro BURNEI! E agora? para as lideranças','Roda de conversa a partir do livro'],
  [('O kit substitui acompanhamento de saúde?','Não. É uma ação de conscientização e conversa. Casos de sofrimento devem ser acompanhados por profissionais de saúde.'),('Onde conheço o livro?','No site do livro, burnei.com.br.'),('A palestra também existe fora do cooperativismo?','Sim. Burnout Sem Lados é a palestra principal, com ficha própria.')],
  'o kit Cooperativa que Cuida',
  section('O kit','<div class="grid three"><article class="card"><h3>Palestra</h3><p>Burnout Sem Lados, versão cooperativa: “Quem cuida de quem cuida”.</p>'+link('/palestras/burnout-sem-lados/','Ficha da palestra principal →')+'</article><article class="card"><h3>Livro</h3><p>Exemplares de '+livro_link()+' para as lideranças.</p>'+link(BURNEI,'Conhecer em burnei.com.br →',ext=True)+'</article><article class="card"><h3>Roda de conversa</h3><p>Conversa com as lideranças a partir do livro.</p></article></div>'), end='<section class="section"><div class="wrap">'+cvv+'</div></section>')


# ---------------------------------------------------------------- artigos, posts e conteúdos
editorial = json.loads((OUT / 'data/editorial.json').read_text())
articles = editorial['artigos']
posts = editorial['posts']
assert articles and posts, 'Conteúdo editorial ausente'
TEMAS = ['Liderança e gestão','Pessoas e trabalho','Cultura e relacionamento','Cooperativismo e governança','Carreira e decisões']
TEMA_PADRAO = 'Liderança e gestão'
SERVICO_TEMA = {
 'Liderança e gestão':('/palestras/desaprenda-a-liderar/','Palestra Desaprenda a Liderar','/mentoria/#mentoria','Mentoria executiva'),
 'Pessoas e trabalho':('/palestras/burnout-sem-lados/','Palestra Burnout Sem Lados','/consultoria/','Consultoria'),
 'Cultura e relacionamento':('/consultoria/','Consultoria','/palestras/a-experiencia-do-dono/','Palestra A Experiência do Dono'),
 'Cooperativismo e governança':('/cooperativismo/programas/#conselho-em-acao','Conselho em Ação','/cooperativismo/','Núcleo de Cooperativismo'),
 'Carreira e decisões':('/mentoria/','Mentoria','/decisor-por-um-dia/','Decisor por um Dia'),
}
def tema(x): return x.get('tema') if x.get('tema') in TEMAS else TEMA_PADRAO
def slugify(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def datebr(d):
    y,m,dd = d.split('-'); return f'{dd}/{m}/{y}'
for p in posts: p['_id'] = 'post-'+slugify(p['titulo'])

def related(a):
    same = [x for x in articles if x is not a and tema(x)==tema(a)]
    other = [x for x in articles if x is not a and x not in same]
    return (same+other)[:2]

for a in articles:
    s1u,s1n,s2u,s2n = SERVICO_TEMA[tema(a)]
    rel = ''.join('<li>'+link('/artigos/'+r['slug']+'/',r['titulo'])+'</li>' for r in related(a))
    nxt = ('<div class="grid two next"><div><h3>Leia também</h3><ul>'+rel+'</ul>'+link('/conteudos/','Todos os conteúdos →')+'</div>'
           '<div><h3>Quando o tema é com a sua equipe</h3><p>Este texto fala de '+E(tema(a).lower())+'. Conheça o trabalho relacionado:</p><ul><li>'+link(s1u,s1n)+'</li><li>'+link(s2u,s2n)+'</li></ul></div></div>')
    page('artigos/'+a['slug'],a['titulo'],a['resumo'],hero(a['tipo'],a['titulo'],a['resumo'],'',image(a['imagem'],a.get('imagemAlt',''),'hero-art',True) if a.get('imagem') else '',crumbs([('/conteudos/','Conteúdos'),('/artigos/','Artigos'),(None,a['titulo'])]))
         +'<article class="wrap reading prose"><p class="meta">Sérgio Missão · <time datetime="'+a['data']+'">'+datebr(a['data'])+'</time> · '+E(tema(a))+'</p>'+rich(a['texto'])+'<p>'+link(a['original'],'Ver publicação original no LinkedIn →',ext=True)+'</p></article>'
         +section('Continue a leitura',nxt), og=a['imagem'] if a.get('imagem','').endswith('.jpg') else 'foto-palco.jpg')

def articlecards(items):
    return '<div class="grid three">'+''.join('<article class="card card-light">'+(image(a['imagem'],a.get('imagemAlt',''),'cover-image') if a.get('imagem') else '')+'<p class="eyebrow">'+E(a['tipo'])+'</p><h3>'+link('/artigos/'+a['slug']+'/',a['titulo'])+'</h3><p>'+E(a['resumo'])+'</p><time datetime="'+a['data']+'">'+datebr(a['data'])+'</time></article>' for a in items)+'</div>'
page('artigos','Artigos e O Lado B da Liderança','Artigos e edições da newsletter de Sérgio Missão, preservados na íntegra.',hero('Artigos e newsletter','O Lado B da Liderança','Decisões, relações e aprendizados sobre o trabalho e a liderança.',link('https://www.linkedin.com/newsletters/o-lado-b-da-lideran%C3%A7a-7498454209936203776/','Assinar no LinkedIn','button',True),image('img/series/o-lado-b-da-lideranca.jpg','O Lado B da Liderança: autoridade se recebe no primeiro dia, legitimidade se renova todo dia','hero-art',True),crumbs([('/conteudos/','Conteúdos'),(None,'Artigos')]))+section('Todos os artigos',articlecards(articles))+section('Mais reflexões',link('/posts/','Ler os posts →')+' · '+link('/conteudos/','Buscar por tema →')),og='img/series/o-lado-b-da-lideranca.jpg')
page('posts','Posts de Sérgio Missão','Textos publicados por Sérgio Missão sobre liderança, cultura, relacionamento e cooperativismo.',hero('Redes sociais','Reflexões do dia a dia.','Posts de Sérgio Missão, com acesso à publicação original.','','',crumbs([('/conteudos/','Conteúdos'),(None,'Posts')]))+'<div class="wrap reading prose">'+''.join('<article id="'+p['_id']+'"><h2>'+E(p['titulo'])+'</h2><p class="meta">'+datebr(p['data'])+' · '+E(tema(p))+'</p>'+(image(p['imagem'],p.get('imagemAlt',''),'post-image') if p.get('imagem','').startswith('img/linkedin/') else '')+'<details><summary>Ler o texto completo</summary>'+rich(p['texto'])+'</details>'+link(p['link'],'Ver no LinkedIn →',ext=True)+'</article>' for p in posts)+'</div>')

# rodadas da série, lidas da própria página (o Site Upd acrescenta rodadas lá)
qvc_path = OUT/'quem-voce-contrataria/index.html'
qvc_html = qvc_path.read_text(encoding='utf-8')
rounds = re.findall(r'<li><a href="#([a-z0-9-]+)"><small>(Rodada \d+)</small><strong>([^<]+)', qvc_html)

items = []
for a in articles: items.append((a['data'],'Artigo',tema(a),a['titulo'],a['resumo'],'/artigos/'+a['slug']+'/'))
for p in posts:
    resumo = re.sub(r'\s+',' ',p['texto']).strip()[:150].rsplit(' ',1)[0]+'…'
    items.append((p['data'],'Post',tema(p),p['titulo'],resumo,'/posts/#'+p['_id']))
for anchor,rn,cargo in rounds:
    items.append(('','Série',CD_ := 'Carreira e decisões','Quem você contrataria? — '+rn+': '+cargo.strip(),'Personagens famosos disputam a vaga. Quem você contrataria e por quê?','/quem-voce-contrataria/#'+anchor))
items.append(('','Série','Liderança e gestão','O Lado B da Liderança (newsletter)','Todas as edições da newsletter, preservadas na íntegra.','/artigos/'))
items.append(('','Experiência','Carreira e decisões','Decisor por um Dia','Método para preparar entrevistas, avaliações e negociações pensando como quem decide.','/decisor-por-um-dia/'))
items.append(('','Experiência','Carreira e decisões','Como funciona a simulação de entrevista','Passo a passo e agenda da simulação, com Sérgio no papel de entrevistador.','/como-funciona-simulacao-entrevista/'))
dated = sorted([i for i in items if i[0]], key=lambda i:i[0], reverse=True)
undated = [i for i in items if not i[0]]
FORMATOS = ['Artigo','Post','Série','Experiência']
def item_html(i):
    d,f,t,ti,re_,u = i
    return ('<li class="c-item" data-formato="'+E(f)+'" data-tema="'+E(t)+'"><p class="c-meta"><span class="badge">'+E(f)+'</span> '+E(t)+((' · <time datetime="'+d+'">'+datebr(d)+'</time>') if d else '')+'</p>'
            '<h3>'+link(u,ti)+'</h3><p>'+E(re_)+'</p></li>')
filters = ('<form class="filters" role="search" aria-label="Filtrar conteúdos" hidden><div class="field"><label for="busca">Buscar por título ou tema</label><input id="busca" type="search" autocomplete="off" placeholder="Ex.: assembleia, burnout, entrevista"></div>'
           '<div class="field"><label for="f-formato">Formato</label><select id="f-formato"><option value="">Todos</option>'+''.join('<option>'+f+'</option>' for f in FORMATOS)+'</select></div>'
           '<div class="field"><label for="f-tema">Tema</label><select id="f-tema"><option value="">Todos</option>'+''.join('<option>'+E(t)+'</option>' for t in TEMAS)+'</select></div>'
           '<button class="button secondary" type="reset">Limpar</button></form><p class="c-count" role="status" aria-live="polite"></p>'
           '<p class="c-empty" hidden>Nenhum conteúdo encontrado. Tente outra palavra ou '+link('/conteudos/','veja todos os conteúdos')+'.</p>')
quick = ('<div class="grid four">'+''.join('<a class="card program" href="'+u+'"><h3>'+E(n)+'</h3><p>'+E(d)+'</p></a>' for n,u,d in [
    ('O Lado B da Liderança','/artigos/',str(len(articles))+' artigos e edições da newsletter'),('Posts','/posts/',str(len(posts))+' reflexões do dia a dia'),
    ('Quem você contrataria?','/quem-voce-contrataria/',str(len(rounds))+' rodadas da série'),('Decisor por um Dia','/decisor-por-um-dia/','Método e simulação de entrevista')])+'</div>')
body = hero('Conteúdos','Textos, séries e experiências.','Artigos da newsletter O Lado B da Liderança, posts, a série Quem você contrataria? e o método Decisor por um Dia. Filtre por tema e formato.','')
body += section('Por onde começar',quick,'formatos')
body += section('Todos os conteúdos',filters+'<ul class="c-list" id="lista">'+''.join(item_html(i) for i in dated+undated)+'</ul>','todos')
page('conteudos','Conteúdos de Sérgio Missão','Artigos, posts, a série Quem você contrataria? e o método Decisor por um Dia, com busca por tema e formato.',body,og='img/series/o-lado-b-da-lideranca.jpg')

# ---------------------------------------------------------------- home
body = ('<section class="home-hero"><div class="wrap hero-grid"><div><h1>Sérgio Missão <span>Palestrante, mentor e consultor</span></h1>'
        '<p class="lead">De uma convenção de vendas a uma reunião de conselho, o trabalho começa pela conversa que precisa acontecer. Conheça as palestras, a mentoria executiva e os projetos de consultoria.</p>'
        '<div class="actions">'+link('/palestras/','Escolher uma palestra','button')+link('/contato/','Conversar sobre minha demanda','button secondary')+'</div>'
        '<p class="quick">'+link('/mentoria/','Mentoria →')+link('/consultoria/','Consultoria →')+link('/cooperativismo/','Cooperativismo →')+'</p></div>'
        +image('foto-palco.jpg','Sérgio Missão falando ao microfone para uma plateia','stage',True,'(max-width: 700px) 100vw, 45vw')+'</div></section>')
sits = [('Estou montando a programação de um evento','Compare as palestras, abra a ficha e encaminhe ao comitê. Biografia e fotos estão prontas para divulgação.',[('/palestras/','Ver as palestras'),('/organizadores/','Material para organizadores')]),
        ('Preciso discutir uma decisão como líder','Mentoria executiva para quem assumiu mais responsabilidade, mudou de cargo ou tem uma conversa decisiva pela frente.',[('/mentoria/','Conhecer a mentoria'),('/mentoria/#entrevistas','Entrevistas, avaliação e negociação')]),
        ('Minha equipe enfrenta um problema que se repete','Consultoria com diagnóstico e acompanhamento quando a questão está entre pessoas e áreas, não em uma pessoa só.',[('/consultoria/','Conhecer a consultoria'),('/consultoria/#diagnostico','Como funciona o diagnóstico')])]
body += section('Por onde começar','<div class="grid three situations">'+''.join('<article class="card situation reveal"><p class="eyebrow">Situação '+str(i)+'</p><h3>“'+E(t)+'”</h3><p>'+E(d)+'</p><div class="card-actions">'+link(l[0][0],l[0][1],'button')+link(l[1][0],l[1][1]+' →')+'</div></article>' for i,(t,d,l) in enumerate(sits,1))+'</div>'
        '<p class="also">Quando a necessidade é desenvolver uma habilidade em grupo, como liderança, comunicação ou negociação, os '+link('/treinamentos/','treinamentos')+' são o formato indicado.</p>','servicos')
body += section('Palestras para o seu próximo encontro',talkcards()+'<p>'+link('/palestras/#fichas','Fichas para encaminhar ao comitê →')+'</p>','palestras')
body += section('Mentoria e consultoria','<div class="grid two"><article class="card"><p class="eyebrow">Para uma pessoa</p><h3>Mentoria</h3><p>Mentoria executiva, mentoria de dirigentes e preparação para entrevistas, avaliação de desempenho e negociação. Parte da experiência como diretor em multinacional.</p>'+link('/mentoria/','Conhecer a mentoria →')+'</article>'
        '<article class="card"><p class="eyebrow">Para a organização</p><h3>Consultoria</h3><p>Diagnóstico, acompanhamento e treinamento para desafios de liderança, comunicação e cultura em empresas e cooperativas.</p>'+link('/consultoria/','Conhecer a consultoria →')+'</article></div>','mentoria-consultoria')
body += ('<section class="section coop-band" id="cooperativismo"><div class="wrap"><p class="eyebrow">Cooperativismo de crédito</p><h2>Cooperativas: propósito vivido no dia a dia</h2>'
         '<p class="reading">De associado a presidente de cooperativa: a experiência de todas as cadeiras aplicada a palestras, programas, assembleias e ao Cooptour.</p>'
         '<ol class="path">'+''.join('<li>'+E(c)+'</li>' for c in ['Associado','Coordenador de núcleo','Conselheiro','Presidente'])+'</ol>'
         +link('/cooperativismo/','Conhecer o núcleo de Cooperativismo','button')+'</div></section>')
body += section('Organizando um evento?','<p class="reading">Biografias, fotos, fichas das palestras e contato comercial reunidos para encaminhar ao comitê.</p>'+link('/organizadores/','Acessar materiais para organizadores →'),'organizadores')
body += section('O Lado B da Liderança',articlecards(articles[:3])+'<p>'+link('/artigos/','Todos os artigos →')+' · '+link('/conteudos/','Todos os conteúdos →')+'</p>','lado-b')
body += section('Prepare-se para a conversa que decide','<p class="reading">Entrevistas, avaliação de desempenho e negociação têm algo em comum: alguém vai pesar o que você entrega. O método Decisor por um Dia ajuda a se preparar pensando como quem decide.</p><div class="actions">'+link('/decisor-por-um-dia/','Conhecer o método','button')+link('/decisor-por-um-dia/#entrevistas','Entrevistas','button secondary')+link('/decisor-por-um-dia/#avaliacao','Avaliação de desempenho','button secondary')+link('/decisor-por-um-dia/#negociacao','Negociação','button secondary')+'</div>','preparacao')
body += '<section class="section" id="quem-voce-contrataria"><div class="wrap">'+serie_quem()+'</div></section>'
body += section('Qual conversa sua organização precisa ter?','<p class="reading">Conte o objetivo, o público e o momento da equipe. A partir disso, o trabalho é alinhado.</p><div class="actions">'+cta('uma proposta para nossa organização','Conversar pelo WhatsApp')+link('/contato/#formulario','Escrever pelo formulário','button secondary')+'</div>','fale')
page('','Palestrante, mentor e consultor','Sérgio Missão: palestras, mentoria executiva e consultoria em liderança, comunicação, governança e cultura, para empresas e cooperativas.',body)

# ---------------------------------------------------------------- série: cabeçalho e rodapé comuns
qvc_head = ('<!-- cabecalho-comum:inicio (gerado por scripts/build_site.py) -->'
            '<header class="header"><div class="wrap qvc-top"><a class="brand" href="/"><img class="logo" src="../logo-sm.png" alt="" width="38" height="32"><span>Sérgio Missão</span><span class="tag">#NaMissão</span></a>'
            '<nav class="qvc-nav" aria-label="Principal">'+''.join(f'<a href="/{s}/"'+(' aria-current="page"' if s=='conteudos' else '')+f'>{n}</a>' for s,n in NAV)+'<a class="qvc-cta" href="/contato/">Conversar com Sérgio</a></nav></div>'
            '<p class="wrap qvc-crumb"><a href="/conteudos/">Conteúdos</a> › Quem você contrataria?</p></header>'
            '<style>.qvc-top{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;justify-content:space-between}.qvc-nav{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center}.qvc-nav a{text-decoration:none;font-size:.92rem;color:inherit;padding:6px 0}.qvc-nav a[aria-current]{text-decoration:underline;text-decoration-thickness:2px}.qvc-nav .qvc-cta{background:#A9512A;color:#fff;border-radius:32px;padding:8px 16px;font-weight:600}.qvc-crumb{font-size:.85rem;margin-top:8px}.qvc-foot{display:flex;flex-wrap:wrap;gap:8px 20px}</style>'
            '<!-- cabecalho-comum:fim -->')
qvc_foot = ('<!-- rodape-comum:inicio (gerado por scripts/build_site.py) -->'
            '<footer class="footer"><div class="wrap"><p class="qvc-foot"><a href="/palestras/">Palestras</a><a href="/mentoria/">Mentoria</a><a href="/consultoria/">Consultoria</a><a href="/treinamentos/">Treinamentos</a><a href="/cooperativismo/">Cooperativismo</a><a href="/organizadores/">Para organizadores</a><a href="/contato/">Contato</a></p>'
            '<p><a href="'+E(wa('uma proposta'))+'">WhatsApp: +55 11 91655-6521</a> · <a href="mailto:contato@sergiomissao.com.br">contato@sergiomissao.com.br</a> · <a href="https://www.linkedin.com/in/missao" target="_blank" rel="noopener">LinkedIn</a> · <a href="https://www.instagram.com/sergio.missao" target="_blank" rel="noopener">Instagram</a></p>'
            '<p>© <span id="ano">2026</span> Sérgio Missão · #NaMissão</p></div></footer><!-- rodape-comum:fim -->')
if '<!-- cabecalho-comum:inicio' in qvc_html:
    qvc_html = re.sub(r'<!-- cabecalho-comum:inicio.*?<!-- cabecalho-comum:fim -->', lambda m: qvc_head, qvc_html, flags=re.S)
    qvc_html = re.sub(r'<!-- rodape-comum:inicio.*?<!-- rodape-comum:fim -->', lambda m: qvc_foot, qvc_html, flags=re.S)
else:
    qvc_html = re.sub(r'<header class="header">.*?</header>', lambda m: qvc_head, qvc_html, count=1, flags=re.S)
    qvc_html = re.sub(r'<footer class="footer">.*?</footer>', lambda m: qvc_foot, qvc_html, count=1, flags=re.S)
qvc_path.write_text(qvc_html, encoding='utf-8')

# ---------------------------------------------------------------- arquivos de apoio
old = OUT/'cooperativas/index.html'
if old.exists(): old.unlink()
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+('/'+p+'/' if p else '/')+'</loc></url>' for p in [*pages,'quem-voce-contrataria'])+'</urlset>\n')
write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
write('404.html','<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Página não encontrada | Sérgio Missão</title><meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/site.css"></head><body><main class="wrap prose"><h1>Página não encontrada</h1><p>O endereço pode ter mudado. Continue pelos caminhos abaixo ou entre em contato.</p><p><a class="button" href="/">Página inicial</a> <a class="button secondary" href="/palestras/">Palestras</a> <a class="button secondary" href="/conteudos/">Conteúdos</a> <a class="text-link" href="/contato/">Contato</a></p></main></body></html>')
write('_redirects','/index.html / 301\n/cooperativas /cooperativismo/ 301\n/cooperativas/ /cooperativismo/ 301\n/cooperativas/index.html /cooperativismo/ 301\n/entrevistas /mentoria/#entrevistas 301\n/avaliacao /mentoria/#avaliacao 301\n/negociacao /mentoria/#negociacao 301\n/apresentacoes / 301\n/preparacao-entrevistas /mentoria/#entrevistas 301\n/palestra-burnout /palestras/burnout-sem-lados/ 301\n/palestra-desaprenda /palestras/desaprenda-a-liderar/ 301\n/palestra-dono /palestras/a-experiencia-do-dono/ 301\n')
for p in posts: p.pop('_id', None)
write('data/editorial.json',json.dumps({'artigos':articles,'posts':posts},ensure_ascii=False,indent=2))
print(json.dumps({'preview':PREVIEW,'pages':len(pages),'noindex':sorted(noindex_pages),'articles':len(articles),'posts':len(posts),'rounds':len(rounds)},ensure_ascii=False))
