# Defesa técnica — duração alvo 6min50s

Grave em 16:9, com rosto visível, áudio claro e zoom legível. Use os valores realmente exibidos após atualizar o relatório. Ensaie a explicação com suas palavras.

| Tempo | Mostrar e explicar |
|---|---|
| 0:00–0:25 | Apresentação pessoal, objetivo e limite da amostra federal de 2025 |
| 0:25–1:15 | CSVs e auditoria: 2.042 compras, 7.077 itens e 15.896 resultados. Exemplo de número ambíguo, data impossível e acento quebrado |
| 1:15–1:55 | Código: cancela antes de escolher vencedor; 852 sem resultado e 99 rejeições; 6.126 itens finais |
| 1:55–2:25 | PostgreSQL: estrela, grão, UNIQUE, FKs e transação. Mostrar uma consulta e o resultado |
| 2:25–3:05 | Modelo BI: calendário dinâmico, mês ordenado, relação ativa e inativa, tabela Medidas e pastas |
| 3:05–3:45 | Explicar Economia R$: VAR guarda estimado e homologado comparáveis, RETURN subtrai. Economia %: DIVIDE evita divisão por zero. Top 10: TOPN escolhe fornecedores no contexto |
| 3:45–5:50 | Percorrer P1–P6, cerca de 20s por página, citando métrica e conclusão. Abrir/fechar menu, filtrar mês e passar o mouse no tooltip |
| 5:50–6:25 | Mostrar sprints, o que foi entregue e o ajuste necessário na integração |
| 6:25–6:50 | Limitações, melhoria futura e encerramento |

Antes de gravar, saiba responder: por que não somar estimado de não comparáveis na economia? Por que a data invertida não exclui o item? Por que CPF/CNPJ são texto? Por que uma junção com todos os resultados multiplicaria o gasto? Por que a média de percentuais não equivale ao deságio agregado?

Publique no Google Drive com permissão de leitor para quem tem o link. Teste em janela anônima. Cole o link no README e envie os links exigidos no AVA. Após enviar, preserve a versão submetida.

## Preparação para gravar

Abra o PNCP.pbix, o modelo de relacionamentos, medidas.dax, uma consulta SQL e o README antes de começar. Limpe os filtros do painel e deixe a página P1 selecionada. Feche o arquivo .env e qualquer janela com credenciais. Faça um teste curto para conferir áudio, rosto e legibilidade.

## Pontos para explicar em cada página

Use estes pontos como apoio e explique com suas palavras. Os números abaixo correspondem à amostra completa, sem filtros.

| Página | Resultado e interpretação |
|---|---|
| P1 — Economia | Volume de R$ 8,04 bilhões, economia de R$ 992,86 milhões e deságio agregado de 14,46%. A economia considera apenas os itens comparáveis, que representam 89,08% dos itens. Volume homologado não é pagamento realizado. |
| P2 — Fornecedores | Os dez maiores fornecedores concentram 41,43% do volume. A concentração é um ponto de atenção para análise; isoladamente, não comprova irregularidade. |
| P3 — Modalidades | Pregão eletrônico apresenta deságio de 24,02%, enquanto concorrência eletrônica concentra 58,43% do volume. Credenciamento participa do volume, mas não do cálculo de economia comparável. |
| P4 — Ciclos | A UFCG apresenta o maior ciclo médio elegível: 266,3 dias em 16 ciclos válidos. O ranking exige pelo menos cinco ciclos válidos; datas invertidas ficam ausentes, preservando o item na análise financeira. |
| P5 — Território | Compare UF e região. A localização corresponde ao cadastro do órgão comprador, não necessariamente ao local de execução do contrato. |
| P6 — Perfis | Obras representam aproximadamente 60,82% do volume, serviços 36,56% e bens 2,63%. A soma exibida pode variar por arredondamento. A classificação utiliza as regras textuais documentadas. |

## Conferência antes de publicar o vídeo

- Duração máxima de sete minutos, com rosto e tela legíveis.
- Demonstração das seis páginas, menu, tooltip e filtro.
- Explicação de duas ou três medidas DAX e do calendário.
- Demonstração do pipeline, de SQL, do modelo e das sprints.
- Nenhuma senha ou arquivo .env visível.
- Link acessível sem login; após a gravação, inserir no README.
