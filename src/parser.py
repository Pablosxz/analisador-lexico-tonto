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
                | classe'''
    p[0] = p[1]  # repassa o que já foi montado


# =============================================================================
# 2. CLASSES
# =============================================================================

def p_classe(p):
    'classe : EST_CLASSE nome natureza heranca'
    p[0] = {
        'construto': 'classe',
        'estereotipo': p[1], # kind, role, phase...
        'nome': p[2],
        'linha': p.lineno(1),
        'pais': p[4], # classes que ela especializa
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

