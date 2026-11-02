
import sys, os, json  # sys: argv/exit; os: caminhos e diretórios; json: exportação da tabela
import especificacao as esp  # esp.CATEGORIAS: quais tipos de token contam para a tabela de simbolos
import lexer, erros, tabela_simbolos, relatorio
import relatorio
import parser

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
        # PLY só da lineno/lexpos de graça; a coluna e calculada a mao aqui.
        coluna = lexer.encontrar_coluna(entrada, token)

        # Ordem em que o relatorio.py a desempacota.
        encontrados.append((token.lineno, coluna, token.type, token.value))

        # Só vai para a tabela de simbolos o que a tabela de categorias conta
        # (simbolos especiais como { ( -- ficam de fora)
        if token.type in esp.CATEGORIAS:
            tabela_simbolos.registrar(token.value, token.type, token.lineno, coluna)

    return encontrados


def ler_entrada(caminho):
    # Erros esperados (arquivo ausente / encoding invalido) viram mensagem
    # amigavel e None, em vez de propagar a excecao ate o topo.
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
        # ensure_ascii=False preserva acentos no JSON em vez de escapar \uXXXX
        json.dump(tabela_simbolos.serializar(), arquivo,
                  ensure_ascii=False, indent=2)


def main():
    # Espera exatamente um argumento: o caminho do arquivo .tonto
    if len(sys.argv) != 2:
        print('uso: python src/main.py <arquivo.tonto>')
        return ERRO_DE_USO

    entrada = ler_entrada(sys.argv[1])
    
    # 1. Executa a Análise Sintática (que puxa o léxico internamente)
    arvore_ontologia = parser.analisar(entrada)
    
    # 2. Mostra os Relatórios Léxicos que você já tinha feito
    # (Supondo que você ajustou analisar() para devolver os tokens léxicos também)
    # relatorio.mostrar_visao_analitica(tokens) 
    # relatorio.mostrar_tabela_sintese()
    
    # 3. Mostra o Novo Relatório Sintático
    relatorio.mostrar_sintese_sintatica(arvore_ontologia)
    relatorio.mostrar_erros_sintaticos(parser.ERROS_SINTATICOS)

    # Sai com codigo 1 quando houve erro lexico
    return ERRO_LEXICO if erros.ERROS else SUCESSO


if __name__ == '__main__':
    sys.exit(main())
