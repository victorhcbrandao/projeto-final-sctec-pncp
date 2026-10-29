# Dicionário de inconsistências

Contagens de células por coluna; os grupos podem se sobrepor. Zero é nulo apenas em campos textuais. Em medidas numéricas é um valor real, sujeito às regras de rejeição.

| Arquivo / coluna | Vazios | Nulos textuais | Espaços/invisíveis | Encoding |
|---|---:|---:|---:|---:|
| compras.processo | 0 | 77 | 47 | 0 |
| compras.objeto_compra | 0 | 0 | 520 | 43 |
| compras.cnpj_orgao | 0 | 0 | 131 | 0 |
| compras.razao_social_orgao | 0 | 0 | 58 | 0 |
| compras.municipio | 0 | 0 | 55 | 28 |
| compras.nome_unidade | 0 | 0 | 63 | 14 |
| compras.modo_disputa | 0 | 967 | 0 | 0 |
| compras.valor_total_estimado | 0 | 0 | 172 | 0 |
| compras.valor_total_homologado | 0 | 0 | 153 | 0 |
| compras.data_abertura_proposta | 617 | 0 | 0 | 0 |
| compras.data_encerramento_proposta | 617 | 0 | 0 | 0 |
| itens.descricao | 0 | 0 | 606 | 116 |
| itens.categoria_item | 0 | 7077 | 0 | 0 |
| itens.quantidade | 0 | 0 | 551 | 0 |
| itens.unidade_medida | 9 | 0 | 935 | 0 |
| itens.valor_unitario_estimado | 0 | 0 | 561 | 0 |
| itens.valor_total_estimado | 0 | 0 | 588 | 0 |
| itens.situacao_item | 0 | 220 | 0 | 0 |
| itens.catalogo_codigo_item | 7068 | 0 | 0 | 0 |
| itens.criterio_julgamento | 0 | 1883 | 0 | 0 |
| resultados.ordem_classificacao_srp | 11976 | 0 | 0 | 0 |
| resultados.ni_fornecedor | 0 | 0 | 990 | 0 |
| resultados.nome_fornecedor | 0 | 0 | 501 | 1 |
| resultados.porte | 0 | 4893 | 0 | 0 |
| resultados.quantidade_homologada | 0 | 0 | 1267 | 0 |
| resultados.valor_unitario_homologado | 0 | 0 | 1352 | 0 |
| resultados.valor_total_homologado | 0 | 0 | 1332 | 0 |
| resultados.data_cancelamento | 15834 | 0 | 0 | 0 |

## Decisões e contagens da transformação

- Total estimado menor que um real: **59** itens rejeitados.
- Unitario estimado ausente ou nao positivo: **23** itens rejeitados.
- Homologado acima de mil vezes estimado: **7** itens rejeitados.
- Unitario homologado ausente ou nao positivo: **6** itens rejeitados.
- Total acima de um trilhao: **3** itens rejeitados.
- Quantidade ausente ou nao positiva: **1** itens rejeitados.

São 99 rejeições, contando apenas o primeiro motivo de cada item. Os 852 itens sem resultado não são rejeições: não entram na junção. Foram descartados 62 resultados cancelados antes da escolha do vencedor. Em 230 itens válidos, a homologação anterior à publicação foi convertida em NULL, junto com o ciclo.

Dinheiro aceita formatos brasileiros e internacionais. Um separador isolado é decimal: `746.815` representa 746,815. Separadores repetidos representam milhares. Datas aceitam os seis formatos do kit, removem a hora e rejeitam datas impossíveis. CNPJ/CPF preservam zeros; identificador estrangeiro permanece textual. Acentos são reparados quando a conversão Latin-1 para UTF-8 é válida.
