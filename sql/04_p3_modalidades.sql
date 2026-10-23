-- P3: Como volume e economia variam por modalidade?
SELECT d.modalidade_id,d.nome_modalidade,COUNT(*) AS itens,
 SUM(f.valor_total_homologado) AS volume,
 SUM(f.economia_valor) AS economia,
 ROUND(100*SUM(f.economia_valor)/NULLIF(SUM(f.valor_total_estimado) FILTER(WHERE comparavel=1),0),2) AS economia_pct,
 ROUND(100*SUM(f.valor_total_homologado)/NULLIF(SUM(SUM(f.valor_total_homologado)) OVER(),0),2) AS participacao_volume_pct
FROM fato_item_contratado f JOIN dim_modalidade d USING(sk_modalidade)
GROUP BY d.modalidade_id,d.nome_modalidade ORDER BY volume DESC;
