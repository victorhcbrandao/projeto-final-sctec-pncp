from datetime import date
import pytest
from src import limpeza
from src.limpeza import CASOS, converter_numero, converter_data, limpar_documento
from src.validar import validar

@pytest.mark.parametrize('funcao,argumentos,esperado', CASOS)
def test_casos_fornecidos(funcao,argumentos,esperado):
    assert getattr(limpeza, funcao)(*argumentos)==esperado

@pytest.mark.parametrize('entrada,esperado', [('746.815',746.815),('1.234.567',1234567),('1,234.56',1234.56),('(1.500,00)',-1500),('0',0)])
def test_numeros_ambiguos(entrada,esperado):
    assert converter_numero(entrada)==esperado

def test_datas_impossiveis_e_estrangeiro():
    assert converter_data('31/02/2025') is None
    assert converter_data('2025-01-02T00:00:00')==date(2025,1,2)
    assert limpar_documento('abc-123','PE')=='ABC-123'

def test_prova_real_integral():
    assert all(v['ok'] for v in validar())
