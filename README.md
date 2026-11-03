# PNCP · Controladoria de contratações públicas

Projeto final do Módulo 2 do SCTEC — análise de dados com Python, PostgreSQL e Power BI.

Repositório: [projeto-final-sctec-pncp](https://github.com/victorhcbrandao/projeto-final-sctec-pncp).

Acesso rápido: [painel Power BI](powerbi/PNCP.pbix), [resultados SQL](docs/RESULTADOS_SQL.md), [checklist](docs/CHECKLIST.md) e [roteiro do vídeo](docs/ROTEIRO_VIDEO.md).

O projeto transforma a amostra fornecida de contratações federais publicadas em 2025 em uma base analítica para investigar economia, concentração de fornecedores, modalidades, ciclos, território e perfil do gasto. A amostra não representa todas as compras públicas do país. Volume homologado não equivale a pagamento realizado.

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

## Arquitetura e decisões

`CSV bruto → auditoria e limpeza Python → tabelas estrela → PostgreSQL → Power BI`

![Modelo dimensional](docs/img/modelo_dimensional.png)

O grão é um item por contratação: `(numero_controle_pncp, numero_item)`. Resultados cancelados saem antes da seleção pela menor ordem de classificação e, no empate, pelo menor sequencial numérico. A quantidade homologada positiva prevalece; na sua ausência, utiliza-se a quantidade do item. A mesma quantidade calcula os dois totais, arredondados a centavos.

São comparáveis os itens fora da modalidade 12 com razão homologado/estimado entre 0,1 e 10, inclusive. Economia pode ser negativa. Para os não comparáveis, `economia_valor` fica NULL: essa escolha atende à seção 4.3 do enunciado, apesar do zero sugerido no roteiro-base. Credenciamento continua no volume total.

Homologação anterior à publicação vira NULL sem excluir o item. Ciclo zero no mesmo dia é válido. Órgãos são dimensionados por CNPJ; a pergunta 4 agrupa pelo nome e exige cinco ciclos válidos. Obras têm prioridade na classificação por palavras inteiras; depois vêm serviços e bens. Todas as 27 UFs são mapeadas para região.

Chaves naturais são únicas nas dimensões. O membro -1 é reservado a ausências de referência. A carga valida as chaves antes de escrever e usa uma única transação para criar e preencher as cinco tabelas; falhas revertem a carga. A criação do banco é uma operação administrativa separada. Recriar um banco existente exige `--recriar` explícito.

## Reprodução — passo a passo no Windows

Para somente visualizar o painel, extraia o ZIP e abra `powerbi/PNCP.pbix`: os dados já estão importados. Para reproduzir o tratamento, carregar o PostgreSQL e atualizar o painel, siga as etapas abaixo. Os comandos são executados no **PowerShell**, exceto os blocos identificados como SQL, que são executados no **Query Tool do pgAdmin**.

### 1. Preparar os programas e a pasta

Você precisa de Python 3.10 ou superior, PostgreSQL, pgAdmin 4 e Power BI Desktop. O banco deste projeto foi validado no PostgreSQL 18.4.

1. Se ainda não tiver o PostgreSQL, obtenha o instalador pela [página oficial para Windows](https://www.postgresql.org/download/windows/).
2. No instalador, inclua PostgreSQL Server, pgAdmin 4 e Command Line Tools. Escolha e guarde a senha do usuário `postgres`. Use a porta `5432` se estiver disponível; se escolher outra, utilize essa mesma porta em todas as conexões deste guia. Não é necessário instalar complementos pelo Stack Builder para executar este projeto.
3. Se o PostgreSQL já estiver instalado, utilize a instalação existente. Pesquise **Serviços** no menu Iniciar e confira se o serviço do PostgreSQL está em execução. O nome pode variar conforme a instalação.
4. Extraia todo o ZIP. Trabalhe na pasta que contém `README.md`, `requirements.txt`, `src`, `data`, `sql` e `powerbi`, não dentro do ZIP.
5. Abra o PowerShell nessa pasta. No Explorador de Arquivos, abra a pasta, digite `powershell` na barra de endereços e pressione Enter. Alternativamente, use `cd` com o caminho real da sua pasta:

```powershell
cd "C:\caminho\para\Projeto_Final_SCTEC_PNCP"
Get-Location
Test-Path .\requirements.txt
python --version
```

Substitua o caminho de exemplo antes de executar. `Test-Path` deve retornar `True`. Se `python` não for reconhecido, tente `py --version`; se funcionar, use `py` no comando de criação do ambiente da etapa 3. Se nenhum funcionar, instale o Python e reabra o PowerShell.

### 2. Registrar o servidor no pgAdmin

O PostgreSQL é o serviço que armazena os bancos. O pgAdmin é a interface para administrá-lo. **Registrar um servidor no pgAdmin apenas salva uma conexão; não instala o serviço nem cria o banco do projeto.**

1. Abra o pgAdmin 4.
2. Se já houver uma conexão chamada `PostgreSQL 18` apontando para sua instalação local, você pode utilizá-la. Não precisa registrar outra.
3. Para registrar uma nova conexão, clique com o botão direito em **Servers → Register → Server…** (Servidores → Registrar → Servidor).
4. Na aba **General**, preencha **Name** com `PostgreSQL local — SCTEC`. Esse nome é apenas um rótulo de sua escolha.
5. Na aba **Connection**, preencha:

| Campo | Valor para a instalação local padrão |
|---|---|
| Host name/address | `localhost` |
| Port | `5432` |
| Maintenance database | `postgres` |
| Username | `postgres` |
| Password | A senha atual do usuário `postgres` |
| Save password | Opcional, para salvar a senha neste computador |

6. Clique em **Save**. Expanda o servidor e depois **Databases**. Se a conexão abrir, o serviço e as credenciais estão funcionando.

A senha mestra do pgAdmin, quando solicitada, é diferente da senha do usuário `postgres`. Neste formulário, use a senha do PostgreSQL. Se ela foi alterada, use a nova senha também no `.env` e no Power BI.

Referência: [registro de servidor no pgAdmin](https://www.pgadmin.org/docs/pgadmin4/latest/server_dialog.html).

**Não crie `pncp_controladoria` manualmente nesta etapa.** O carregador Python cria esse banco automaticamente. Se ele já existir de uma execução anterior, consulte a etapa 6 antes de carregar novamente.

### 3. Criar o ambiente Python e instalar as dependências

Na pasta do projeto, execute uma linha por vez:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se você utiliza o comando `py`, a primeira linha pode ser `py -m venv .venv`. Os comandos seguintes continuam usando o executável dentro de `.venv`.

O projeto utiliza pandas, psycopg2-binary e pytest. Aguarde a instalação terminar sem erros. Não é necessário ativar o ambiente virtual, pois os comandos usam seu executável diretamente. Isso também evita problemas com a política de execução do PowerShell.

### 4. Configurar a conexão no arquivo .env

Execute:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

A condição preserva um `.env` que já exista. Configure os campos abaixo, substituindo o texto de exemplo pela sua senha real:

```dotenv
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD="COLOQUE_SUA_SENHA_AQUI"
PG_DATABASE=pncp_controladoria
```

Salve e feche o Bloco de Notas. O arquivo deve se chamar **`.env`**, não `.env.txt`. Use aspas externas iguais, como no exemplo; elas não fazem parte da senha. A conexão deve usar o mesmo servidor, porta e usuário que funcionaram no pgAdmin.

O banco `postgres` da etapa 2 é administrativo. O banco `pncp_controladoria` deste arquivo é o destino dos dados do projeto. Não troque `PG_DATABASE` por `postgres`.

A senha não deve ser enviada ao GitHub, exibida na gravação nem compartilhada. O `.env` é ignorado pelo Git e não acompanha o ZIP. Também não deixe ativa uma regra temporária `trust` usada para recuperação de senha: restaure a autenticação original antes de continuar.

### 5. Executar o tratamento e conferir os testes

Confirme que `data/raw` contém `compras.csv`, `itens.csv` e `resultados.csv`. Depois, execute:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.pipeline
```

Esse comando executa a limpeza, a auditoria, a montagem das tabelas e a validação dos resultados. **Ainda não carrega o PostgreSQL.** Ele gera os CSVs tratados em `data/processed` e as evidências em `reports`.

Em seguida:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

Na versão validada, o resultado foi **61 testes aprovados**. Se houver erro, resolva-o antes de continuar; não considere uma execução interrompida como concluída.

### 6. Criar o banco e carregar os dados

**Primeira execução, quando `pncp_controladoria` ainda não existe:**

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.carregar
```

O carregador conecta ao banco administrativo `postgres`, cria `pncp_controladoria` em UTF-8 e depois cria e preenche as cinco tabelas em uma transação. Ao final, deve aparecer `Carga concluida e confirmada`, com as contagens. O usuário precisa de permissão para criar bancos; neste ambiente local, utiliza-se `postgres`.

| Tabela | Linhas esperadas |
|---|---:|
| dim_orgao | 363 |
| dim_fornecedor | 2.652 |
| dim_modalidade | 7 |
| dim_localidade | 27 |
| fato_item_contratado | 6.126 |

**Se aparecer “Banco ja existe”:** o carregador interrompe a operação para preservar os dados. Se você quer apenas consultar ou gravar o vídeo, pule para a etapa 7. Se criou um banco vazio manualmente, ele também será tratado como existente.

Somente se quiser **apagar e reconstruir todo o banco indicado em `PG_DATABASE`**, após conferir o nome e preservar qualquer conteúdo necessário, execute:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.carregar --recriar
```

Esse comando encerra conexões com o banco do projeto, apaga-o e recria-o. Não é necessário para trocar uma senha, registrar uma conexão no pgAdmin, abrir o painel ou executar consultas. A criação do banco é separada da transação de carga; não use a opção esperando que uma falha restaure o banco anterior.

### 7. Localizar as tabelas e executar SQL no pgAdmin

1. No pgAdmin, clique com o botão direito em **Databases → Refresh**.
2. Expanda **pncp_controladoria → Schemas → public → Tables**. As cinco tabelas devem aparecer. Atualize a lista se necessário.
3. Clique com o botão direito em **pncp_controladoria → Query Tool**. Confira que o editor está conectado a esse banco, e não ao banco administrativo `postgres`.
4. Cole a consulta abaixo e clique em **Execute/Run** (botão de executar). Leia o resultado na aba **Data Output**:

```sql
SELECT 'dim_orgao' AS tabela, COUNT(*) AS linhas FROM public.dim_orgao
UNION ALL SELECT 'dim_fornecedor', COUNT(*) FROM public.dim_fornecedor
UNION ALL SELECT 'dim_modalidade', COUNT(*) FROM public.dim_modalidade
UNION ALL SELECT 'dim_localidade', COUNT(*) FROM public.dim_localidade
UNION ALL SELECT 'fato_item_contratado', COUNT(*) FROM public.fato_item_contratado;
```

5. Para conferir a análise de economia, use o botão **Open File** do Query Tool e abra `sql/02_p1_economia.sql`, ou copie o conteúdo do arquivo para o editor. Execute a consulta.
6. Compare com: **6.126 itens**, **1.962 contratações**, **R$ 8.044.498.805,74** de volume homologado e **R$ 992.861.686,95** de economia.
7. Abra e execute os arquivos `03_p2_fornecedores.sql` até `07_p6_perfis.sql`, um por vez. O arquivo `02_perguntas.sql` reúne as seis consultas; se utilizá-lo, selecione uma consulta completa por vez para acompanhar cada resultado.

Os resultados de referência estão em [RESULTADOS_SQL.md](docs/RESULTADOS_SQL.md). O script `01_criar_banco.sql` é utilizado internamente pela carga para estruturar as tabelas; não é necessário executá-lo manualmente depois da carga.

### 8. Abrir e atualizar o Power BI

1. Abra `powerbi/PNCP.pbix` no Power BI Desktop. Ele já contém os dados da versão validada. Para visualizar as páginas, não é preciso recriar nem atualizar o banco.
2. Para buscar os dados de sua instalação, primeiro conclua a carga da etapa 6. Depois clique em **Página Inicial → Atualizar** no Power BI.
3. Se o aplicativo solicitar autenticação, selecione o tipo **Banco de dados**, informe o usuário `postgres` e sua senha atual e conecte.
4. A fonte do relatório é o servidor `localhost:5432`, banco `pncp_controladoria`. Se sua instalação usa outro servidor, porta ou banco, ajuste a fonte em **Transformar dados → Configurações da fonte de dados → Alterar fonte**, quando disponível. Confirme que as consultas do modelo apontam para o mesmo destino do `.env`.
5. Se houver uma senha antiga salva, abra **Configurações da fonte de dados**, selecione a fonte PostgreSQL e utilize **Editar permissões → Editar credenciais**; os nomes podem variar conforme a versão. Informe a nova senha e tente atualizar novamente.
6. Confira P1 sem filtros: volume aproximado de **8,04 Bi**, economia de **992,86 Mi**, economia percentual de **14,46%** e cobertura comparável de **89,08%**. Navegue pelas seis páginas e salve o relatório após uma atualização bem-sucedida.

No Desktop, os botões com ações são acionados com **Ctrl + clique**. Passe o mouse sobre os gráficos para visualizar o tooltip. A fonte editável também está disponível em `powerbi/PNCP.pbip`; para começar a revisão, prefira o PBIX pronto.

Referência: [conector PostgreSQL no Power BI](https://learn.microsoft.com/power-query/connectors/postgresql).

### 9. Resolver os erros mais comuns

| Mensagem ou situação | O que conferir |
|---|---|
| `requirements.txt` não encontrado | O PowerShell está na pasta que contém o README e `requirements.txt`? Use `Get-Location` e `Test-Path .\requirements.txt`. |
| `No module named src` | Execute a partir da raiz do projeto, usando `-m src.pipeline`, e não de dentro da pasta `src`. |
| `No module named pandas` ou `psycopg2` | Instale `requirements.txt` usando o mesmo Python de `.venv` que executa os scripts. |
| Arquivo tratado não encontrado | Execute `src.pipeline` antes de `src.carregar`; confira se o tratamento terminou sem erros. |
| `connection refused` | Verifique se o serviço PostgreSQL está iniciado e se host e porta estão corretos. Registrar o servidor no pgAdmin não inicia nem instala o serviço. |
| `password authentication failed` | Use a senha atual do usuário PostgreSQL, não a senha mestra do pgAdmin. Atualize `.env`, pgAdmin e Power BI após uma troca. |
| A conexão funciona no pgAdmin, mas não no Python | Confira o `.env` da pasta efetivamente executada. Variáveis de ambiente `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD` e `PG_DATABASE` já definidas na sessão têm prioridade sobre o arquivo. |
| `Banco ja existe` | Para consultar, mantenha o banco e prossiga à etapa 7. A opção `--recriar` é exclusiva para reconstrução deliberada. |
| Tabela não encontrada no Query Tool | Confirme a conexão com `pncp_controladoria`, a conclusão da carga e o schema `public`. |
| Painel abre, mas a atualização falha | O PBIX pode exibir dados importados mesmo sem conexão atual. Confira serviço, credenciais e destino da fonte antes de atualizar. |

Para a gravação, deixe o banco pronto e uma consulta com resultado aberta. Não é necessário reinstalar programas ou apagar o banco durante a apresentação.

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

![Sprints do projeto](docs/img/sprints.png)

Meta inicial: 28/10/2026; validação técnica concluída em 29/10/2026. O documento menciona 03/11/2016; confirmar a data oficial no AVA. O quadro distingue etapas implementadas de validações e entregas ainda pendentes.

## Validação e entrega

- 61 testes Python aprovados na conferência final de 29/10/2026; inclui os 54 casos fornecidos e a prova real integral.
- Validação nativa PostgreSQL: carga confirmada, grão único e totais reconciliados; seis perguntas executadas. Evidência: [resultados SQL](reports/resultados_postgresql.json).
- Power BI: 25 medidas, seis páginas e PBIX com dados. Conferidos totais, filtro de janeiro, calendário marcado, abertura/fechamento do menu, navegação e tooltip contextual. [Evidências](reports/validacao_powerbi.json).
- Repositório público verificado sem autenticação em 30/10/2026; código e histórico disponíveis na branch `main`.
- Gravação do vídeo e envio no AVA: pendentes.

O [roteiro de defesa](docs/ROTEIRO_VIDEO.md) organiza uma apresentação de até sete minutos. **Vídeo: gravação e link público pendentes.** Atualizar este campo antes da entrega. Não enviar ao AVA enquanto os itens obrigatórios do [checklist](docs/CHECKLIST.md) estiverem pendentes.

## Melhorias futuras

Carga incremental com controle de alterações, testes de regressão por recorte, classificação de itens com revisão humana, validação cadastral de documentos, monitoramento da qualidade por lote e atualização agendada do painel. A economia estimada deve ser interpretada com cautela: não comprova eficiência causal nem execução financeira.

## Revisão do painel

O PBIX foi reaberto no Power BI Desktop, preservando os dados e os indicadores. Evidências: [menu](docs/img/menu_powerbi.png), [tooltip contextual](docs/img/tooltip_powerbi.png) e [calendário marcado](docs/img/calendario_marcado.png).

Para validar em conjunto, comece pela página Economia, teste um mês, percorra as seis páginas e compare com [RESULTADOS_SQL.md](docs/RESULTADOS_SQL.md). O [checklist](docs/CHECKLIST.md) separa a implementação concluída das pendências de publicação e entrega.
