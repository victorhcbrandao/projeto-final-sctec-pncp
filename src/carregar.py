"""Carga atomica das cinco tabelas. Recriacao de banco existente exige --recriar."""
import argparse
import json
from decimal import Decimal
from datetime import date
import pandas as pd
from src import config

TABELAS = ["dim_orgao","dim_fornecedor","dim_modalidade","dim_localidade","fato_item_contratado"]
def ler_tabelas():
    dados={n:pd.read_csv(config.PASTA_PROCESSED/f"{n}.csv",dtype=str,keep_default_na=False) for n in TABELAS}
    fato=dados["fato_item_contratado"]
    if fato.duplicated(["numero_controle_pncp","numero_item"]).any():raise ValueError("Grao duplicado")
    for nome in TABELAS[:-1]:
        dim=dados[nome];sk=dim.columns[0]
        if dim[sk].duplicated().any() or not set(fato[sk])<=set(dim[sk]):raise ValueError(f"Chave invalida: {sk}")
    for col in ['quantidade','valor_unitario_estimado','valor_unitario_homologado']:
        if any(not x or Decimal(x)<=0 for x in fato[col]):raise ValueError(f"Medida invalida: {col}")
    return dados

def tuplas(df):
    def valor(c,v):
        if v=="":return None
        if c.startswith('sk_') or c in {'numero_item','modalidade_id','comparavel','dias_ciclo'}:return int(v)
        if c.startswith('valor_') or c in {'quantidade','economia_valor'}:return Decimal(v)
        if c.startswith('data_'):return date.fromisoformat(v)
        return v
    return [tuple(valor(c,v) for c,v in zip(df.columns,row)) for row in df.itertuples(index=False,name=None)]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recriar',action='store_true',help='APAGA o banco do projeto, encerra suas conexoes e cria novamente')
    args=parser.parse_args()
    dados=ler_tabelas()  # valida ANTES de qualquer operacao no banco
    from src import banco
    banco.preparar_banco(args.recriar)
    con=banco.conectar()
    try:
        with con:  # commit unico; qualquer erro reverte DDL e todas as cargas
            banco.executar_script(con,config.PASTA_SQL/'01_criar_banco.sql')
            for nome in TABELAS:
                df=dados[nome];banco.inserir_em_lote(con,nome,list(df.columns),tuplas(df))
            contagens={n:banco.consultar(con,f'SELECT COUNT(*) FROM {n}')[0][0] for n in TABELAS}
            for n in TABELAS:
                if contagens[n]!=len(dados[n]):raise ValueError(f'Contagem divergente: {n}')
        config.PASTA_REPORTS.mkdir(exist_ok=True)
        (config.PASTA_REPORTS/'validacao_banco.json').write_text(json.dumps(contagens,indent=2),encoding='utf-8')
        print('Carga concluida e confirmada:',contagens)
    except Exception:
        print('Carga revertida. Nenhuma tabela parcialmente carregada foi confirmada.')
        raise
    finally:
        con.close()

if __name__=='__main__':main()
