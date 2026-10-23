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
