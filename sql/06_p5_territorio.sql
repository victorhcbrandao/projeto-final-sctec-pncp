-- P5: Como o volume e a economia se distribuem territorialmente?
SELECT d.regiao,d.uf_sigla,SUM(f.valor_total_homologado) AS volume,
 SUM(f.economia_valor) AS economia,
 ROUND(100*SUM(f.economia_valor)/NULLIF(SUM(f.valor_total_estimado) FILTER(WHERE comparavel=1),0),2) AS economia_pct
FROM fato_item_contratado f JOIN dim_localidade d USING(sk_localidade)
GROUP BY d.regiao,d.uf_sigla ORDER BY volume DESC;
SELECT d.regiao,SUM(f.valor_total_homologado) AS volume,
 SUM(f.economia_valor) AS economia,
 ROUND(100*SUM(f.economia_valor)/NULLIF(SUM(f.valor_total_estimado) FILTER(WHERE comparavel=1),0),2) AS economia_pct
FROM fato_item_contratado f JOIN dim_localidade d USING(sk_localidade)
GROUP BY d.regiao ORDER BY volume DESC;
