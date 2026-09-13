import ply.lex as lex
import especificacao as esp

tokens = [
    # categorias resolvidas por consulta
    'EST_CLASSE', # estereotipo de classe: kind, role, phase...
    'EST_RELACAO', # estereotipo de relacao: componentOf, mediation...
    'RESERVADA', # palavra reservada: package, import, genset...
    'TIPO_NATIVO', # tipo nativo: string, number, date...
    'META_ATRIBUTO', # meta-atributo: ordered, const, derived...

    # categorias resolvidas pela forma do lexema
    'NOME_CLASSE', # inicia com maiuscula, sem numeros
    'NOME_RELACAO', # inicia com minuscula, sem numeros
    'NOME_INSTANCIA', # termina em numero inteiro
    'NOVO_TIPO', # termina com a subcadeia DataType
    'INTEIRO', # numero usado em cardinalidade: [1..*]

    # simbolos especiais
    'ABRE_CHAVE', 'FECHA_CHAVE', 'ABRE_PAR', 'FECHA_PAR',
    'ABRE_COL', 'FECHA_COL', 'INTERVALO', 'AGREG_ESQ', 'AGREG_DIR',
    'ASTERISCO', 'ARROBA', 'DOIS_PONTOS',

    # extensoes: presentes nos arquivos .tonto
    'COMPOSICAO', # <o>-- : composicao
    'CONECTOR', # -- : conector de relacao comum
    'VIRGULA', # , : separa itens de specifics e de enum
]

# ---------------------------------------------------------------------------------
# REGRAS
#
# Observação: O PLY testa as funções na ordem em que aparecem no arquivo e para na
# primeira que casar, não na que casa mais caracteres, como faz o Flex.
# Por isso utilizamos a ordem abaixo.
# ---------------------------------------------------------------------------------

# Palavra reservada com hifen, que não casa com nenhum outro padrão de nome
def t_RESERVADA(t):
    r'functional-complexes'
    return t

# Antes de NOME_CLASSE e NOME_RELACAO: senao Planeta1 viraria Planeta + 1.
def t_NOME_INSTANCIA(t):
    r'[A-Za-z][A-Za-z]*(_[A-Za-z]+)*[0-9]+'
    return t

# Decidimos tratar NOVO_TIPO como uma categoria especial, pois é um subconjunto de NOME_CLASSE, ou seja, todo CPFDataType também é um nome de classe válido.
# A regra separada antes pegaria apenas o prefixo de MyDataTypeThing, por exemplo.
# E depois, jamais seria alcançada. Por isso, a categoria é decidida após o casamento.
def t_NOME_CLASSE(t):
    r'[A-Z][A-Za-z]*(_[A-Za-z]+)*'

    # Caso o lexema termine com 'DataType' e não tenha sublinhado, é um NOVO_TIPO.
    if t.value.endswith('DataType') and '_' not in t.value:
        t.type = 'NOVO_TIPO'
    return t


def t_NOME_RELACAO(t):
    r'[a-z][A-Za-z]*(_[A-Za-z]+)*'

    # As 64 palavras reservadas começam com minuscula, logo colidem só com este padrão.
    t.type = esp.RESERVADAS.get(t.value, 'NOME_RELACAO')
    return t


def t_INTEIRO(t):
    r'[0-9]+'
    return t


# --- Operadores de vários caracteres ---

# 5 caracteres: tem de ser testado antes de <>-- e de --
def t_COMPOSICAO(t):
    r'<o>--'
    return t


def t_AGREG_ESQ(t):
    r'<>--'
    return t


# Antes de CONECTOR, se não o -- inicial seria consumido sozinho
def t_AGREG_DIR(t):
    r'--<>'
    return t


def t_CONECTOR(t):
    r'--'
    return t


def t_INTERVALO(t):
    r'\.\.'
    return t


# --------------------------
# SIMBOLOS DE UM CARACTERE
# --------------------------

t_ABRE_CHAVE  = r'\{'
t_FECHA_CHAVE = r'\}'
t_ABRE_PAR    = r'\('
t_FECHA_PAR   = r'\)'
t_ABRE_COL    = r'\['
t_FECHA_COL   = r'\]'
t_ASTERISCO   = r'\*'
t_ARROBA      = r'@'
t_DOIS_PONTOS = r':'
t_VIRGULA     = r','

# --------------------------------------
# ESPAÇOS EM BRANCO E CONTAGEM DE LINHA
# --------------------------------------

# Espaço e tabulação são ignorados
t_ignore = ' \t'

# Encontrou quebra de linha, incrementa o contador de linhas do lexer e não devolve token.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Encontra a coluna do token, que é a distância até a última quebra de linha antes do lexema.
def encontrar_coluna(entrada, token):
    inicio_linha = entrada.rfind('\n', 0, token.lexpos) + 1

    return (token.lexpos - inicio_linha) + 1


# ----------------
# ERRO LEXICO
# ----------------

def t_error(t):
    # Apenas imprime a mensagem de erro, sem interromper a analise.
    print(f'[erro lexico] linha {t.lexer.lineno}: caractere inesperado {t.value[0]!r}')

    t.lexer.skip(1)


# ------------------------------
# CONSTRUÇÃO DO ANALISADOR
# ------------------------------

def construir():
    # O PLY lê as regras deste modulo, gera o NFA pelo algoritmo de Thompson, converte em DFA por construção de subconjuntos e devolve o simulador.
    return lex.lex()
