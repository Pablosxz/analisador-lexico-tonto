# analisador-lexico-tonto

Analisador léxico para a **Textual Ontology Language (TONTO)**, desenvolvido para a
disciplina de Compiladores da Universidade Federal Rural do Semi-Árido (UFERSA), 
sob orientação do professor Patrício de Alencar Silva.

O analisador lê um arquivo `.tonto`, reconhece os elementos da linguagem e produz
duas visualizações: a relação analítica de todos os tokens, com linha e coluna de
ocorrência, e uma tabela de síntese com as quantidades por categoria. Erros léxicos
são reportados com a localização exata e uma sugestão de correção compatível com a
especificação da linguagem.

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
* [Sobre a implementação](#sobre-a-implementação)
  * [De expressão regular a analisador](#de-expressão-regular-a-analisador)
  * [Ordem das regras](#ordem-das-regras)
  * [Sobre o NOVO_TIPO](#sobre-o-novo_tipo)
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
| PLY (Python Lex-Yacc) | 3.11 | geração do analisador léxico a partir de expressões regulares |

O PLY é a implementação em Python da ferramenta LEX. A partir das expressões
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
python src/main.py exemplos/validos/University.tonto
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
│   ├── erros.py                 Detecção de erro e sugestão de correção
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
| `RESERVADA` | palavra reservada | `package`, `import`, `genset` |
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

### Convenções de nomes

As quatro convenções de nome são reconhecidas pelas seguintes expressões regulares:

| Elemento | Expressão regular | Descrição |
| --- | --- | --- |
| Nome de classe | `[A-Z][A-Za-z]*([_-][A-Za-z]+)*_?` | inicia com maiúscula, sem números |
| Nome de relação | `[a-z][A-Za-z]*([_-][A-Za-z]+)*_?` | inicia com minúscula, sem números |
| Nome de instância | `[A-Za-z][A-Za-z]*([_-][A-Za-z]+)*[0-9]+` | inicia com letra e termina com inteiro |
| Novo tipo de dado | nome de classe terminado em `DataType`, sem separadores | `CPFDataType`, `PhoneNumberDataType` |

### Visão analítica

A primeira visualização relaciona todos os tokens encontrados, com a linha e a
coluna de sua localização no código-fonte:

```
VISAO ANALITICA
 LINHA   COL  TOKEN            LEXEMA
     1     1  RESERVADA        package
     1     9  NOME_CLASSE      University
     3     1  EST_CLASSE       category
     3    10  NOME_CLASSE      Organization
     4     1  EST_CLASSE       kind
     4     6  NOME_CLASSE      University
     4    17  RESERVADA        specializes
     6     3  ARROBA           @
     6     4  EST_RELACAO      componentOf
     7     7  AGREG_ESQ        <>--
     7    20  INTEIRO          1
     7    21  INTERVALO        ..
     7    23  ASTERISCO        *
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
CATEGORIA                   DISTINTOS  OCORRENCIAS
Estereotipos de classe              3            4
Estereotipos de relacao             2            2
Palavras reservadas                10           10
Tipos nativos                       1            1
Meta-atributos                      1            1
Classes                            14           16
Relacoes                            4            4
Instancias                          2            2
Novos tipos de dado                 1            1
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
      {"linha": 3, "coluna": 1},
      {"linha": 4, "coluna": 1}
    ]
  }
]
```

O arquivo é reconstruído a cada execução (`tabela_simbolos.serializar()`), e serve
como saída estruturada para uso por outra ferramenta, como uma fase futura de
análise sintática.

### Tratamento de erros léxicos

Quando um caractere não pertence a nenhum padrão da linguagem, o analisador
registra o erro e prossegue a partir do caractere seguinte, de modo que uma única
execução reporta todos os problemas do arquivo.

Como o analisador recebe apenas o caractere que falhou, e não o lexema completo, o
módulo de erros reconstrói a palavra em torno da posição do erro antes de formular
a sugestão. Em `Pessoa__Fisica`, por exemplo, o caractere reportado seria apenas o
segundo sublinhado, uma vez que `Pessoa_` já teria sido reconhecido como nome de
classe. Sem essa reconstrução, a mensagem falaria de um sublinhado solto, sem
indicar em que nome ele ocorre.

Os casos tratados são:

| Entrada | Sugestão apresentada |
| --- | --- |
| `_Pessoa` | nome não pode começar com sublinhado |
| `Pessoa__Fisica` | sublinhado duplo não é permitido |
| `[1.*]` | ponto isolado não é token; a linguagem usa `..` em cardinalidade |
| `<>-` | operador de relação incompleto |
| `Person;` | a linguagem não utiliza ponto e vírgula |
| `name = string` | não existe atribuição; o tipo de um atributo é dado por `:` |
| `Órgão` | nomes aceitam apenas letras sem acento |
| `a--b` como nome | o hífen em um nome deve vir entre letras |

Exemplo de saída:

```
ERROS LEXICOS (1)
  linha 4, coluna 12: '_' em 'Pessoa__Fisica'
     sugestao: sublinhado duplo nao e permitido; use um unico sublinhado
     entre letras
```

Um erro léxico não interrompe a análise: o analisador registra a ocorrência,
avança um caractere e continua, de modo que uma única execução reporta todos os
problemas do arquivo. Ao final, o programa encerra com código de saída `1`.

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

Por esse motivo, a ordem de declaração das regras neste projeto foi definida explicitamente:

```
NOME_INSTANCIA  ->  NOME_CLASSE  ->  NOME_RELACAO
```

Sem essa ordem, `Planeta1` seria reconhecido como o nome de classe `Planeta`
seguido do inteiro `1`. O mesmo cuidado se aplica aos operadores de relação, em que
`<o>--`, `<>--` e `--<>` precisam ser testados antes de `--`.

### Sobre o NOVO_TIPO

A categoria `NOVO_TIPO` não possui regra própria. Todo lexema terminado em
`DataType` é também um nome de classe válido, de modo que os dois padrões não são
mutuamente exclusivos: a linguagem reconhecida por `NOVO_TIPO` está contida na
linguagem reconhecida por `NOME_CLASSE`.

Uma regra separada falharia nas duas posições possíveis. Declarada antes de
`NOME_CLASSE`, consumiria apenas o prefixo de nomes mais longos, dividindo
`MyDataTypeThing` em `MyDataType` e `Thing`. Declarada depois, nunca seria
alcançada. A categoria é, portanto, decidida após o reconhecimento do lexema
completo, do mesmo modo como as palavras reservadas são distinguidas dos nomes de
relação por consulta a uma tabela.

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
