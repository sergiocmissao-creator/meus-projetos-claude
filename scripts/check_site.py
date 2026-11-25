from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json, xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]/'sergiomissao-site'
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.links=[];self.assets=[];self.h1=0;self.canonical=[];self.descriptions=[];self.alt_errors=[];self.title=False
        self.og_image=[];self.forms=[];self.inputs=[];self.labels=[];self.headings=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='title':self.title=True
        if tag=='a':self.links.append(a.get('href',''))
        if tag in ('img','script') and a.get('src'):self.assets.append(a['src'])
        if tag=='img' and 'alt' not in a:self.alt_errors.append(a.get('src'))
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='link' and a.get('rel')=='stylesheet':self.assets.append(a['href'])
        if tag=='meta' and a.get('name')=='description':self.descriptions.append(a.get('content',''))
        if tag=='meta' and a.get('property')=='og:image':self.og_image.append(a.get('content',''))
        if tag=='form':self.forms.append(a)
        if tag in ('input','select','textarea') and a.get('type') not in ('hidden',) and a.get('name')!='bot-field':self.inputs.append(a.get('id'))
        if tag=='label' and a.get('for'):self.labels.append(a['for'])
        if tag in ('h1','h2','h3','h4'):self.headings.append(int(tag[1]))

files=list(root.rglob('*.html'));parsed={p:Page(p.read_text()) for p in files};errors=[];link_count=0
for p,doc in parsed.items():
    new=p.name!='404.html' and 'quem-voce-contrataria' not in p.parts
    if new:
        if doc.h1!=1:errors.append(f'{p}: {doc.h1} h1')
        if len(doc.canonical)!=1 or len(doc.descriptions)!=1:errors.append(f'{p}: metadata')
        if not doc.title:errors.append(f'{p}: title')
        if doc.alt_errors:errors.append(f'{p}: missing alt {doc.alt_errors}')
        duplicates=[x for x,n in Counter(doc.ids).items() if n>1]
        if duplicates:errors.append(f'{p}: duplicate ids {duplicates}')
    for href in doc.links+doc.assets:
        link_count+=1
        if not href or href=='#':
            if new: errors.append(f'{p}: empty href/src')
            continue
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        dest=(root/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else (p.parent/unquote(u.path) if u.path else p)
        dest=dest.resolve()
        if dest.is_dir():dest=dest/'index.html'
        if not dest.exists():errors.append(f'{p.relative_to(root)}: missing {href}')
        elif u.fragment and dest in parsed and u.fragment not in parsed[dest].ids:
            # Root hash compatibility is provided by site.js.
            if dest!=root/'index.html':errors.append(f'{p.relative_to(root)}: missing anchor {href}')

    if new:
        if len(doc.og_image)!=1:errors.append(f'{p}: og:image')
        else:
            og=urlsplit(doc.og_image[0]).path.lstrip('/')
            if not (root/og).is_file():errors.append(f'{p}: og:image inexistente {og}')
        for f in doc.forms:
            if f.get('role')=='search':continue
            if f.get('data-netlify')!='true' or not f.get('name') or f.get('netlify-honeypot')!='bot-field':errors.append(f'{p}: formulário sem Netlify/honeypot')
        for i in doc.inputs:
            if i and i not in doc.labels and i not in ('busca','f-formato','f-tema'):errors.append(f'{p}: campo sem label {i}')
        jumps=[b for a,b in zip(doc.headings,doc.headings[1:]) if b>a+1]
        if jumps:errors.append(f'{p}: salto de títulos {doc.headings[:12]}')

# Pendências "a preencher" só podem existir na prévia.
import os
preview=os.environ.get('SITE_PREVIEW')=='1'
for p in files:
    t=p.read_text()
    if not preview and ('a preencher' in t.lower()) and 'quem-voce-contrataria' not in p.parts:errors.append(f'{p}: "a preencher" fora da prévia')
    if 'wa.me/' in t and 'wa.me/5511916556521' not in t:errors.append(f'{p}: WhatsApp diferente do DDD 11')
    for bad in ('99653-6157','99137-0128','FGV','MBA'):
        if bad in t and 'artigos' not in p.parts and 'posts' not in p.parts:errors.append(f'{p}: termo proibido {bad}')

# Toda URL e âncora do inventário anterior precisa continuar respondendo (arquivo ou redirecionamento 301).
redirects={}
for line in (root/'_redirects').read_text().splitlines():
    parts=line.split()
    if len(parts)>=2:redirects[parts[0].rstrip('/') or '/']=parts[1]
inv=json.loads((root.parent/'scripts/inventario_antes.json').read_text())
legacy_js=(root/'assets/site.js').read_text()
for path,info in inv.items():
    if path=='/404.html':continue
    f=root/path.strip('/')/'index.html' if path!='/' else root/'index.html'
    if f.is_file():
        now=parsed.get(f.resolve()) or Page(f.read_text())
        for i in info['ids']:
            if i in ('menu-button','nav','conteudo','ano','titulo'):continue
            if i not in now.ids and not (path=='/' and f"{i}:" in legacy_js.replace("'","")):errors.append(f'âncora perdida {path}#{i}')
    elif path.rstrip('/') not in redirects:errors.append(f'URL perdida sem redirecionamento {path}')
    else:
        dest=redirects[path.rstrip('/')];d=root/urlsplit(dest).path.strip('/')/'index.html'
        if not d.is_file():errors.append(f'redirecionamento para destino inexistente {path} -> {dest}')

sm=ET.parse(root/'sitemap.xml')
for loc in sm.findall('.//{*}loc'):
    path=urlsplit(loc.text).path
    if not (root/path.strip('/')/'index.html').is_file():errors.append('sitemap missing '+path)
data=json.loads((root/'data/editorial.json').read_text())
if len(data['artigos'])<10 or len(data['posts'])<8:errors.append('Editorial preservation count')
for a in data['artigos']:
    if not (root/'artigos'/a['slug']/'index.html').exists():errors.append('Missing article '+a['slug'])
print(json.dumps({'html_files':len(files),'links_and_assets_checked':link_count,'sitemap_urls':len(sm.findall('.//{*}loc')),'articles':len(data['artigos']),'posts':len(data['posts']),'errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
