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

sm=ET.parse(root/'sitemap.xml')
for loc in sm.findall('.//{*}loc'):
    path=urlsplit(loc.text).path
    if not (root/path.strip('/')/'index.html').is_file():errors.append('sitemap missing '+path)
data=json.loads((root/'data/editorial.json').read_text())
if len(data['artigos'])!=10 or len(data['posts'])!=8:errors.append('Editorial preservation count')
for a in data['artigos']:
    if not (root/'artigos'/a['slug']/'index.html').exists():errors.append('Missing article '+a['slug'])
print(json.dumps({'html_files':len(files),'links_and_assets_checked':link_count,'sitemap_urls':len(sm.findall('.//{*}loc')),'articles':len(data['artigos']),'posts':len(data['posts']),'errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
