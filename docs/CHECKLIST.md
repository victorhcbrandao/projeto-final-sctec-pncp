# Checklist de entrega — estado verificável

| Requisito | Evidência | Estado |
|---|---|---|
| Arquivos brutos preservados | data/raw | Concluído |
| Auditoria por problema e coluna | reports/auditoria_colunas.csv e docs/INCONSISTENCIAS.md | Concluído |
| Regras de limpeza e seleção | src/limpeza.py e montar_tabelas.py | Testes aprovados |
| Estrela com 4 dimensões e 1 fato | sql/01_criar_banco.sql | Validado no PostgreSQL |
| Carga em lote e transação | src/carregar.py e banco.py | Validado no PostgreSQL |
| Seis perguntas SQL | sql/02_perguntas.sql | Seis perguntas executadas |
| Prova real Python | reports/prova_real.json | Aprovada |
| 15+ medidas e calendário DAX | powerbi/medidas.dax e modelo | 25 medidas; dados atualizados no Desktop |
| Seis páginas, conclusões, menu e tooltip | powerbi/PNCP.Report | Validado no Desktop |
| PBIX funcional | powerbi/PNCP.pbix | Salvo com dados |
| Diagrama e sprints no README | docs/img | Concluído |
| Histórico Git e main | Histórico local em main | Concluído |
| Repositório público | Link a incluir | Pendente |
| Vídeo até 7 min com rosto e demonstrações | Link a incluir | Pendente |
| Links testados sem autenticação e envio AVA | Conferência final | Pendente |
