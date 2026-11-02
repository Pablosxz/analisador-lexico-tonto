# parser.py - analisador sintático da linguagem TONTO

import ply.yacc as yacc
import lexer
from lexer import tokens  # o PLY usa a mesma lista de tokens do léxico

# Erros sintáticos encontrados, usados no relatório de erros.
ERROS_SINTATICOS = []


# =============================================================================
# 1. PACOTE E IMPORTS
# =============================================================================
# A primeira regra é o símbolo inicial: o arquivo inteiro, com um pacote.
# Ontologias com vários pacotes ficam em vários arquivos.

def p_ontologia(p):
    'ontologia : lista_imports PACKAGE nome conteudo'
    p[0] = {
        'nome': p[3],
        'linha': p.lineno(2),
        'imports': p[1],
        # Declarações com erro de sintaxe ficam de fora (já estão no relatório).
        'declaracoes': [e for e in p[4] if e['construto'] != 'erro'],
    }


def p_lista_imports(p):
    '''lista_imports : lista_imports importacao
                     | vazio'''
    if len(p) == 3: # lista_imports importacao
        p[0] = p[1] + [p[2]]
    else: # vazio
        p[0] = []


def p_importacao(p):
    'importacao : IMPORT nome'
    p[0] = {'nome': p[2], 'linha': p.lineno(1)}


def p_conteudo(p):
    '''conteudo : conteudo elemento
                | vazio'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_elemento(p):
    '''elemento : classe
                | enum_decl
                | datatype_decl
                | genset_decl
                | relacao_externa'''
    p[0] = p[1]  # repassa o que já foi montado


# Recuperação de erro (modo pânico): quando uma declaração tem erro, o PLY
# descarta tokens até o começo da próxima declaração e continua dali.
def p_elemento_com_erro(p):
    'elemento : error'
    p[0] = {'construto': 'erro'}


# =============================================================================
# 2. CLASSES
# =============================================================================

def p_classe(p):
    'classe : EST_CLASSE nome natureza heranca corpo_classe'
    membros = p[5]
    p[0] = {
        'construto': 'classe',
        'estereotipo': p[1], # kind, role, phase...
        'nome': p[2],
        'linha': p.lineno(1),
        'pais': p[4], # classes que ela especializa
        'atributos': [m for m in membros if m['construto'] == 'atributo'],
        'relacoes': [m for m in membros if m['construto'] == 'relacao'], # relações internas
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
    '''membro : atributo
              | relacao_interna'''
    p[0] = p[1]


# =============================================================================
# 3. ATRIBUTOS E CARDINALIDADE
# =============================================================================

# Ex.: nome : string [1] { const }
# Os meta-atributos (ordered, const...) também não são guardados.
def p_atributo(p):
    'atributo : nome DOIS_PONTOS tipo cardinalidade_opc meta_opc'
    p[0] = {'construto': 'atributo', 'nome': p[1], 'tipo': p[3], 'linha': p.lineno(1)}


def p_tipo(p):
    '''tipo : TIPO_NATIVO
            | nome'''
    p[0] = p[1]


# Ex.: [1] ou [1..*]. Usada em atributos e relações, mas não é guardada.
def p_cardinalidade(p):
    '''cardinalidade : ABRE_COL limite FECHA_COL
                     | ABRE_COL limite INTERVALO limite FECHA_COL'''


def p_limite(p):
    '''limite : INTEIRO
              | ASTERISCO'''


def p_cardinalidade_opc(p):
    '''cardinalidade_opc : cardinalidade
                         | vazio'''


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
    p[0] = {'construto': 'enum', 'nome': p[2], 'linha': p.lineno(1)}


def p_valores_enum(p):
    '''valores_enum : valores_enum VIRGULA nome
                    | nome'''


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
# 6. GENSETS
# =============================================================================

# Ex.: disjoint complete genset Fases { general Pessoa specifics Crianca, Adulto }
def p_genset_decl(p):
    'genset_decl : restricoes GENSET nome ABRE_CHAVE GENERAL nome SPECIFICS lista_nomes FECHA_CHAVE'
    p[0] = {
        'construto': 'genset',
        'nome': p[3],
        'linha': p.lineno(2),
        'geral': p[6],
        'especificos': p[8],
    }


# disjoint e complete são opcionais e não são guardados.
def p_restricoes(p):
    '''restricoes : DISJOINT COMPLETE
                  | DISJOINT
                  | COMPLETE
                  | vazio'''


# =============================================================================
# 7. RELAÇÕES
# =============================================================================
# Interna: fica dentro da classe, que é a origem.
# Externa: fica solta no pacote e diz a origem depois de "relation".

def p_relacao_externa(p):
    'relacao_externa : estereotipo_rel RELATION nome dados_relacao'
    p[0] = dict(p[4], origem=p[3], linha=p.lineno(2))


def p_relacao_interna(p):
    'relacao_interna : estereotipo_rel dados_relacao'
    p[0] = dict(p[2], linha=p.lineno(2))


# O estereótipo (@material, @mediation...) é opcional e não é guardado.
def p_estereotipo_rel(p):
    '''estereotipo_rel : ARROBA EST_RELACAO
                       | vazio'''


# Ex.: [1] <>-- tem -- [1..*] Departamento
def p_dados_relacao(p):
    'dados_relacao : cardinalidade_opc ligacao cardinalidade nome'
    p[0] = {
        'construto': 'relacao',
        'nome': p[2], # nome da relação, ou None
        'destino': p[4],
    }


def p_ligacao_sem_nome(p):
    'ligacao : tipo_ligacao'
    p[0] = None


# As formas com nome ficam por extenso para evitar um conflito shift/reduce:
# assim o PLY só decide o tipo da ligação depois de ver o nome.
def p_ligacao_com_nome(p):
    '''ligacao : CONECTOR nome CONECTOR
               | AGREG_ESQ nome CONECTOR'''
    p[0] = p[2]


# O tipo da ligação (--, <>--, --<>) não é guardado.
def p_tipo_ligacao(p):
    '''tipo_ligacao : CONECTOR
                    | AGREG_ESQ
                    | AGREG_DIR'''


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

# Como cada token aparece na sugestão de correção.
LEGIVEL = {
    'NOME_CLASSE': 'um nome', 'NOME_RELACAO': 'um nome',
    'NOME_INSTANCIA': 'um nome', 'NOVO_TIPO': 'um nome',
    'EST_CLASSE': 'um estereótipo de classe (kind, role...)',
    'EST_RELACAO': 'um estereótipo de relação', 'TIPO_NATIVO': 'um tipo (string, number...)',
    'NATUREZA': 'uma natureza', 'META_ATRIBUTO': 'um meta-atributo', 'INTEIRO': 'um número',
    'ABRE_CHAVE': "'{'", 'FECHA_CHAVE': "'}'", 'ABRE_COL': "'['", 'FECHA_COL': "']'",
    'INTERVALO': "'..'", 'ASTERISCO': "'*'", 'ARROBA': "'@'", 'DOIS_PONTOS': "':'",
    'VIRGULA': "','", 'CONECTOR': "'--'", 'AGREG_ESQ': "'<>--'", 'AGREG_DIR': "'--<>'",
    '$end': 'o fim do arquivo',
}


def p_error(t):
    # Tokens que a tabela do PLY aceitaria neste ponto. Palavras reservadas
    # não estão no LEGIVEL e aparecem como são escritas: PACKAGE -> 'package'.
    estado = parser.statestack[-1]
    esperados = sorted({LEGIVEL.get(tipo, f"'{tipo.lower()}'")
                        for tipo in parser.action[estado] if tipo != 'error'})

    if t is None:
        ERROS_SINTATICOS.append({
            'linha': 'fim',
            'mensagem': 'o arquivo terminou antes da hora',
            'sugestao': "falta fechar uma '}'" if "'}'" in esperados else 'complete a última declaração',
        })
        return

    if len(esperados) == 1:
        sugestao = f"faltou {esperados[0]} antes de '{t.value}'"
    elif len(esperados) <= 4:
        sugestao = 'esperava ' + ', '.join(esperados[:-1]) + ' ou ' + esperados[-1]
    else:
        sugestao = f"confira a escrita desta linha perto de '{t.value}'"

    ERROS_SINTATICOS.append({
        'linha': t.lineno,
        'mensagem': f"'{t.value}' nao era esperado aqui",
        'sugestao': sugestao,
    })


# =============================================================================
# CONSTRUÇÃO E USO
# =============================================================================
# debug=True gera o parser.out, com a gramática e os conflitos.
parser = yacc.yacc(debug=True)


def analisar(texto):
    # Devolve o pacote do arquivo, ou None se um erro impediu a análise
    # (por exemplo, o arquivo termina no meio de uma declaração).
    # Cada arquivo usa um léxico novo, começando na linha 1.
    return parser.parse(texto, lexer=lexer.construir(), tracking=True)

