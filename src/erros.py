# erros.py - registro dos erros lexicos encontrados na analise.

# Lista de erros encontrados. Cada item: {'linha', 'coluna', 'lexema'}.
ERROS = []

def registrar(lexema, linha, coluna):
    # Chamada pelo t_error do lexer quando nenhum padrao casa com o caractere.
    ERROS.append({
        'linha': linha,
        'coluna': coluna,
        'lexema': lexema,
    })
