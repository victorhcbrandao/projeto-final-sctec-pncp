# PNCP · Controladoria de contratações públicas

Projeto final do Módulo 2 do SCTEC, desenvolvido para transformar dados de contratações públicas em informações que apoiem a análise e o acompanhamento do gasto público.

A partir de uma amostra de contratações federais publicadas em 2025, o projeto investiga seis questões: quanto foi economizado em relação aos valores estimados, quais fornecedores concentram o volume homologado, como as modalidades se diferenciam, quais órgãos apresentam os maiores ciclos de contratação, como os valores se distribuem pelo território e qual é a participação de obras, serviços e bens.

A solução integra **Python**, para auditoria e tratamento dos arquivos; **PostgreSQL**, para armazenamento em modelo dimensional e consultas SQL; e **Power BI**, para exploração dos resultados em seis páginas interativas. As regras de tratamento, os testes e as evidências de validação documentam o percurso dos dados, desde os CSVs originais até os indicadores do painel.

A base tratada reúne **6.126 itens de 1.962 contratações**, com aproximadamente **R$ 8,04 bilhões em volume homologado**. Os resultados se limitam à amostra fornecida: volume homologado não representa pagamento realizado, e a economia calculada considera somente os itens que atendem às regras de comparabilidade.

Repositório: [projeto-final-sctec-pncp](https://github.com/victorhcbrandao/projeto-final-sctec-pncp).

Acesso rápido: [painel Power BI](powerbi/PNCP.pbix), [resultados SQL](docs/RESULTADOS_SQL.md) e [vídeo de apresentação — 6min50s](https://drive.google.com/file/d/1KI4VbRp8DBg23SjDjPh2lHSzWeeF2YhB/view).

## Resultados reproduzidos em Python

| Controle | Resultado |
|---|---:|
| Compras / itens / resultados brutos | 2.042 / 7.077 / 15.896 |
| Itens com resultado válido antes dos filtros | 6.225 |
| Itens sem resultado / rejeitados | 852 / 99 |
| Itens finais / contratações | 6.126 / 1.962 |
| Itens comparáveis | 5.457 |
| Volume homologado | R$ 8.044.498.805,74 |
| Estimado comparável | R$ 6.867.663.469,91 |
| Economia nos comparáveis | R$ 992.861.686,95 |
| Economia percentual ponderada | 14,46% |
| Ciclos válidos / ausentes | 5.896 / 230 |
| Itens com sobrepreço comparável | 27 |

Evidências: [auditoria](reports/auditoria_pipeline.json), [prova real](reports/prova_real.json) e [dicionário de inconsistências](docs/INCONSISTENCIAS.md). O percentual é a razão entre somas; não é a média dos percentuais dos itens.

Em `compras.csv`, não há repetição de `numero_controle_pncp` (2.042 chaves distintas). Os formatos, nulos disfarçados e acentos quebrados são detalhados no dicionário; as contagens completas por coluna estão em `reports/auditoria_colunas.csv`.

As 99 rejeições consideram apenas o primeiro motivo por item: 59 totais estimados inferiores a R$ 1; 23 valores unitários estimados ausentes ou não positivos; 7 homologados acima de mil vezes o estimado; 6 unitários homologados ausentes ou não positivos; 3 totais acima de R$ 1 trilhão; e 1 quantidade ausente ou não positiva. Os 852 itens sem resultado elegível são contabilizados separadamente.

## Arquitetura e decisões

`CSV bruto → auditoria e limpeza Python → tabelas estrela → PostgreSQL → Power BI`

![Modelo dimensional](docs/img/modelo_dimensional.png)

O grão é um item por contratação: `(numero_controle_pncp, numero_item)`. Resultados cancelados saem antes da seleção pela menor ordem de classificação e, no empate, pelo menor sequencial numérico. A quantidade homologada positiva prevalece; na sua ausência, utiliza-se a quantidade do item. A mesma quantidade calcula os dois totais, arredondados a centavos.

São comparáveis os itens fora da modalidade 12 com razão homologado/estimado entre 0,1 e 10, inclusive. Economia pode ser negativa. Para os não comparáveis, `economia_valor` fica NULL: essa escolha atende à seção 4.3 do enunciado. Credenciamento continua no volume total.

Homologação anterior à publicação vira NULL sem excluir o item. Ciclo zero no mesmo dia é válido. Órgãos são dimensionados por CNPJ; a pergunta 4 agrupa pelo nome e exige cinco ciclos válidos. Obras têm prioridade na classificação por palavras inteiras; depois vêm serviços e bens. Todas as 27 UFs são mapeadas para região.

Chaves naturais são únicas nas dimensões. O membro -1 é reservado a ausências de referência. A carga valida as chaves antes de escrever e usa uma única transação para criar e preencher as cinco tabelas; falhas revertem a carga. A criação do banco é uma operação administrativa separada. Recriar um banco existente exige `--recriar` explícito.

## Execução do projeto

Pré-requisitos: Python 3.10+, PostgreSQL, pgAdmin e Power BI Desktop instalados, com o serviço PostgreSQL em execução. Extraia o ZIP e abra o PowerShell na pasta que contém `README.md`, `requirements.txt` e `src`.

### 1. Conectar ao PostgreSQL pelo pgAdmin

Utilize uma conexão local existente ou clique com o botão direito em **Servers → Register → Server**. Em **General**, escolha um nome para a conexão. Em **Connection**, informe:

| Campo | Valor |
|---|---|
| Host name/address | `localhost` |
| Port | `5432` (ou a porta da sua instalação) |
| Maintenance database | `postgres` |
| Username | `postgres` |
| Password | Sua senha atual do PostgreSQL |

Clique em **Save**. Isso registra a conexão; o banco `pncp_controladoria` será criado pelo script de carga, sem precisar criá-lo manualmente.

### 2. Preparar o Python e a conexão

No PowerShell, dentro da pasta do projeto, execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

No `.env`, preencha e salve:

```dotenv
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD="SUA_SENHA"
PG_DATABASE=pncp_controladoria
```

Use a mesma senha e porta que funcionaram no pgAdmin. Preserve o nome `.env`, sem acrescentar `.txt`; esse arquivo não deve ser publicado. Se `python` não for reconhecido, tente `py` no comando de criação do ambiente.

### 3. Tratar os CSVs e carregar o banco

Mantenha `compras.csv`, `itens.csv` e `resultados.csv` em `data/raw`. Execute uma linha por vez, prosseguindo somente se não houver erros:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline
.\.venv\Scripts\python.exe -X utf8 -m pytest -q
.\.venv\Scripts\python.exe -X utf8 -m src.carregar
```

O primeiro comando trata os arquivos e gera as tabelas em `data/processed`; o segundo executa os testes; o terceiro cria o banco e carrega as cinco tabelas automaticamente. **Não é necessário importar os CSVs manualmente no pgAdmin nem executar o script de estrutura separadamente.**

Resultado esperado: 61 testes aprovados e a mensagem `Carga concluida e confirmada`, com 363 órgãos, 2.652 fornecedores, 7 modalidades, 27 localidades e 6.126 itens na fato.

Se aparecer **“Banco ja existe”** e você quiser apenas consultar os dados, siga para a etapa 4. Somente para **apagar e reconstruir o banco do projeto**, use:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.carregar --recriar
```

### 4. Abrir e executar os arquivos SQL

1. No pgAdmin, clique com o botão direito em **Databases → Refresh**.
2. Expanda **pncp_controladoria → Schemas → public → Tables** para visualizar as tabelas carregadas.
3. Clique com o botão direito no banco **pncp_controladoria → Query Tool**.
4. No editor, use **Open File** e selecione `sql/02_p1_economia.sql`. Clique em **Execute/Run** e confira a aba **Data Output**.
5. Repita com os arquivos `03_p2_fornecedores.sql` até `07_p6_perfis.sql`. Como alternativa, abra `02_perguntas.sql`, que reúne todas as perguntas, e selecione uma consulta completa por vez antes de executar.

A primeira consulta deve retornar **6.126 itens**, **1.962 contratações**, **R$ 8.044.498.805,74** de volume homologado e **R$ 992.861.686,95** de economia. Compare os demais resultados com [RESULTADOS_SQL.md](docs/RESULTADOS_SQL.md).

O arquivo `01_criar_banco.sql` é utilizado pelo carregador para estruturar as tabelas; não precisa ser executado novamente após a carga. Se uma consulta informar que a tabela não existe, confira se o Query Tool está conectado a `pncp_controladoria`, e não a `postgres`.

### 5. Abrir o Power BI

Abra `powerbi/PNCP.pbix`. Os dados já estão importados; para atualizá-los a partir do seu banco, clique em **Página Inicial → Atualizar** e informe as credenciais de banco de dados do usuário `postgres` quando solicitado.

A fonte utiliza `localhost:5432` e o banco `pncp_controladoria`. Se sua instalação for diferente ou a senha tiver mudado, ajuste a fonte ou as credenciais em **Configurações da fonte de dados**. O arquivo `PNCP.pbip` também está disponível como projeto editável.

Confira P1 sem filtros: **8,04 Bi** de volume, **992,86 Mi** de economia, **14,46%** de economia percentual e **89,08%** de itens comparáveis. No Desktop, use **Ctrl + clique** nos botões de navegação e passe o mouse nos gráficos para exibir o tooltip.

## Power BI e perguntas

| Página | Foco |
|---|---|
| P1 | Economia absoluta e percentual, volume e cobertura comparável |
| P2 | Top 10 fornecedores por identidade e concentração |
| P3 | Volume, economia e deságio por modalidade |
| P4 | Ciclo por nome de órgão com pelo menos cinco ciclos válidos |
| P5 | Volume e economia por UF e região |
| P6 | Composição entre obras, serviços e bens e ticket médio |

As medidas explícitas estão em `Medidas`, organizadas em pastas, e em [medidas.dax](powerbi/medidas.dax). O calendário DAX deriva os limites das datas da fato. Mês e ano/mês têm colunas de ordenação. Publicação é a relação ativa; homologação é inativa e utilizada por `USERELATIONSHIP`. O calendário automático está desativado no modelo. O calendário está marcado como tabela de datas; sua expressão está em [calendario.dax](powerbi/calendario.dax). `Ranking Fornecedor` demonstra o iterador `RANKX`; economia e concentração usam `VAR`, `CALCULATE` e `DIVIDE`.

No Desktop, use **Ctrl + clique** nos botões de menu e navegação (ou selecione o botão e pressione Ctrl + Enter). Passe o mouse sobre gráficos/tabelas para abrir o tooltip personalizado. As conclusões textuais descrevem a amostra completa; os indicadores respondem aos filtros.

## Planejamento

![Sprints do projeto — entrega concluída](docs/img/sprints.png?v=5e5e7c5)

Meta inicial: 28/10/2026; validação técnica em 29/10/2026 e revisão final em 03/11/2026. O quadro registra os objetivos, tarefas, períodos e situação de cada etapa.

## Validação e entrega

- 61 testes Python aprovados novamente em 03/11/2026; inclui os 54 casos fornecidos e a prova real integral.
- Validação nativa PostgreSQL registrada em 29/10/2026: carga confirmada, grão único e totais reconciliados; seis perguntas executadas. Evidência: [resultados SQL](reports/resultados_postgresql.json).
- Power BI: 25 medidas, seis páginas e PBIX com dados. Conferidos totais, filtro de janeiro, calendário marcado, abertura/fechamento do menu, navegação e tooltip contextual. [Evidências](reports/validacao_powerbi.json).
- Repositório público com código e histórico na branch `main`; mensagens dos commits descrevem as alterações sem prefixos técnicos.

A nova execução local confirmou os 54 exemplos fornecidos, os 28 controles da prova real e a integridade dos CSVs originais. A reconexão ao PostgreSQL em 03/11 não foi concluída com a configuração local disponível; as evidências anteriores foram preservadas.

## Melhorias futuras

Carga incremental com controle de alterações, testes de regressão por recorte, classificação de itens com revisão humana, validação cadastral de documentos, monitoramento da qualidade por lote e atualização agendada do painel. A economia estimada deve ser interpretada com cautela: não comprova eficiência causal nem execução financeira.

## Revisão do painel

O PBIX foi reaberto no Power BI Desktop, preservando os dados e os indicadores. Evidências: [menu](docs/img/menu_powerbi.png), [tooltip contextual](docs/img/tooltip_powerbi.png) e [calendário marcado](docs/img/calendario_marcado.png).

Para validar em conjunto, comece pela página Economia, teste um mês, percorra as seis páginas e compare com [RESULTADOS_SQL.md](docs/RESULTADOS_SQL.md).
