import sys
from rdflib import Graph, RDF, URIRef, Namespace
import networkx as nx
import graphviz # Biblioteca para renderização

# --- Configurações ---
NAMESPACE_URI = "http://example.org/yang#"
NAMESPACE = Namespace(NAMESPACE_URI)
MAX_NODES_TO_DRAW = 50 

def load_and_visualize_graphviz(rdf_file_path):
    """
    Carrega um arquivo RDF (Turtle) e gera um grafo usando Graphviz, abrindo-o em uma janela.
    """
    print(f"**Iniciando visualização com Graphviz: {rdf_file_path}**\n")

    # 1. Carregar o Grafo RDF usando rdflib
    g = Graph()
    try:
        g.parse(rdf_file_path, format="turtle")
        print(f"[SUCESSO] Grafo carregado. Total de triplas: {len(g)}")
    except Exception as e:
        print(f"[ERRO] Não foi possível carregar o arquivo RDF: {e}")
        return

    # 2. Converter Triplas RDF para um Grafo NetworkX (para facilitar o foco)
    G = nx.DiGraph()
    
    for s, p, o in g:
        s_label = str(s)
        p_label = str(p)
        o_label = str(o)

        # Limpeza básica para rótulos curtos (IMPORTANTE para o Graphviz)
        s_display = s_label.replace(NAMESPACE_URI, "yang:")
        p_display = p_label.replace(NAMESPACE_URI, "yang:").split('#')[-1]
        o_display = o_label.replace(NAMESPACE_URI, "yang:")
        
        G.add_edge(s_display, o_display, label=p_display)

    # 3. Focar no módulo principal (Usando a mesma lógica de detecção)
    graph_to_draw = G
    if len(G.nodes) > MAX_NODES_TO_DRAW:
        print(f"[AVISO] Grafo grande ({len(G.nodes)} nós). Focando no módulo principal e vizinhos imediatos.")
        
        module_node_uri = URIRef(NAMESPACE.Module)
        module_node = None
        
        for s, p, o in g.triples((None, RDF.type, module_node_uri)):
            module_node = str(s).replace(NAMESPACE_URI, "yang:")
            break 
            
        if module_node and module_node in G:
            print(f"[INFO] Módulo principal detectado: {module_node}")
            
            nodes_to_draw = set([module_node])
            nodes_to_draw.update(G.successors(module_node))
            nodes_to_draw.update(G.predecessors(module_node))
            
            graph_to_draw = G.subgraph(nodes_to_draw)
        else:
            print("[ERRO LÓGICO] Não foi possível focar no módulo principal.")
            
    
    # 4. Renderizar com Graphviz
    dot = graphviz.Digraph(comment='Grafo de Conhecimento YANG', format='png', engine='dot')
    
    # Configurações gerais do grafo (opcional)
    dot.attr(rankdir='LR') # Layout da esquerda para a direita

    for node in graph_to_draw.nodes():
        # Configura o estilo do nó
        dot.node(node, node, shape='box', style='filled', fillcolor='skyblue', fontname='Helvetica')

    for u, v, data in graph_to_draw.edges(data=True):
        label = data.get('label', '')
        # Limita o tamanho do rótulo da aresta para melhor visualização
        if len(label) > 30:
            label = label[:27] + '...'
            
        dot.edge(u, v, label=label, fontname='Helvetica', color='gray')

    # 5. Visualizar
    # render() salva o arquivo (ex: .png) E tenta abrir a janela (view=True)
    output_filename = rdf_file_path.replace(".rdf", "_kg_visualization")
    
    try:
        # Salva como PNG e tenta abrir no visualizador padrão do sistema
        dot.render(output_filename, view=True, cleanup=True) 
        print(f"\n[SUCESSO] Grafo salvo como {output_filename}.png e janela de visualização aberta (se o Graphviz estiver configurado).")
    except Exception as e:
        # Se a visualização nativa falhar (view=True), pelo menos salva o arquivo
        print(f"\n[AVISO] Falha ao abrir a janela nativa do Graphviz: {e}")
        print(f"[INFO] O arquivo {output_filename}.png foi salvo no diretório de execução.")
        dot.render(output_filename, view=False, cleanup=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python visualize_graphviz.py <arquivo_de_entrada.rdf>")
        sys.exit(1)
    
    input_rdf_file = sys.argv[1]
    load_and_visualize_graphviz(input_rdf_file)