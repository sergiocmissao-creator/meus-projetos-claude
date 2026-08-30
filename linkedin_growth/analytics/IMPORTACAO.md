# MODELO DE IMPORTAÇÃO DOS DADOS DO LINKEDIN

Este é o passo que destrava o sistema inteiro. Sem estes dados, o sistema funciona só no modo
qualitativo (radar, ideias, comentários) — os módulos 1, 9 e 10 (Content Intelligence, Performance
Intelligence, Strategic Learning) ficam **desligados**, porque não há benchmark interno (§13).

---

## Como exportar (LinkedIn, versão web — leva ~10 minutos)

### 1. Exportação oficial da conta — `Settings → Data privacy → Get a copy of your data`

Marcar pelo menos:
- **Posts / Shares** → histórico de publicações
- **Connections** → lista de conexões com cargo e empresa
- **Comments** → comentários que Sergio fez (alimenta `comentarios/historico.csv`)
- **Reactions**

O e-mail com o `.zip` chega em minutos (arquivos pequenos) ou até 24h (arquivo completo).

### 2. Analytics de criador — `Perfil → Analytics`

Baixar em **Export**:
- `Post impressions` — série temporal
- `Followers` — série + demografia (cargo, empresa, setor, localidade)
- `Profile viewers`
- `Search appearances`

### 3. Métricas por post (o que a exportação NÃO traz completo)

Para os últimos ~20 posts, abrir cada post → **View analytics** e anotar em `posts.csv`:
impressões, membros alcançados, reações, comentários, republicações, e — quando disponível —
seguidores ganhos e visitas ao perfil.

É trabalhoso. Fazer só uma vez, para os **20 últimos posts**. Depois disso, preencher no dia
seguinte a cada publicação (2 minutos por post).

---

## Onde colocar os arquivos

```
analytics/
  raw/                      ← criar esta pasta e jogar os exports crus aqui
    Shares.csv
    Connections.csv
    Comments.csv
    followers_YYYYMMDD.xlsx
    ...
```

Depois é só dizer **`IMPORTAR DADOS`** que o sistema lê, normaliza e preenche
`posts.csv`, `seguidores.csv`, `perfil.csv` e `interacoes.csv`.

---

## Prioridade, se o tempo for curto

| Prioridade | Dado | Destrava |
|---|---|---|
| **1** | Métricas dos últimos 20 posts | Benchmark interno (§13), todas as métricas normalizadas (§12) |
| **2** | Demografia de seguidores (cargo/empresa) | Qualified Audience Score (§59) — o indicador mais importante do sistema |
| **3** | Lista de conexões | Network Gap (§42) e conexões em comum do Top 100 |
| **4** | Histórico de comentários feitos | Relationship Intelligence (§52) |
| **5** | Série de impressões e visitas | Growth Score (§57) |

**Se Sergio só puder fazer uma coisa: prioridade 2.** A demografia de seguidores é o único dado
que responde à pergunta central do sistema — *a audiência está ficando mais qualificada?* — e é o
único que nenhuma análise qualitativa consegue substituir.

---

## Dicionário das colunas de `posts.csv`

| Coluna | O que é | Origem |
|---|---|---|
| `territorio` | 1 dos 7 territórios de `perfil/territorios.md` | classificação do sistema |
| `formato` | texto / carrossel / imagem / vídeo / artigo / newsletter / enquete / documento | manual |
| `estrutura` | qual das 10 fórmulas editoriais do §48 | classificação do sistema |
| `interacoes_estrategicas` | nº de comentários/compartilhamentos vindos de A1/A2/B do Top 100 | cruzamento com `radar/` |
| `comentarios_de_terceiros` | comentários excluindo as respostas do próprio Sergio | manual |
| `*_por_mil` | métricas normalizadas por 1.000 impressões (§12) | calculado |
| `authority_score` / `growth_score` / `conversation_score` | §56, §57, §58 | calculado |

**Regra:** campo sem dado fica **vazio**. Nunca preencher com zero, "n/a" ou estimativa — zero e
ausência são coisas diferentes, e essa distinção é o que impede o sistema de tirar conclusão falsa.
