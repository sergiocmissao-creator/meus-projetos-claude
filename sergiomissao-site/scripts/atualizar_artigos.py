#!/usr/bin/env python3
"""Atualiza a seção "Artigos" do index.html a partir de data/linkedin.json.

Regras de curadoria (decididas por Sergio em 07/10/2026):
  - entram TODOS os artigos e edições da newsletter de autoria dele;
  - entram os posts de autoria dele com MAIS de 70 curtidas (reações);
  - reposts e conteúdos de terceiros nunca entram.

O bloco gerado fica entre os marcadores
  <!-- LINKEDIN:INICIO -->  e  <!-- LINKEDIN:FIM -->
dentro da seção #artigos. Rodar de novo com os mesmos dados não muda nada.

Uso: python3 scripts/atualizar_artigos.py   (a partir da pasta sergiomissao-site)
"""
import html
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "data" / "linkedin.json"
PAGINA = RAIZ / "index.html"
INICIO, FIM = "<!-- LINKEDIN:INICIO -->", "<!-- LINKEDIN:FIM -->"
MIN_CURTIDAS = 70
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ROTULO = {"artigo": "Artigo", "newsletter": "Newsletter", "post": "Post"}


def entra(item: dict) -> bool:
    if not item.get("autor_proprio", True):
        return False
    tipo = item.get("tipo")
    if tipo in ("artigo", "newsletter"):
        return True
    return tipo == "post" and int(item.get("curtidas", 0)) > MIN_CURTIDAS


def data_br(iso: str) -> str:
    try:
        d = date.fromisoformat(iso[:10])
        return f"{d.day:02d} {MESES[d.month - 1]} {d.year}"
    except ValueError:
        return ""


def cartao(item: dict) -> str:
    e = html.escape
    tipo = item["tipo"]
    resumo = item.get("resumo", "").strip()
    curtidas = f' · {int(item["curtidas"])} curtidas' if tipo == "post" else ""
    return (
        f'<article class="li-card li-{tipo}">'
        f'<p class="li-meta">{ROTULO[tipo]} · <time datetime="{e(item.get("data", "")[:10])}">'
        f'{data_br(item.get("data", ""))}</time>{curtidas}</p>'
        f'<h3 class="li-titulo"><a href="{e(item["url"])}" target="_blank" rel="noopener">'
        f'{e(item["titulo"])}</a></h3>'
        + (f'<p class="li-resumo">{e(resumo)}</p>' if resumo else "")
        + f'<a class="li-link" href="{e(item["url"])}" target="_blank" rel="noopener">'
        f'Ler no LinkedIn →</a></article>'
    )


def gerar_bloco(itens: list) -> str:
    vistos, selecionados = set(), []
    for it in itens:
        if entra(it) and it["url"] not in vistos:
            vistos.add(it["url"])
            selecionados.append(it)
    selecionados.sort(key=lambda i: i.get("data", ""), reverse=True)
    estilo = (
        "<style>.li-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));"
        "margin-top:1.5rem}.li-card{border:1px solid rgba(127,127,127,.25);border-radius:10px;padding:1.1rem;"
        "display:flex;flex-direction:column;gap:.5rem}.li-meta{font-size:.8rem;opacity:.7;margin:0}"
        ".li-titulo{font-size:1.05rem;line-height:1.35;margin:0}.li-titulo a{color:inherit;text-decoration:none}"
        ".li-resumo{font-size:.92rem;opacity:.85;margin:0}.li-link{margin-top:auto;font-size:.9rem}</style>"
    )
    if not selecionados:
        return f"{INICIO}{FIM}"
    cartoes = "".join(cartao(i) for i in selecionados)
    return f'{INICIO}{estilo}<div class="li-grid">{cartoes}</div>{FIM}'


def main() -> int:
    dados = json.loads(DADOS.read_text(encoding="utf-8"))
    pagina = PAGINA.read_text(encoding="utf-8")
    if INICIO not in pagina or FIM not in pagina:
        print("Marcadores LINKEDIN não encontrados no index.html", file=sys.stderr)
        return 1
    antes, resto = pagina.split(INICIO, 1)
    _, depois = resto.split(FIM, 1)
    nova = antes + gerar_bloco(dados.get("itens", [])) + depois
    if nova == pagina:
        print("Sem mudanças.")
        return 0
    PAGINA.write_text(nova, encoding="utf-8")
    print("index.html atualizado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
