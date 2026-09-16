import erros
import tabela_simbolos

# Nome interno do token -> rotulo em portugues, na ordem em que aparecem na
# tabela de sintese.
from especificacao import CATEGORIAS


def mostrar_visao_analitica(tokens):
    print('VISAO ANALITICA')
    print(f"{'LINHA':>6} {'COL':>5}  {'TOKEN':<16} LEXEMA")
    for linha, coluna, tipo, lexema in tokens:
        print(f"{linha:>6} {coluna:>5}  {tipo:<16} {lexema}")


def mostrar_tabela_sintese():
    print('TABELA DE SINTESE')
    print(f"{'CATEGORIA':<28} {'DISTINTOS':>9}  {'OCORRENCIAS':>11}")
    for token, rotulo in CATEGORIAS.items():
        print(f"{rotulo:<28} {tabela_simbolos.distintos(token):>9}  "
              f"{tabela_simbolos.ocorrencias(token):>11}")


def mostrar_exportacao(caminho):
    print(f'Tabela de simbolos exportada para {caminho}')


def mostrar_erros():
    if not erros.ERROS:
        return

    print(f'ERROS LEXICOS ({len(erros.ERROS)})')
    for erro in erros.ERROS:
        print(f"  Erro lexico: simbolo nao reconhecido '{erro['lexema']}' "
              f"na linha {erro['linha']}, coluna {erro['coluna']}")
