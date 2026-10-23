"""Orquestra auditoria, transformacao e, opcionalmente, carga PostgreSQL."""
import argparse,subprocess,sys
def main():
    p=argparse.ArgumentParser();p.add_argument('--carregar',action='store_true');p.add_argument('--recriar',action='store_true');a=p.parse_args()
    if a.recriar and not a.carregar:p.error('--recriar exige --carregar')
    for m in ['limpeza','auditar','montar_tabelas','validar']:
        subprocess.run([sys.executable,'-m','src.'+m],check=True)
    if a.carregar:subprocess.run([sys.executable,'-m','src.carregar']+(['--recriar'] if a.recriar else []),check=True)
if __name__=='__main__':main()
