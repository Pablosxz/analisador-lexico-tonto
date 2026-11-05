import erros
import tabela_simbolos

# Nome interno do token -> rotulo em portugues, na ordem em que aparecem na
# tabela de sintese.
from especificacao import CATEGORIAS


def mostrar_visao_analitica(tokens):
    print('VISAO ANALITICA LÉXICA')
    print(f"{'LINHA':>6} {'COL':>5}  {'TOKEN':<16} LEXEMA")
    for linha, coluna, tipo, lexema in tokens:
        print(f"{linha:>6} {coluna:>5}  {tipo:<16} {lexema}")

# =============================================================================
# RELATÓRIO DA ANÁLISE SINTÁTICA
# =============================================================================

def mostrar_sintese_sintatica(pacotes):
    """
    Exibe a tabela de síntese estrutural exigida nos requisitos do sintático.
    Lê a lista de pacotes gerada pelo parser.py.
    """
    if not pacotes:
        print("\n[!] Nenhuma ontologia válida para resumir devido a erros críticos de sintaxe.")
        return

    print("=" * 70)
    print(" " * 15 + "RESUMO DA ONTOLOGIA (SÍNTESE SINTÁTICA)")
    print("=" * 70)

    # 1. Pacotes e o que cada um importa
    print(f"\nPACOTES ENCONTRADOS: {len(pacotes)}")
    for pacote in pacotes:
        importa = ', '.join(i['nome'] for i in pacote.get('imports', [])) or 'nenhum'
        print(f"  - Pacote: {pacote.get('nome', 'Sem_Nome')} (importa: {importa})")

    for pacote in pacotes:
        mostrar_pacote(pacote)

    print("=" * 70)


def mostrar_pacote(pacote):
    nome_pacote = pacote.get('nome', 'Sem_Nome')
    print("-" * 70)
    print(f"PACOTE {nome_pacote}")

    declaracoes = pacote.get('declaracoes', [])
    
    # Filtrando as declarações por tipo de construto
    classes = [d for d in declaracoes if d.get('construto') == 'classe']
    relacoes_externas = [d for d in declaracoes if d.get('construto') == 'relacao']
    enums = [d for d in declaracoes if d.get('construto') == 'enum']
    datatypes = [d for d in declaracoes if d.get('construto') == 'datatype']
    gensets = [d for d in declaracoes if d.get('construto') == 'genset']

    # 2. Classes e Relações Internas
    print(f"\nCLASSES NO PACOTE '{nome_pacote}' ({len(classes)} encontradas):")
    for c in classes:
        est = c.get('estereotipo', 'sem_estereotipo')
        nome = c.get('nome', 'Sem_Nome')
        print(f"  - [{est}] {nome}")
        
        # Busca por relações declaradas internamente no corpo da classe
        relacoes_internas = c.get('relacoes', [])
        if relacoes_internas:
            print(f"      > Relações Internas da Classe ({len(relacoes_internas)}):")
            for r in relacoes_internas:
                nome_rel = r.get('nome') or '<relação_sem_nome>'
                destino = r.get('destino', '')
                print(f"        * Conecta com: {destino} (Nome da Relação: {nome_rel})")

    # 3. Relações Externas
    print(f"\nRELAÇÕES EXTERNAS ({len(relacoes_externas)} encontradas):")
    if not relacoes_externas:
        print("  - Nenhuma")
    for r in relacoes_externas:
        origem = r.get('origem', '')
        nome_rel = r.get('nome') or '<relação_sem_nome>'
        destino = r.get('destino', '')
        print(f"  - Origem: {origem}  --({nome_rel})-->  Destino: {destino}")

    # 4. Tipos e Agrupamentos (Enums, Datatypes, Gensets)
    tipos_total = len(enums) + len(datatypes) + len(gensets)
    print(f"\nDECLARAÇÕES DE TIPOS E GENSETS ({tipos_total} encontradas):")
    if tipos_total == 0:
        print("  - Nenhuma")
    for e in enums:
        print(f"  - [enum] {e.get('nome')}")
    for d in datatypes:
        print(f"  - [datatype] {d.get('nome')}")
    for g in gensets:
        print(f"  - [genset] {g.get('nome')}")


def mostrar_erros_sintaticos(erros_lista):
    """
    Exibe o relatório de erros com sugestões, conforme exigido pelo professor.
    """
    if not erros_lista:
        print("\nNenhum erro encontrado.")
        return

    print(f"\nERROS SINTÁTICOS ENCONTRADOS ({len(erros_lista)}):")
    for erro in erros_lista:
        linha = erro.get('linha', '?')
        msg = erro.get('mensagem', '')
        sugestao = erro.get('sugestao', '')
        print(f"  [Linha {linha}] {msg}")
        print(f"      -> Sugestão de tratamento: {sugestao}")


def mostrar_tabela_sintese():
    print('TABELA DE SINTESE')
    print(f"{'CATEGORIA':<28} {'DISTINTOS':>9}  {'OCORRENCIAS':>11}")
    for token, rotulo in CATEGORIAS.items():
        print(f"{rotulo:<28} {tabela_simbolos.distintos(token):>9}  "
              f"{tabela_simbolos.ocorrencias(token):>11}")


def mostrar_exportacao(caminho):
    print(f'Tabela de simbolos exportada para {caminho}')


def mostrar_erros():
    if not erros.ERROS:
        return

    print(f'ERROS LEXICOS ({len(erros.ERROS)})')
    for erro in erros.ERROS:
        print(f"  Erro lexico: simbolo nao reconhecido '{erro['lexema']}' "
              f"na linha {erro['linha']}, coluna {erro['coluna']}")
