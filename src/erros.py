# Lista de erros encontrados na analise.
# Cada item: {'linha', 'coluna', 'lexema', 'contexto', 'sugestao'}
ERROS = []

# Caracteres que o TONTO admite dentro de um identificador. Utilizamos para reconstruir a palavra em volta do erro.
_CARACTERES_DE_PALAVRA = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'


def contexto(entrada, posicao):
    # O PLY entrega apenas o caractere que falhou, não a palavra inteira.
    inicio = posicao
    while inicio > 0 and entrada[inicio - 1] in _CARACTERES_DE_PALAVRA:
        inicio -= 1

    fim = posicao + 1
    while fim < len(entrada) and entrada[fim] in _CARACTERES_DE_PALAVRA:
        fim += 1

    return entrada[inicio:fim]


def sugerir(caractere, palavra):
    # Cada retorno é uma sugestao compativel com a especificação da linguagem
    if caractere == '_':
        if palavra.startswith('_'):
            return ("nomes nao podem comecar com sublinhado; o sublinhado deve "
                    "ficar entre letras, como em Second_Baptist_Church")
        if palavra.endswith('_'):
            return ("nomes nao podem terminar com sublinhado; remova-o ou "
                    "acrescente ao menos uma letra depois dele")
        if '__' in palavra:
            return "sublinhado duplo nao e permitido; use um unico sublinhado entre letras"
        return "o sublinhado deve aparecer entre letras, nunca junto a numeros ou simbolos"

    if caractere == '.':
        return "ponto isolado nao e um token; TONTO usa '..' em cardinalidade, como em [1..*]"

    # Hifen: só existe dentro de 'functional-complexes' e nos operadores de relação.
    if caractere == '-':
        if len(palavra) > 1:
            return ("hifen em nome nao e permitido; a unica palavra da linguagem com "
                    f"hifen e 'functional-complexes' - verifique a grafia de '{palavra}'")
        return ("hifen isolado; os operadores de relacao validos sao '--', "
                "'<>--', '--<>' e '<o>--'")

    # Operador de relacao incompleto.
    if caractere in '<>':
        return ("operador de relacao incompleto; as formas validas sao '<>--', "
                "'--<>' e '<o>--'")

    # Ponto e virgula
    if caractere == ';':
        return "TONTO nao usa ponto e virgula; declaracoes terminam com o fim da linha"

    # Igual: não existe atribuicao na linguagem
    if caractere == '=':
        return "nao existe atribuicao em TONTO; o tipo de um atributo e dado por ':'"

    # Aspas: a linguagem não define literais de cadeia
    if caractere in '"\'':
        return "TONTO nao define literais de cadeia; 'string' e um tipo, nao um valor entre aspas"

    # Letra acentuada ou fora do ASCII: os padroes de nome aceitam apenas A-Z e a-z.
    if not caractere.isascii() and caractere.isalpha():
        return (f"'{caractere}' nao e aceito em nomes; use apenas letras sem acento, "
                "como em Orgao em vez de Órgão")

    # Ultimo caso: nada mais se aplica.
    return "caractere nao pertence ao alfabeto da linguagem TONTO"


def registrar(entrada, posicao, linha, coluna):
    # Chamada pelo t_error do lexer
    caractere = entrada[posicao]
    palavra = contexto(entrada, posicao)

    # Um unico erro de digitacao pode disparar t_error mais de uma vez, por isso, não registramos o mesmo erro mais de uma vez.
    if ERROS and ERROS[-1]['linha'] == linha and ERROS[-1]['contexto'] == palavra:
        return

    ERROS.append({
        'linha': linha,
        'coluna': coluna,
        'lexema': caractere,
        'contexto': palavra,
        'sugestao': sugerir(caractere, palavra),
    })


def limpar():
    # Zera a lista entre analises
    ERROS.clear()
