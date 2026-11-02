# analisador-lexico-tonto

Analisador léxico para a **Textual Ontology Language (TONTO)**, desenvolvido para a
disciplina de Compiladores da Universidade Federal Rural do Semi-Árido (UFERSA), 
sob orientação do professor Patrício de Alencar Silva.

O analisador lê um arquivo `.tonto`, reconhece os elementos da linguagem e produz
duas visualizações: a relação analítica de todos os tokens, com linha e coluna de
ocorrência, e uma tabela de síntese com as quantidades por categoria. Erros léxicos
são reportados com a localização exata, sem interromper a análise. A tabela de
símbolos completa é ainda gravada em JSON, para uso por outra ferramenta.

## Sumário

* [Objetivos](#objetivos)
* [Tecnologias utilizadas](#tecnologias-utilizadas)
* [Tutorial de execução](#tutorial-de-execução)
  * [Instalação das dependências](#instalação-das-dependências)
  * [Execução](#execução)
* [Estrutura do projeto](#estrutura-do-projeto)
* [Análise léxica](#análise-léxica)
  * [Tokens reconhecidos](#tokens-reconhecidos)
  * [Convenções de nomes](#convenções-de-nomes)
  * [Visão analítica](#visão-analítica)
  * [Tabela de síntese](#tabela-de-síntese)
  * [Tabela de símbolos em JSON](#tabela-de-símbolos-em-json)
  * [Tratamento de erros léxicos](#tratamento-de-erros-léxicos)
* [Análise sintática](#análise-sintática)
  * [Construções reconhecidas](#construções-reconhecidas)
  * [Decisões de projeto](#decisões-de-projeto)
  * [Conflito shift/reduce](#conflito-shiftreduce)
  * [Tratamento de erros sintáticos](#tratamento-de-erros-sintáticos)
* [Sobre a implementação](#sobre-a-implementação)
  * [De expressão regular a analisador](#de-expressão-regular-a-analisador)
  * [Ordem das regras](#ordem-das-regras)
  * [Por que uma regra só para nomes](#por-que-uma-regra-só-para-nomes)
* [Autores](#autores)
* [Referências](#referências)

## Objetivos

O projeto tem como objetivo dar suporte à análise de corretude de uma ontologia
especificada textualmente com a linguagem TONTO, reconhecendo:

* estereótipos de classe, como `kind`, `role`, `phase` e `category`;
* estereótipos de relação, como `componentOf`, `mediation` e `material`;
* palavras reservadas da linguagem, como `package`, `import` e `genset`;
* símbolos especiais, incluindo os operadores de relação `<>--`, `--<>` e `<o>--`;
* nomes de classe, de relação e de instância, segundo as convenções da linguagem;
* tipos de dados nativos e novos tipos definidos pelo usuário;
* meta-atributos, como `ordered`, `const` e `derived`.

## Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
| --- | --- | --- |
| Python | 3.10 ou superior | linguagem de implementação |
| PLY (Python Lex-Yacc) | 3.11 | geração dos analisadores léxico (lex) e sintático (yacc) |

O PLY é a implementação em Python das ferramentas LEX e YACC. A partir das expressões
regulares declaradas no projeto, ele constrói o autômato finito que reconhece os
tokens da linguagem.

## Tutorial de execução

### Instalação das dependências

Clonar o repositório e entrar no diretório do projeto:

```bash
git clone https://github.com/Pablosxz/analisador-lexico-tonto.git
cd analisador-lexico-tonto
```

Criar e ativar um ambiente virtual:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux e macOS
python3 -m venv venv
source venv/bin/activate
```

Instalar as dependências:

```bash
pip install -r requirements.txt
```

### Execução

O programa recebe como argumento o caminho do arquivo a ser analisado:

```bash
python src/main.py exemplos/validos/Hospital.tonto
```

O programa termina com código de saída `0` quando nenhum erro léxico é encontrado,
`1` quando há erros léxicos e `2` em caso de erro de uso, como arquivo inexistente.

## Estrutura do projeto

```
analisador-lexico-tonto/
├── exemplos/
│   ├── validos/                 Arquivos .tonto corretos
│   └── invalidos/               Arquivos .tonto com erros propositais
├── src/
│   ├── especificacao.py         Palavras da linguagem e categorias de token
│   ├── lexer.py                 Regras léxicas, linha e coluna
│   ├── erros.py                 Registro dos erros léxicos encontrados
│   ├── tabela_simbolos.py       Registro dos nomes encontrados
│   ├── relatorio.py             Impressão das saídas
│   └── main.py                  Programa principal
├── saida/                       tabela_simbolos.json (gerado a cada execução)
├── requirements.txt
└── README.md
```

Cada módulo tem uma responsabilidade única. O `lexer.py` reconhece, o `erros.py`
acumula, a `tabela_simbolos.py` registra, o `relatorio.py` imprime e o `main.py`
orquestra. Nenhum módulo imprime fora do `relatorio.py`, e nenhum lê ou escreve
arquivo fora do `main.py`.

## Análise léxica

### Tokens reconhecidos

| Token | Descrição | Exemplo |
| --- | --- | --- |
| `EST_CLASSE` | estereótipo de classe | `kind`, `role`, `phase` |
| `EST_RELACAO` | estereótipo de relação | `componentOf`, `mediation` |
| `PACKAGE`, `IMPORT`, `GENSET`... | palavra reservada, um token para cada | `package`, `import`, `datatype` |
| `NATUREZA` | natureza ontológica, usada após `of` | `functional-complexes`, `relators` |
| `TIPO_NATIVO` | tipo de dado nativo | `string`, `number`, `date` |
| `META_ATRIBUTO` | meta-atributo de atributo | `ordered`, `const` |
| `NOME_CLASSE` | nome de classe | `Person`, `Second_Baptist_Church` |
| `NOME_RELACAO` | nome de relação | `hasParent`, `is_part_of` |
| `NOME_INSTANCIA` | nome de instância | `Planeta1`, `pizza03` |
| `NOVO_TIPO` | novo tipo de dado | `CPFDataType` |
| `INTEIRO` | inteiro de cardinalidade | `1`, `2` |
| `ABRE_CHAVE` `FECHA_CHAVE` | delimitadores de bloco | `{` `}` |
| `ABRE_PAR` `FECHA_PAR` | parênteses | `(` `)` |
| `ABRE_COL` `FECHA_COL` | colchetes de cardinalidade | `[` `]` |
| `INTERVALO` | intervalo de cardinalidade | `..` |
| `AGREG_ESQ` `AGREG_DIR` | agregação | `<>--` `--<>` |
| `COMPOSICAO` | composição | `<o>--` |
| `CONECTOR` | conector de relação comum | `--` |
| `ASTERISCO` | cardinalidade ilimitada | `*` |
| `ARROBA` | prefixo de estereótipo de relação | `@` |
| `DOIS_PONTOS` | tipo de atributo | `:` |
| `VIRGULA` | separador de itens | `,` |

Cada palavra reservada tem um token próprio porque o analisador sintático precisa
diferenciá-las: `package` e `genset`, por exemplo, iniciam construções diferentes.

### Convenções de nomes

Todo nome é reconhecido por uma única expressão regular,
`[A-Za-z][A-Za-z0-9]*([_-][A-Za-z0-9]+)*_?`, e a categoria é decidida depois pela
função `classificar_nome`, nesta ordem:

| Condição | Token | Exemplo |
| --- | --- | --- |
| é uma palavra da linguagem | token da palavra | `kind`, `package` |
| só letras e termina em `DataType` | `NOVO_TIPO` | `CPFDataType` |
| termina em número | `NOME_INSTANCIA` | `Planeta1`, `pizza03` |
| começa com maiúscula | `NOME_CLASSE` | `Person`, `Second_Baptist_Church` |
| começa com minúscula | `NOME_RELACAO` | `hasParent`, `is_part_of` |

### Visão analítica

A primeira visualização relaciona todos os tokens encontrados, com a linha e a
coluna de sua localização no código-fonte:

```
VISAO ANALITICA
 LINHA   COL  TOKEN            LEXEMA
     1     1  RESERVADA        package
     1     9  NOME_CLASSE      Hospital
     3     1  EST_CLASSE       kind
     3     6  NOME_CLASSE      Unidade_Basica_De_Saude
     4     1  EST_CLASSE       kind
     4     6  NOME_CLASSE      Pessoa
     4    13  ABRE_CHAVE       {
     5     5  NOME_RELACAO     nome
     5    10  DOIS_PONTOS      :
     5    12  TIPO_NATIVO      string
     5    19  ABRE_COL         [
     5    20  INTEIRO          1
```

A coluna é calculada a partir da posição absoluta do lexema no arquivo, medindo a
distância até a última quebra de linha anterior. Esse cálculo não depende de nenhum
contador acumulado, de modo que a coluna permanece correta mesmo após a recuperação
de um erro léxico.

### Tabela de síntese

A segunda visualização apresenta as quantidades por categoria, distinguindo o
número de nomes distintos do número total de ocorrências:

```
TABELA DE SINTESE
CATEGORIA                    DISTINTOS  OCORRENCIAS
Estereotipos de classe               4           15
Estereotipos de relacao              2           15
Palavras reservadas                  9           30
Tipos nativos                        3            6
Meta-atributos                       0            0
Classes                             23           63
Relacoes                            17           17
Instancias                          23           23
Novos tipos de dado                  0            0
```

As contagens são obtidas da tabela de símbolos, que registra cada lexema junto de
sua categoria e da lista de todas as suas ocorrências no arquivo.

### Tabela de símbolos em JSON

Além das duas visualizações impressas no terminal, cada execução grava a tabela de
símbolos completa em `saida/tabela_simbolos.json`, agrupada por lexema:

```json
[
  {
    "lexema": "kind",
    "categoria": "EST_CLASSE",
    "ocorrencias": [
      { "linha": 3, "coluna": 1 },
      { "linha": 4, "coluna": 1 },
      { "linha": 10, "coluna": 1 }
    ]
  }
]
```

O arquivo é reconstruído a cada execução: `tabela_simbolos.serializar()` converte o
dicionário interno em uma estrutura serializável e o `main.py` a grava em disco.
Serve como saída estruturada para uso por outra ferramenta, como uma fase futura de
análise sintática, que precisaria justamente da lista de tokens com suas posições.

Para o arquivo `Hospital.tonto`, o JSON gerado contém 81 lexemas distintos.

### Tratamento de erros léxicos

Um erro léxico ocorre quando um caractere da entrada não pertence a nenhum padrão
da linguagem. Nesse caso o analisador **não interrompe a análise**: registra a
ocorrência com sua posição exata, avança um caractere e prossegue. Uma única
execução reporta, portanto, todos os problemas do arquivo, e não apenas o primeiro.

A recuperação é feita pela regra `t_error` do `lexer.py`, que calcula a coluna e
delega o registro ao módulo `erros.py`. Este acumula as ocorrências em uma lista,
sem imprimir nada: a exibição fica a cargo do `relatorio.py`, ao final da análise.

Exemplo de saída para um arquivo com quatro construções inválidas:

```
ERROS LEXICOS (5)
  Erro lexico: simbolo nao reconhecido '_' na linha 2, coluna 6
  Erro lexico: simbolo nao reconhecido ';' na linha 3, coluna 12
  Erro lexico: simbolo nao reconhecido '=' na linha 4, coluna 6
  Erro lexico: simbolo nao reconhecido 'Ó' na linha 5, coluna 6
  Erro lexico: simbolo nao reconhecido 'ã' na linha 5, coluna 9
```

O último caso ilustra o comportamento da recuperação: o nome `Órgão` produz duas
ocorrências, uma para cada letra acentuada, porque o analisador retoma a leitura
no caractere seguinte a cada falha.

Havendo ao menos um erro léxico, o programa encerra com código de saída `1`.

## Análise sintática

O analisador sintático (`src/parser.py`) é gerado pelo módulo `yacc` do PLY, que
constrói um analisador ascendente LALR(1), o mesmo método do Bison. Cada regra da
gramática é uma função `p_...`: a regra fica na docstring e o corpo é executado
quando o PLY reduz aquela regra. O resultado da análise de um arquivo é um
dicionário com o pacote e suas declarações, usado pela tabela de símbolos e pelas
saídas.

### Construções reconhecidas

| Construção | Exemplo |
| --- | --- |
| Pacote e importação | `import Pessoa` e `package Hospital` |
| Classe | `role Medico specializes Pessoa { especialidade : Especialidade }` |
| Classe enumerada | `enum Especialidade { Pediatra01, Dentista02 }` |
| Tipo de dado complexo | `datatype Telefone { ddd : number  numero : string }` |
| Relação interna (dentro da classe) | `@mediation [1..*] -- [1] Paciente` |
| Relação externa | `@material relation Paciente [1..*] -- consulta -- [1..*] Medico` |
| Conjunto de generalização | `disjoint complete genset Fases { general Pessoa specifics Crianca, Adulto }` |

<details>
<summary>Gramática completa</summary>

```
ontologia         → lista_imports PACKAGE nome conteudo
lista_imports     → lista_imports importacao | vazio
importacao        → IMPORT nome
conteudo          → conteudo elemento | vazio
elemento          → classe | enum_decl | datatype_decl | genset_decl
                  | relacao_externa | error

classe            → EST_CLASSE nome natureza heranca corpo_classe
natureza          → OF lista_naturezas | vazio
lista_naturezas   → lista_naturezas VIRGULA NATUREZA | NATUREZA
heranca           → SPECIALIZES lista_nomes | vazio
lista_nomes       → lista_nomes VIRGULA nome | nome
corpo_classe      → ABRE_CHAVE membros FECHA_CHAVE | vazio
membros           → membros membro | vazio
membro            → atributo | relacao_interna

atributo          → nome DOIS_PONTOS tipo cardinalidade_opc meta_opc
tipo              → TIPO_NATIVO | nome
cardinalidade     → ABRE_COL limite FECHA_COL
                  | ABRE_COL limite INTERVALO limite FECHA_COL
limite            → INTEIRO | ASTERISCO
cardinalidade_opc → cardinalidade | vazio
meta_opc          → ABRE_CHAVE lista_meta FECHA_CHAVE | vazio
lista_meta        → lista_meta VIRGULA META_ATRIBUTO | META_ATRIBUTO

enum_decl         → ENUM nome ABRE_CHAVE valores_enum FECHA_CHAVE
valores_enum      → valores_enum VIRGULA nome | nome

datatype_decl     → DATATYPE nome heranca_tipo corpo_datatype
heranca_tipo      → SPECIALIZES tipo | vazio
corpo_datatype    → ABRE_CHAVE atributos FECHA_CHAVE | vazio
atributos         → atributos atributo | vazio

genset_decl       → restricoes GENSET nome ABRE_CHAVE GENERAL nome
                    SPECIFICS lista_nomes FECHA_CHAVE
restricoes        → DISJOINT COMPLETE | DISJOINT | COMPLETE | vazio

relacao_externa   → estereotipo_rel RELATION nome dados_relacao
relacao_interna   → estereotipo_rel dados_relacao
estereotipo_rel   → ARROBA EST_RELACAO | vazio
dados_relacao     → cardinalidade_opc ligacao cardinalidade nome
ligacao           → tipo_ligacao | CONECTOR nome CONECTOR | AGREG_ESQ nome CONECTOR
tipo_ligacao      → CONECTOR | AGREG_ESQ | AGREG_DIR

nome              → NOME_CLASSE | NOME_RELACAO | NOME_INSTANCIA | NOVO_TIPO
```

</details>

### Decisões de projeto

* **Um pacote por arquivo.** Cada arquivo tem os imports seguidos de um `package`,
  como em todos os exemplos do professor. Uma ontologia com vários pacotes é
  dividida em vários arquivos, analisados juntos.
* **Qualquer nome onde a gramática espera um nome.** Os exemplos do professor nem
  sempre seguem as convenções (a classe `ClassName1`, por exemplo, termina em
  número), então os quatro tipos de nome são aceitos.
* **Reconhecer sem guardar.** Naturezas, cardinalidades, meta-atributos,
  estereótipos e tipos de ligação das relações, restrições do genset e valores de
  enums são reconhecidos para que o arquivo seja aceito, mas não são guardados,
  porque as saídas não os utilizam.

### Conflito shift/reduce

O PLY aponta um conflito: dentro de uma classe, depois de um atributo como
`nome : string`, um `[` pode ser a cardinalidade do atributo ou o início de uma
relação interna sem estereótipo. O PLY resolve pelo *shift*, associando o `[` ao
atributo, que é o comportamento desejado, como no caso do *else* pendente. O
conflito aparece no arquivo `src/parser.out`, gerado junto com o analisador.

Um segundo conflito foi evitado escrevendo as ligações com nome por extenso
(`CONECTOR nome CONECTOR` e `AGREG_ESQ nome CONECTOR`), para que o PLY só decida o
tipo da ligação depois de ler o nome.

### Tratamento de erros sintáticos

Quando nenhuma regra aceita o próximo token, a função `p_error` consulta a tabela do
PLY para saber quais tokens eram esperados naquele ponto e monta uma sugestão. Para
continuar depois do erro, a regra `elemento : error` aplica o modo pânico: o
analisador descarta tokens até o início da próxima declaração e retoma a análise.

Erros encontrados em `exemplos/invalidos/sintaxe_invalida.tonto`:

| Linha | Erro | Sugestão |
| --- | --- | --- |
| 6 | `'string'` não era esperado | confira a escrita desta linha perto de `'string'` |
| 9 | `'kind'` não era esperado | faltou um nome antes de `'kind'` |
| 10 | `'Verde'` não era esperado | esperava `','` ou `'}'` |
| 12 | `'specifics'` não era esperado | faltou `'general'` antes de `'specifics'` |
| fim | o arquivo terminou antes da hora | falta fechar uma `'}'` |

Se o arquivo termina no meio de uma declaração, não há onde retomar: o erro é
registrado e o restante do arquivo não é analisado.

## Sobre a implementação

### De expressão regular a analisador

O projeto não implementa o reconhecedor manualmente. As expressões regulares
declaradas no `lexer.py` são convertidas pelo PLY em um autômato finito, seguindo a
cadeia estudada na disciplina:

1. cada expressão regular é convertida em um autômato finito não determinista
   pelo algoritmo de McNaughton-Yamada-Thompson;
2. o autômato não determinista é convertido em um autômato finito determinista
   pela construção de subconjuntos;
3. o autômato determinista é simulado sobre a cadeia de entrada.

Como a simulação consome cada caractere uma única vez, a análise é linear no
tamanho do arquivo. Todo o custo de construção ocorre antes da leitura do primeiro
caractere.

### Ordem das regras

O material da disciplina descreve a ferramenta LEX, que resolve a ambiguidade entre
duas regras pelo critério do casamento mais longo, característico dos motores de
expressão regular da família POSIX. O PLY delega o casamento ao módulo `re` do
Python, de semântica *leftmost-first*, no qual vence a primeira alternativa que
casa, independentemente do número de caracteres consumidos.

Por isso a ordem de declaração importa nos operadores de relação: `<o>--`, `<>--` e
`--<>` são testados antes de `--`, senão o `--` inicial seria consumido sozinho. Nos
nomes o problema não ocorre, porque uma única regra reconhece a palavra inteira.

### Por que uma regra só para nomes

Com uma regra por categoria de nome, cada uma reconhecia apenas o trecho da palavra
que combinava com ela. No exemplo `TDAH.tonto` do professor, `Criterion_A1a` era
dividido em `Criterion_A1` (instância) e `a` (relação), e o analisador sintático
recebia dois nomes seguidos. Reconhecendo a palavra inteira primeiro e decidindo a
categoria depois, como já era feito com as palavras reservadas, nenhum nome é
cortado.

## Autores

- Pablo Lucas de Souza Ernesto (https://github.com/Pablosxz)
- Clara Leticia Lopes de Oliveira (https://github.com/ClaraLeticia)

## Referências

1. AHO, A. V. et al. *Compiladores: princípios, técnicas e ferramentas*. 2. ed.
   São Paulo: Pearson, 2008.
2. COUTINHO, M. L.; ALMEIDA, J. P. A.; SALES, T. P.; GUIZZARDI, G. A Textual Syntax
   and Toolset for Well-Founded Ontologies. In: *14th International Conference on
   Formal Ontology in Information Systems (FOIS 2024)*, p. 208-222. IOS Press, 2024.
3. GUIZZARDI, G. et al. Endurant Types in Ontology-Driven Conceptual Modeling:
   Towards OntoUML 2.0. In: *International Conference on Conceptual Modeling*,
   p. 136-150. Springer, 2018.
4. LENKE, M. *Tonto: A Textual Syntax for OntoUML*. Disponível em:
   https://matheuslenke.github.io/tonto-docs/
5. BEAZLEY, D. *PLY (Python Lex-Yacc)*. Disponível em:
   https://www.dabeaz.com/ply/
