# Vocabulario da linguagem TONTO.
# Acrescentar ou remover uma palavra se resolve aqui, sem mexer nas expressoes
# regulares: o lexer.py consulta RESERVADAS depois de casar o lexema.

# Estereotipos de classe
_EST_CLASSE = """
    event situation process category mixin phaseMixin roleMixin historicalRoleMixin
    kind collective quantity quality mode intrinsicMode extrinsicMode subkind phase
    role historicalRole relator
""".split()

# Estereotipos de relacao
_EST_RELACAO = """
    material derivation comparative mediation characterization externalDependence
    componentOf memberOf subCollectionOf subQualityOf instantiation termination
    participational participation historicalDependence creation manifestation
    bringsAbout triggers composition aggregation inherence value formal constitution
""".split()

# Palavras reservadas
_RESERVADA = """
    genset disjoint complete general specifics where package import
    functional-complexes specializes of relation enum relators intrinsic-modes extrinsic-modes
""".split()

# Tipos de dado nativos
_TIPO_NATIVO = "number string boolean date time datetime".split()

# Meta-atributos
_META_ATRIBUTO = "ordered const derived subsets redefines".split()

# Lexema -> nome do token. Em lexer.py:65 o default e 'NOME_RELACAO': se a
# palavra nao esta aqui, e um nome escrito pelo usuario.

RESERVADAS = {}

for _palavra in _EST_CLASSE:
    RESERVADAS[_palavra] = 'EST_CLASSE'
for _palavra in _EST_RELACAO:
    RESERVADAS[_palavra] = 'EST_RELACAO'
for _palavra in _RESERVADA:
    RESERVADAS[_palavra] = 'RESERVADA'
for _palavra in _TIPO_NATIVO:
    RESERVADAS[_palavra] = 'TIPO_NATIVO'
for _palavra in _META_ATRIBUTO:
    RESERVADAS[_palavra] = 'META_ATRIBUTO'

# Nome do token -> rotulo exibido na tabela de sintese
CATEGORIAS = {
    'EST_CLASSE':     'Estereotipos de classe',
    'EST_RELACAO':    'Estereotipos de relacao',
    'RESERVADA':      'Palavras reservadas',
    'TIPO_NATIVO':    'Tipos nativos',
    'META_ATRIBUTO':  'Meta-atributos',
    'NOME_CLASSE':    'Classes',
    'NOME_RELACAO':   'Relacoes',
    'NOME_INSTANCIA': 'Instancias',
    'NOVO_TIPO':      'Novos tipos de dado',
}
