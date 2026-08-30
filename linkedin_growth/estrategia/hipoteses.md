# HIPÓTESES EDITORIAIS

_Formato: hipótese · o que a confirmaria · o que a derrubaria · confiança · próximo teste._
_Regra (§60/§63): nenhuma hipótese muda de status com base em um único post._
_Confiança inicial de todas: **nula** — não há dado histórico importado (ver `analytics/baseline.md`)._

---

**H1 — Histórias executivas reais geram mais autoridade do que posts conceituais.**
- Confirma: posts com caso real têm mais comentários de A1/A2 por 1.000 impressões.
- Derruba: posts conceituais atraem os mesmos perfis com igual ou maior densidade.
- Confiança: nula. Próximo teste: alternar 3 e 3, medir `interacoes_estrategicas` normalizada.

**H2 — Post com dado + fonte gera mais compartilhamento que post só com opinião.**
- Confirma: compartilhamentos por 1.000 impressões maior no grupo com dado.
- Derruba: sem diferença, ou dado reduz comentários (encerra a conversa em vez de abrir).
- Confiança: nula. Observação: dado dá autoridade mas pode matar debate. Medir os dois efeitos.

**H3 — Entrada universal ("furar a bolha") traz mais seguidores, entrada cooperativa traz mais autoridade.**
- Confirma: entrada universal com maior `seg_por_mil`; entrada cooperativa com maior `authority_score`.
- Derruba: entrada universal traz seguidores irrelevantes (QAS cai) sem ganho de alcance qualificado.
- Confiança: nula. **Esta é a hipótese mais importante do sistema** — dela depende toda a
  arquitetura de territórios (§8). Próximo teste: 2 universais para cada 3 cooperativos, 6 semanas.

**H4 — Comentar em post alheio de alta audiência gera mais seguidores qualificados por hora investida do que publicar.**
- Confirma: visitas ao perfil e seguidores em dias de comentário estratégico sem publicação própria.
- Derruba: sem efeito mensurável.
- Confiança: nula. Se confirmada, muda a alocação de tempo do Sergio inteira. **Alto valor.**

**H5 — Contraponto educado a uma tese dominante gera mais conversa que concordância elaborada.**
- Confirma: `conversation_score` maior; discussão entre terceiros nos comentários.
- Derruba: contraponto reduz alcance ou atrai audiência hostil.
- Confiança: nula. Risco reputacional: médio. Testar só com temas de baixa sensibilidade primeiro.

**H6 — Nomear o instrumento (escala P0–P4) em cada post acelera a formação de território.**
- Confirma: terceiros passam a usar o vocabulário sem que Sergio marque.
- Derruba: vocabulário próprio soa jargão e afasta.
- Confiança: nula. Este é o teste mais lento (6+ meses) e o de maior retorno se der certo.

**H7 — Horário e dia importam menos do que o setor acredita.**
- Confirma: variação de horário não explica variação de desempenho após controlar por tema.
- Derruba: efeito claro e repetido.
- Confiança: nula. Registrada para **evitar** que o sistema atribua a horário o que é do conteúdo.
