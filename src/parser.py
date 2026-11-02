# parser.py - analisador sintático da linguagem TONTO

import ply.yacc as yacc
import lexer
from lexer import tokens  # o PLY usa a mesma lista de tokens do léxico

# Erros sintáticos encontrados, usados no relatório de erros.
ERROS_SINTATICOS = []


# =============================================================================
# 1. ARQUIVO, PACOTES E IMPORTS
# =============================================================================
# A primeira regra é o símbolo inicial: o arquivo inteiro.

def p_ontologia(p):
    'ontologia : lista_imports lista_pacotes'
    pacotes = p[2]
    # Imports escritos antes do primeiro package pertencem a ele.
    pacotes[0]['imports'] = p[1] + pacotes[0]['imports']
    p[0] = pacotes


def p_lista_imports(p):
    '''lista_imports : lista_imports importacao
                     | vazio'''
    if len(p) == 3: # lista_imports importacao
        p[0] = p[1] + [p[2]]
    else: # vazio
        p[0] = []


def p_importacao(p):
    'importacao : IMPORT nome'
    p[0] = {'construto': 'import', 'nome': p[2], 'linha': p.lineno(1)}


def p_lista_pacotes(p):
    '''lista_pacotes : lista_pacotes pacote
                     | pacote'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_pacote(p):
    'pacote : PACKAGE nome conteudo'
    elementos = p[3]
    p[0] = {
        'construto': 'pacote',
        'nome': p[2],
        'linha': p.lineno(1),
        'imports': [e for e in elementos if e['construto'] == 'import'],
        'declaracoes': [e for e in elementos if e['construto'] != 'import'],
    }


def p_conteudo(p):
    '''conteudo : conteudo elemento
                | vazio'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_elemento(p):
    '''elemento : importacao
                | classe
                | enum_decl
                | datatype_decl'''
    p[0] = p[1]  # repassa o que já foi montado


# =============================================================================
# 2. CLASSES
# =============================================================================

def p_classe(p):
    'classe : EST_CLASSE nome natureza heranca corpo_classe'
    p[0] = {
        'construto': 'classe',
        'estereotipo': p[1], # kind, role, phase...
        'nome': p[2],
        'linha': p.lineno(1),
        'pais': p[4], # classes que ela especializa
        'atributos': p[5],
    }


# "of functional-complexes, relators": precisa ser reconhecido para aceitar
# o arquivo, mas não é usado nas saídas, então não guarda nada em p[0].
def p_natureza(p):
    '''natureza : OF lista_naturezas
                | vazio'''


def p_lista_naturezas(p):
    '''lista_naturezas : lista_naturezas VIRGULA NATUREZA
                       | NATUREZA'''


def p_heranca(p):
    '''heranca : SPECIALIZES lista_nomes
               | vazio'''
    p[0] = p[2] if len(p) == 3 else []


def p_lista_nomes(p):
    '''lista_nomes : lista_nomes VIRGULA nome
                   | nome'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# Corpo opcional entre chaves: { nome : string [1] ... }
def p_corpo_classe(p):
    '''corpo_classe : ABRE_CHAVE membros FECHA_CHAVE
                    | vazio'''
    p[0] = p[2] if len(p) == 4 else []


def p_membros(p):
    '''membros : membros membro
               | vazio'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else []


def p_membro(p):
    'membro : atributo'
    p[0] = p[1]


# =============================================================================
# 3. ATRIBUTOS E CARDINALIDADE
# =============================================================================

# Ex.: nome : string [1] { const }
# A cardinalidade e os meta-atributos do atributo não são usados nas saídas.
def p_atributo(p):
    'atributo : nome DOIS_PONTOS tipo cardinalidade_opc meta_opc'
    p[0] = {'construto': 'atributo', 'nome': p[1], 'tipo': p[3], 'linha': p.lineno(1)}


def p_tipo(p):
    '''tipo : TIPO_NATIVO
            | nome'''
    p[0] = p[1]


# Guardada como texto ("1", "1..*") porque é mostrada nas relações.
def p_cardinalidade(p):
    '''cardinalidade : ABRE_COL limite FECHA_COL
                     | ABRE_COL limite INTERVALO limite FECHA_COL'''
    p[0] = p[2] if len(p) == 4 else f'{p[2]}..{p[4]}'


def p_limite(p):
    '''limite : INTEIRO
              | ASTERISCO'''
    p[0] = p[1]


def p_cardinalidade_opc(p):
    '''cardinalidade_opc : cardinalidade
                         | vazio'''
    p[0] = p[1]


def p_meta_opc(p):
    '''meta_opc : ABRE_CHAVE lista_meta FECHA_CHAVE
                | vazio'''


def p_lista_meta(p):
    '''lista_meta : lista_meta VIRGULA META_ATRIBUTO
                  | META_ATRIBUTO'''


# =============================================================================
# 4. ENUMS
# =============================================================================

def p_enum_decl(p):
    'enum_decl : ENUM nome ABRE_CHAVE valores_enum FECHA_CHAVE'
    p[0] = {'construto': 'enum', 'nome': p[2], 'linha': p.lineno(1), 'valores': p[4]}


def p_valores_enum(p):
    '''valores_enum : valores_enum VIRGULA nome
                    | nome'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# =============================================================================
# 5. DATATYPES
# =============================================================================

def p_datatype_decl(p):
    'datatype_decl : DATATYPE nome heranca_tipo corpo_datatype'
    p[0] = {
        'construto': 'datatype',
        'nome': p[2],
        'linha': p.lineno(1),
        'pai': p[3], # tipo especializado, ou None
        'atributos': p[4],
    }


# Ex.: datatype int specializes number
def p_heranca_tipo(p):
    '''heranca_tipo : SPECIALIZES tipo
                    | vazio'''
    p[0] = p[2] if len(p) == 3 else None


# Ao contrário da classe, o corpo de um datatype só tem atributos.
def p_corpo_datatype(p):
    '''corpo_datatype : ABRE_CHAVE atributos FECHA_CHAVE
                      | vazio'''
    p[0] = p[2] if len(p) == 4 else []


def p_atributos(p):
    '''atributos : atributos atributo
                 | vazio'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else []


# =============================================================================
# NOMES E REGRA VAZIA
# =============================================================================
# Qualquer tipo de nome é aceito onde a gramática espera um nome.

def p_nome(p):
    '''nome : NOME_CLASSE
            | NOME_RELACAO
            | NOME_INSTANCIA
            | NOVO_TIPO'''
    p[0] = p[1]


def p_vazio(p):
    'vazio :'


# =============================================================================
# ERRO SINTÁTICO
# =============================================================================

def p_error(t):
    if t is None:
        ERROS_SINTATICOS.append({'linha': 'fim', 'mensagem': 'o arquivo terminou antes da hora'})
    else:
        ERROS_SINTATICOS.append({'linha': t.lineno,
                                 'mensagem': f"'{t.value}' nao era esperado aqui"})


# =============================================================================
# CONSTRUÇÃO E USO
# =============================================================================
# debug=True gera o parser.out, com a gramática e os conflitos.
parser = yacc.yacc(debug=True)


def analisar(texto):
    # Cada arquivo usa um léxico novo, começando na linha 1.
    return parser.parse(texto, lexer=lexer.construir(), tracking=True)

