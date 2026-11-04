import sys, os, json
import especificacao as esp
import lexer
import erros
import tabela_simbolos
import relatorio
import parser # Importa o novo módulo do analisador sintático

SUCESSO = 0
ERRO_COMPILACAO = 1
ERRO_DE_USO = 2

ARQUIVO_SAIDA = os.path.join('saida', 'tabela_simbolos.json')

# Mantemos a sua função original, mas renomeada para deixar claro seu propósito
def analisar_lexico(entrada):
    analisador = lexer.construir()
    analisador.input(entrada)
    encontrados = []

    for token in analisador:
        coluna = lexer.encontrar_coluna(entrada, token)
        encontrados.append((token.lineno, coluna, token.type, token.value))

        if token.type in esp.CATEGORIAS:
            tabela_simbolos.registrar(token.value, token.type, token.lineno, coluna)

    return encontrados

def ler_entrada(caminho):
    try:
        with open(caminho, encoding='utf-8') as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        print(f'erro: arquivo nao encontrado: {caminho}')
    except UnicodeDecodeError:
        print(f'erro: {caminho} nao esta em UTF-8')
    return None

def main():
    # Espera exatamente um argumento: o caminho do arquivo .tonto
    if len(sys.argv) != 2:
        print('uso: python src/main.py <arquivo.tonto>')
        return ERRO_DE_USO

    entrada = ler_entrada(sys.argv[1])
    if entrada is None:
        return ERRO_DE_USO
    
    # 1. Executa a Análise Léxica (extrai tokens e popula a tabela de símbolos)
    tokens = analisar_lexico(entrada)
    
    # 2. Executa a Análise Sintática (constrói a árvore e captura erros de sintaxe)
    arvore_ontologia = parser.analisar(entrada)
    
    # 3. Relatórios Léxicos
    relatorio.mostrar_visao_analitica(tokens)
    print()
    relatorio.mostrar_tabela_sintese()
    print()
    
    # 4. Relatórios Sintáticos
    if arvore_ontologia:
        relatorio.mostrar_sintese_sintatica(arvore_ontologia)
        print()
    relatorio.mostrar_erros_sintaticos(parser.ERROS_SINTATICOS)

    # Verifica se houve falha em qualquer uma das fases
    houve_erro_lexico = len(erros.ERROS) > 0
    houve_erro_sintatico = len(parser.ERROS_SINTATICOS) > 0

    if houve_erro_lexico or houve_erro_sintatico:
        return ERRO_COMPILACAO
        
    return SUCESSO

if __name__ == '__main__':
    sys.exit(main())