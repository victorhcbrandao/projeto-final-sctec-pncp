"""Verifica a prova real e a integridade dos CSVs sem depender do banco."""
import json
from decimal import Decimal
import pandas as pd
from .config import PASTA_PROCESSED, PASTA_REPORTS

def validar():
    f = pd.read_csv(PASTA_PROCESSED/'fato_item_contratado.csv', dtype=str, keep_default_na=False)
    verificacoes = []
    def conferir(nome, atual, esperado):
        verificacoes.append({'controle': nome, 'obtido': str(atual), 'esperado': str(esperado), 'ok': bool(atual == esperado)})
    conferir('Itens', len(f), 6126)
    conferir('Grão único', f.duplicated(['numero_controle_pncp','numero_item']).sum(), 0)
    conferir('Contratações', f.numero_controle_pncp.nunique(), 1962)
    conferir('Comparáveis', (f.comparavel=='1').sum(), 5457)
    conferir('Sem ciclo', (f.dias_ciclo=='').sum(), 230)
    conferir('Volume homologado', sum(map(Decimal,f.valor_total_homologado)), Decimal('8044498805.74'))
    conferir('Estimado comparável', sum(map(Decimal,f.loc[f.comparavel=='1','valor_total_estimado'])), Decimal('6867663469.91'))
    conferir('Economia', sum(Decimal(x) for x in f.economia_valor if x), Decimal('992861686.95'))
    conferir('Não comparáveis com economia preenchida', ((f.comparavel=='0') & (f.economia_valor!='')).sum(), 0)
    conferir('Sobrepreço', sum(Decimal(x)<0 for x in f.economia_valor if x), 27)
    for nome,n in [('orgao',363),('fornecedor',2652),('modalidade',7),('localidade',27)]:
        d=pd.read_csv(PASTA_PROCESSED/f'dim_{nome}.csv',dtype=str)
        sk=f'sk_{nome}'
        conferir(f'Dimensão {nome}',len(d),n)
        conferir(f'PK {nome}',d[sk].duplicated().sum(),0)
        conferir(f'FK {nome}',(~f[sk].isin(d[sk])).sum(),0)
    for perfil,n in [('Bens',3310),('Serviços',1849),('Obras e engenharia',967)]:
        conferir(perfil,(f.perfil_gasto==perfil).sum(),n)
    pub=pd.to_datetime(f.data_publicacao)
    hom=pd.to_datetime(f.data_homologacao.replace('',None))
    dias=pd.to_numeric(f.dias_ciclo.replace('',None))
    conferir('Ciclo coerente',(((hom-pub).dt.days.fillna(-1)) != dias.fillna(-1)).sum(),0)
    conferir('Publicação mínima',pub.min().strftime('%Y-%m-%d'),'2025-01-02')
    conferir('Publicação máxima',pub.max().strftime('%Y-%m-%d'),'2025-12-31')
    PASTA_REPORTS.mkdir(exist_ok=True)
    (PASTA_REPORTS/'prova_real.json').write_text(json.dumps(verificacoes,ensure_ascii=False,indent=2),encoding='utf-8')
    erros=[v for v in verificacoes if not v['ok']]
    if erros: raise AssertionError(erros)
    print(f'{len(verificacoes)} controles da prova real aprovados.')
    return verificacoes

if __name__=='__main__': validar()
