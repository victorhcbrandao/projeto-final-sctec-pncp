"""Acesso PostgreSQL. Transacoes sao controladas pelo chamador."""
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from src import config

def conectar(database=None):
    try:
        return psycopg2.connect(dbname=database or config.PG_DATABASE, connect_timeout=10, **config.PG_CONFIG)
    except (psycopg2.Error, UnicodeDecodeError) as exc:
        raise RuntimeError("Falha de conexao. Confira servico, usuario, porta e senha no .env local.") from exc

def preparar_banco(recriar=False):
    if config.PG_DATABASE in {"postgres", "template0", "template1"}:
        raise ValueError("Escolha um banco de projeto, nao um banco administrativo.")
    con = conectar("postgres")
    try:
        con.autocommit = True
        with con.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (config.PG_DATABASE,))
            existe = cur.fetchone() is not None
            if existe and not recriar:
                raise RuntimeError("Banco ja existe. Para apaga-lo e reconstruir conscientemente, use --recriar.")
            if existe:
                cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=%s AND pid<>pg_backend_pid()", (config.PG_DATABASE,))
                cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(config.PG_DATABASE)))
            cur.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(config.PG_DATABASE)))
    finally:
        con.close()

def executar_script(conexao, caminho):
    with conexao.cursor() as cur:
        cur.execute(caminho.read_text(encoding="utf-8"))

def consultar(conexao, comando, params=None):
    with conexao.cursor() as cur:
        cur.execute(comando, params)
        return cur.fetchall()

def inserir_em_lote(conexao, tabela, colunas, linhas):
    if not linhas: return
    comando=sql.SQL("INSERT INTO {} ({}) VALUES %s").format(sql.Identifier(tabela),sql.SQL(", ").join(map(sql.Identifier,colunas)))
    with conexao.cursor() as cur:
        execute_values(cur,comando.as_string(conexao),linhas,page_size=2000)
