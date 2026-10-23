-- P1: Quanto foi economizado, com qual cobertura e volume?
SELECT COUNT(*) AS itens, COUNT(DISTINCT numero_controle_pncp) AS contratacoes,
 SUM(valor_total_homologado) AS volume_homologado,
 SUM(valor_total_estimado) FILTER (WHERE comparavel=1) AS estimado_comparavel,
 SUM(economia_valor) AS economia_reais,
 ROUND(100*SUM(economia_valor)/NULLIF(SUM(valor_total_estimado) FILTER (WHERE comparavel=1),0),2) AS economia_pct,
 ROUND(100.0*COUNT(*) FILTER (WHERE comparavel=1)/NULLIF(COUNT(*),0),2) AS itens_comparaveis_pct
FROM fato_item_contratado;
