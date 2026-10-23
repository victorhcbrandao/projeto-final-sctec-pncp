-- P1: Quanto foi economizado, com qual cobertura e volume?
SELECT COUNT(*) AS itens, COUNT(DISTINCT numero_controle_pncp) AS contratacoes,
 SUM(valor_total_homologado) AS volume_homologado,
 SUM(valor_total_estimado) FILTER (WHERE comparavel=1) AS estimado_comparavel,
 SUM(economia_valor) AS economia_reais,
 ROUND(100*SUM(economia_valor)/NULLIF(SUM(valor_total_estimado) FILTER (WHERE comparavel=1),0),2) AS economia_pct,
 ROUND(100.0*COUNT(*) FILTER (WHERE comparavel=1)/NULLIF(COUNT(*),0),2) AS itens_comparaveis_pct
FROM fato_item_contratado;


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


-- P3: Como volume e economia variam por modalidade?
SELECT d.modalidade_id,d.nome_modalidade,COUNT(*) AS itens,
 SUM(f.valor_total_homologado) AS volume,
 SUM(f.economia_valor) AS economia,
 ROUND(100*SUM(f.economia_valor)/NULLIF(SUM(f.valor_total_estimado) FILTER(WHERE comparavel=1),0),2) AS economia_pct,
 ROUND(100*SUM(f.valor_total_homologado)/NULLIF(SUM(SUM(f.valor_total_homologado)) OVER(),0),2) AS participacao_volume_pct
FROM fato_item_contratado f JOIN dim_modalidade d USING(sk_modalidade)
GROUP BY d.modalidade_id,d.nome_modalidade ORDER BY volume DESC;


-- P4: Quais nomes de órgãos têm maior ciclo? Pelo menos 5 ciclos válidos.
SELECT d.nome_orgao, COUNT(f.dias_ciclo) AS ciclos_validos,
 ROUND(AVG(f.dias_ciclo),1) AS ciclo_medio_dias,MAX(f.dias_ciclo) AS ciclo_maximo_dias,
 COUNT(*) FILTER(WHERE f.dias_ciclo IS NULL) AS itens_sem_ciclo
FROM fato_item_contratado f JOIN dim_orgao d USING(sk_orgao)
GROUP BY d.nome_orgao HAVING COUNT(f.dias_ciclo)>=5
ORDER BY ciclo_medio_dias DESC,d.nome_orgao;
-- Datas anteriores à publicação são ausentes, nunca ciclos negativos ou zero artificial.
SELECT COUNT(dias_ciclo) AS ciclos_validos,COUNT(*) FILTER(WHERE dias_ciclo IS NULL) AS sem_ciclo,
 ROUND(AVG(dias_ciclo),1) AS media,MAX(dias_ciclo) AS maximo FROM fato_item_contratado;


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


-- P6: Qual é a composição do gasto por perfil?
SELECT perfil_gasto,COUNT(*) AS itens,SUM(valor_total_homologado) AS volume,
 ROUND(100*SUM(valor_total_homologado)/NULLIF(SUM(SUM(valor_total_homologado)) OVER(),0),2) AS participacao_pct,
 ROUND(SUM(valor_total_homologado)/NULLIF(COUNT(*),0),2) AS ticket_medio,
 SUM(economia_valor) AS economia,
 ROUND(100*SUM(economia_valor)/NULLIF(SUM(valor_total_estimado) FILTER(WHERE comparavel=1),0),2) AS economia_pct
FROM fato_item_contratado GROUP BY perfil_gasto ORDER BY volume DESC;
