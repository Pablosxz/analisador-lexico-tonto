
import sys, os, json
import especificacao as esp
import lexer, erros, tabela_simbolos, relatorio

# Codigos de saida do programa
SUCESSO = 0
ERRO_LEXICO = 1
ERRO_DE_USO = 2

# Onde a tabela de simbolos e gravada, relativo ao diretorio de execucao.
ARQUIVO_SAIDA = os.path.join('saida', 'tabela_simbolos.json')

def analisar(entrada):
    # Constroi o analisador a partir das regras do lexer.py e percorre a entrada.
    analisador = lexer.construir()
    analisador.input(entrada)

    encontrados = []

    # Iterar sobre o lexer devolve um token por vez até o fim do arquivo.
    for token in analisador:
        coluna = lexer.encontrar_coluna(entrada, token)

        # Tupla na ordem em que o relatorio.py a desempacota.
        encontrados.append((token.lineno, coluna, token.type, token.value))

        # Só vai para a tabela de simbolos o que a tabela de categorias conta
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


def exportar_tabela(caminho):
    # Cria o diretório na primeira execução e reescreve o arquivo nas seguintes
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, 'w', encoding='utf-8') as arquivo:
        json.dump(tabela_simbolos.serializar(), arquivo,
                  ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) != 2:
        print('uso: python src/main.py <arquivo.tonto>')
        return ERRO_DE_USO

    entrada = ler_entrada(sys.argv[1])
    if entrada is None:
        return ERRO_DE_USO

    tokens = analisar(entrada)

    # Visão analítica: lista de tokens, com linha, coluna, tipo e lexema.
    relatorio.mostrar_visao_analitica(tokens)
    print()

    # Visão sintética: tabela de simbolos, com nome, tipo, linha e coluna.
    relatorio.mostrar_tabela_sintese()
    print()

    # Saida estruturada
    exportar_tabela(ARQUIVO_SAIDA)
    relatorio.mostrar_exportacao(ARQUIVO_SAIDA)
    print()

    relatorio.mostrar_erros()

    # Sai com codigo 1 quando houve erro lexico
    return ERRO_LEXICO if erros.ERROS else SUCESSO


if __name__ == '__main__':
    sys.exit(main())
