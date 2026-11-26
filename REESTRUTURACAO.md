# Site Sérgio Missão

Reestruturação a partir do conteúdo de `sergiomissao-site/index.html` no commit `8705b98f577b4104492a0372d5087c18432f8f4b`. Essa versão permanece recuperável no histórico Git.

## Atualização

O site continua estático. Todas as páginas são HTML com conteúdo completo, metadados próprios e links diretos. Não depende de Node, serviços novos, formulários externos ou execução de JavaScript para apresentar as ofertas e os contatos.

Para regenerar as páginas, execute `python3 scripts/build_site.py` na raiz do repositório. O conteúdo editorial está em `sergiomissao-site/data/editorial.json`; textos comerciais e componentes estão no gerador. Os estilos e o comportamento de menu/compatibilidade ficam em `sergiomissao-site/assets/`.

Execute `python3 scripts/check_site.py` para validar títulos, descrições, H1, IDs, imagens, links internos, âncoras e sitemap. Os arquivos gerados devem ser incluídos no commit; o diretório publicável continua sendo `sergiomissao-site`.

As URLs antigas com fragmentos são encaminhadas por `assets/site.js`. As rotas legadas de entrevistas e palestras têm redirecionamentos em `_redirects`. A série `quem-voce-contrataria` e seus arquivos foram preservados. Os 10 artigos e 8 posts foram mantidos integralmente.

## Fontes e decisões

- Portfólio, conteúdos, fotos, marca e identidade: versão atual do site e repositório.
- Contatos comerciais e livro em produção: PDF comercial `Palestra_BURNEI_Sergio_Missao.pdf`, versão atual conferida em 29/10/2026. O PDF não fica mais disponível para download no site (contém o MBA); a página de organizadores oferece pedir a apresentação pelo WhatsApp, por decisão de 30/10/2026. Esse material usa o título BURNEI! E agora?, identificado dessa forma na página de organizadores; a página da palestra preserva Burnout Sem Lados.
- Formação acadêmica (MBA Executivo pela FGV) não aparece no site, por decisão de 30/10/2026; fica apenas no LinkedIn.
- Telefone no site: somente o WhatsApp +55 11 91655-6521 (decisão de 30/10/2026). Os números +55 54 99653-6157 e +55 35 99137-0128 ficam apenas em flyers e outros documentos, como o PDF comercial. E-mail e redes sociais preservados do site.
- Durações dos treinamentos: formatos informados na versão anterior. Duração de palestras e valores individuais continuam sob consulta.
- Cargos no cooperativismo descritos sem instituição ou período não confirmado. Não foram inventados clientes, depoimentos ou certificações.
- A agenda Google existente foi preservada. Não foi localizado endereço operacional Cal.com.

## Publicação e verificações pendentes

O repositório não contém configuração da hospedagem ou fluxo de CI/deploy. A sessão Netlify acessível abriu onboarding, sem exibir o projeto responsável pelo domínio. Não criar novo projeto nem trocar DNS para contornar esse acesso: usar o projeto existente.

O ambiente de execução bloqueou a abertura de servidor local, e o navegador bloqueou URLs `file:`. Verificação visual em desktop/celular e conferência das rotas no domínio precisam ocorrer em prévia HTTP ou no deploy autorizado. Verificações estáticas não substituem essas etapas. Commit no GitHub não comprova publicação.

## Reformulação de novembro de 2026 (branch `reformulacao-2026-11`)

Alternativa aprovada em 25/11/2026: navegação por serviço (Palestras, Mentoria, Consultoria, Cooperativismo, Conteúdos, Sobre + "Conversar com Sérgio"), com o índice editorial dentro de `/conteudos/`.

- Prévia: `SITE_PREVIEW=1 python3 scripts/build_site.py` mostra os blocos "a preencher" (depoimentos, Casos, Mídia). **Antes de publicar no main, gerar sem a variável** (`python3 scripts/build_site.py`); `check_site.py` sem a variável falha se sobrar "a preencher".
- `/cooperativas/` foi substituída por `/cooperativismo/` (301 em `_redirects` e na âncora `#cooperativas` da home, via `site.js`).
- Itens do `editorial.json` aceitam o campo `tema` (Liderança e gestão; Pessoas e trabalho; Cultura e relacionamento; Cooperativismo e governança; Carreira e decisões). Sem o campo, o item entra em "Liderança e gestão".
- `quem-voce-contrataria/index.html` continua editado à mão (rodadas); o cabeçalho e o rodapé entre os marcadores `cabecalho-comum` e `rodape-comum` são regravados pelo gerador.
- Toda menção ao livro BURNEI! E agora? leva a https://burnei.com.br (decisão de 25/11/2026).
- Primeira pessoa só nas falas assinadas do Cooperativismo (frase de abertura, frases das cadeiras, aviso da Assembleia Viva); demais textos institucionais em terceira pessoa (decisão de 25/11/2026).
- Duração estimada de Burnout Sem Lados e Desaprenda a Liderar: 60 a 90 minutos (autorizada em 25/11/2026).
- Consultoria: diagnóstico, acompanhamento e treinamento (confirmados em 25/11/2026).
- `scripts/inventario_antes.json` guarda URLs e âncoras anteriores; `check_site.py` falha se alguma deixar de responder.

## Próxima revisão: agendamento e pagamento

Integrar o agendamento ao Calendário do Google Workspace e definir como receber pagamentos, principalmente para Mentorias, Avaliação de Desempenho e Preparação de Entrevistas. Links definitivos, valores e meio de pagamento serão definidos nessa etapa. Até lá, os botões "Agendar" continuam levando à agenda atual (`calendar.app.google/P4hFoDGgfbcVtn9u8`), e o fluxo Quem você contrataria? → AGENDAR ENTREVISTA → Como funciona a simulação foi mantido.
