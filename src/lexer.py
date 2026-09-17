import ply.lex as lex
import especificacao as esp
import erros

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

# Naturezas ontológicas: as tres palavras da linguagem escritas com hifen.
# Precisam de regra propria porque o hifen nao faz parte de nenhum padrao de nome.
def t_RESERVADA(t):
    r'functional-complexes|intrinsic-modes|extrinsic-modes'
    return t

# Novo tipo de dado: inicia com letra, sem numeros nem separadores, e termina com a subcadeia DataType.
# O (?!...) no fim exige que NADA de nome venha depois do DataType.
def t_NOVO_TIPO(t):
    r'[A-Za-z]+DataType(?![A-Za-z0-9_-])'
    return t

# Nome de instancia: inicia com qualquer letra e termina em numero. Ex.: Planeta1, pizza03.
# Antes de NOME_CLASSE e NOME_RELACAO: senao Planeta1 viraria Planeta + 1.
def t_NOME_INSTANCIA(t):
    r'[A-Za-z][A-Za-z]*([_-][A-Za-z]+)*[0-9]+'
    return t


# Nome de classe: inicia com maiuscula, sem numeros, com sublinhado ou hifen
# entre letras. Ex.: Person, Second_Baptist_Church.
def t_NOME_CLASSE(t):
    r'[A-Z][A-Za-z]*([_-][A-Za-z]+)*_?'
    return t


# Nome de relacao: mesmo padrao, iniciando com minuscula. Ex.: hasParent, is_part_of.
# Pega tambem as palavras da linguagem, que tem esta mesma forma (por isso a consulta).
def t_NOME_RELACAO(t):
    r'[a-z][A-Za-z]*([_-][A-Za-z]+)*_?'

    # As 64 palavras reservadas começam com minuscula, logo colidem só com este padrão.
    t.type = esp.RESERVADAS.get(t.value, 'NOME_RELACAO')
    return t


# Inteiro: aparece apenas em cardinalidade. Ex.: o 1 e o 2 em [1..2].
def t_INTEIRO(t):
    r'[0-9]+'
    return t


# --- Operadores de vários caracteres ---

# Composicao: a parte não é compartilhavel com outro todo.
# 5 caracteres: tem de ser testado antes de <>-- e de --
def t_COMPOSICAO(t):
    r'<o>--'
    return t


# Agregacao com o losango a esquerda: o todo e a classe do lado esquerdo.
def t_AGREG_ESQ(t):
    r'<>--'
    return t


# Agregacao espelhada: o todo e a classe do lado direito.
# Antes de CONECTOR, se não o -- inicial seria consumido sozinho
def t_AGREG_DIR(t):
    r'--<>'
    return t


# Conector de relacao comum, sem losango. Ex.: [1..*] -- [1] Employee.
def t_CONECTOR(t):
    r'--'
    return t


# Intervalo de cardinalidade. O ponto isolado nao e token da linguagem: so o par.
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

# ------------------------------------------------
# COMENTÁRIOS, ESPAÇOS EM BRANCO E CONTAGEM DE LINHA
# ------------------------------------------------

# Comentario de varias linhas. Reconhecido e descartado: sem return, nao vira token.
def t_comentario_bloco(t):
    r'/\*[\s\S]*?\*/'

    t.lexer.lineno += t.value.count('\n')

# Comentario de uma linha, tambem descartado.
# Não consome o \n final: ele fica para t_newline, que mantém o contador.
def t_comentario_linha(t):
    r'//[^\n]*'

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

# Chamada quando nenhum padrao casa com o caractere na posicao atual.
def t_error(t):
    # t.lexer.lexdata guarda a entrada inteira, o que permite calcular a coluna.
    coluna = encontrar_coluna(t.lexer.lexdata, t)
    erros.registrar(t.value[0], t.lexer.lineno, coluna)

    # Recupera e segue no próximo caractere, em vez de abortar a analise.
    t.lexer.skip(1)


# ------------------------------
# CONSTRUÇÃO DO ANALISADOR
# ------------------------------

def construir():
    # O PLY lê as regras deste modulo, gera o NFA pelo algoritmo de Thompson, converte em DFA por construção de subconjuntos e devolve o simulador.
    return lex.lex()
