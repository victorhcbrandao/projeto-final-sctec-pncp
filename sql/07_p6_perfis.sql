-- P6: Qual é a composição do gasto por perfil?
SELECT perfil_gasto,COUNT(*) AS itens,SUM(valor_total_homologado) AS volume,
 ROUND(100*SUM(valor_total_homologado)/NULLIF(SUM(SUM(valor_total_homologado)) OVER(),0),2) AS participacao_pct,
 ROUND(SUM(valor_total_homologado)/NULLIF(COUNT(*),0),2) AS ticket_medio,
 SUM(economia_valor) AS economia,
 ROUND(100*SUM(economia_valor)/NULLIF(SUM(valor_total_estimado) FILTER(WHERE comparavel=1),0),2) AS economia_pct
FROM fato_item_contratado GROUP BY perfil_gasto ORDER BY volume DESC;
