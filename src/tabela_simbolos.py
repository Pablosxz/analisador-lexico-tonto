# Registro dos lexemas encontrados na analise.
# Cada entrada: lexema -> {'categoria', 'ocorrencias'}, onde 'ocorrencias' e a
# lista de pares (linha, coluna) em que aquele lexema apareceu.
SIMBOLOS = {}


def registrar(lexema, categoria, linha, coluna):
    # O lexema sozinho basta como chave: o lexer classifica pela forma, entao um
    # mesmo lexema cai sempre na mesma categoria.
    entrada = SIMBOLOS.setdefault(lexema, {'categoria': categoria, 'ocorrencias': []})
    entrada['ocorrencias'].append((linha, coluna))


def distintos(categoria):
    # Quantos nomes diferentes daquela categoria aparecem no arquivo.
    return sum(1 for e in SIMBOLOS.values() if e['categoria'] == categoria)


def ocorrencias(categoria):
    # Quantas vezes, no total, os nomes daquela categoria aparecem.
    return sum(len(e['ocorrencias']) for e in SIMBOLOS.values()
               if e['categoria'] == categoria)
