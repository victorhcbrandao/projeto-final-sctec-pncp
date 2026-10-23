"""Auditoria por arquivo e coluna; contagens sao de celulas afetadas, sem somar grupos sobrepostos."""
import json
import pandas as pd
from src import config, limpeza

def main():
    registros = []
    for arquivo in ["compras", "itens", "resultados"]:
        df = pd.read_csv(config.PASTA_RAW / f"{arquivo}.csv", dtype=str, keep_default_na=False)
        for coluna in df:
            serie = df[coluna]
            normal = serie.map(limpeza.remover_invisiveis).map(lambda x: limpeza.consertar_acento(x.strip(" "))).map(limpeza.tirar_espacos)
            registros.append({"arquivo":arquivo,"coluna":coluna,"linhas":len(df),
                "vazios":int((serie=="").sum()),
                "nulos_disfarcados_texto":int(((normal!="") & normal.map(limpeza.eh_nulo)).sum()),
                "espacos_ou_invisiveis":int((serie.map(limpeza.remover_invisiveis).map(limpeza.tirar_espacos)!=serie).sum()),
                "encoding_corrigido":int((serie.map(limpeza.consertar_acento)!=serie).sum())})
    config.PASTA_REPORTS.mkdir(exist_ok=True)
    pd.DataFrame(registros).to_csv(config.PASTA_REPORTS / "auditoria_colunas.csv",index=False,encoding="utf-8")
    print(f"Auditoria de {len(registros)} colunas salva em reports/auditoria_colunas.csv")

if __name__ == "__main__": main()
