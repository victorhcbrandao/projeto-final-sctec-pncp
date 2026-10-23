-- P2: Quem concentra o volume? A identidade é o NI, não o nome.
WITH fornecedores AS (
 SELECT d.ni_fornecedor, MAX(d.nome_fornecedor) AS nome_fornecedor,
 SUM(f.valor_total_homologado) AS volume, COUNT(*) AS itens
 FROM fato_item_contratado f JOIN dim_fornecedor d USING(sk_fornecedor)
 GROUP BY d.ni_fornecedor
), ranking AS (
 SELECT *, ROW_NUMBER() OVER(ORDER BY volume DESC,ni_fornecedor) AS posicao,
 SUM(volume) OVER() AS volume_geral FROM fornecedores
)
SELECT posicao,ni_fornecedor,nome_fornecedor,itens,volume,
 ROUND(100*volume/NULLIF(volume_geral,0),2) AS participacao_pct,
 ROUND(100*SUM(volume) FILTER(WHERE posicao<=10) OVER()/NULLIF(volume_geral,0),2) AS concentracao_top10_pct
FROM ranking WHERE posicao<=10 ORDER BY posicao;
