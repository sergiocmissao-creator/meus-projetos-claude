# Site Sérgio Missão

Reestruturação a partir do conteúdo de `sergiomissao-site/index.html` no commit `8705b98f577b4104492a0372d5087c18432f8f4b`. Essa versão permanece recuperável no histórico Git.

## Atualização

O site continua estático. Todas as páginas são HTML com conteúdo completo, metadados próprios e links diretos. Não depende de Node, serviços novos, formulários externos ou execução de JavaScript para apresentar as ofertas e os contatos.

Para regenerar as páginas, execute `python3 scripts/build_site.py` na raiz do repositório. O conteúdo editorial está em `sergiomissao-site/data/editorial.json`; textos comerciais e componentes estão no gerador. Os estilos e o comportamento de menu/compatibilidade ficam em `sergiomissao-site/assets/`.

Execute `python3 scripts/check_site.py` para validar títulos, descrições, H1, IDs, imagens, links internos, âncoras e sitemap. Os arquivos gerados devem ser incluídos no commit; o diretório publicável continua sendo `sergiomissao-site`.

As URLs antigas com fragmentos são encaminhadas por `assets/site.js`. As rotas legadas de entrevistas e palestras têm redirecionamentos em `_redirects`. A série `quem-voce-contrataria` e seus arquivos foram preservados. Os 10 artigos e 8 posts foram mantidos integralmente.

## Fontes e decisões

- Portfólio, conteúdos, fotos, marca e identidade: versão atual do site e repositório.
- Contatos comerciais, MBA Executivo pela FGV e livro em produção: PDF comercial `Palestra_BURNEI_Sergio_Missao.pdf`, versão atual conferida em 29/10/2026. PDF disponibilizado sem alterações. Esse material usa o título BURNEI! E agora?, identificado dessa forma na página de organizadores; a página da palestra preserva Burnout Sem Lados.
- Telefones: +55 54 99653-6157 primeiro e +55 35 99137-0128 como adicional. E-mail e redes sociais preservados do site.
- Durações dos treinamentos: formatos informados na versão anterior. Duração de palestras e valores individuais continuam sob consulta.
- Cargos no cooperativismo descritos sem instituição ou período não confirmado. Não foram inventados clientes, depoimentos ou certificações.
- A agenda Google existente foi preservada. Não foi localizado endereço operacional Cal.com.

## Publicação e verificações pendentes

O repositório não contém configuração da hospedagem ou fluxo de CI/deploy. A sessão Netlify acessível abriu onboarding, sem exibir o projeto responsável pelo domínio. Não criar novo projeto nem trocar DNS para contornar esse acesso: usar o projeto existente.

O ambiente de execução bloqueou a abertura de servidor local, e o navegador bloqueou URLs `file:`. Verificação visual em desktop/celular e conferência das rotas no domínio precisam ocorrer em prévia HTTP ou no deploy autorizado. Verificações estáticas não substituem essas etapas. Commit no GitHub não comprova publicação.
