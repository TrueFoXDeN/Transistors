import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import pprint

pp = pprint.PrettyPrinter(indent=4)

from dataclasses import dataclass
from enum import Enum

graph = {}


class KnotenTyp(Enum):
    PMOS = 0
    NMOS = 1
    VDD = 2
    GND = 3
    OUTPUT = 4


@dataclass
class Knoten:
    name: str
    knoten_typ: KnotenTyp
    gate: str = ''

    def __hash__(self):
        return hash(self.name + str(self.knoten_typ) + self.gate)


# Für jeden Knoten

def add_edge(knoten1: Knoten, knoten2: Knoten):
    # if knoten1 not in graph:
    #     graph[knoten1] = []
    # if knoten2 not in graph:
    #     graph[knoten2] = []

    graph[knoten1].append(knoten2)


def add_knoten_to_graph(knoten: Knoten):
    graph[knoten] = []


def iterative_dfs(start_node):
    visited = set()
    outputs = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            if node.knoten_typ == KnotenTyp.PMOS and not inputs[node.gate]:
                stack.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
            elif node.knoten_typ == KnotenTyp.NMOS and inputs[node.gate]:
                stack.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
            elif node.knoten_typ == KnotenTyp.OUTPUT:
                outputs.add(node)
            elif node.knoten_typ == KnotenTyp.VDD:
                stack.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
    return visited, outputs


if __name__ == '__main__':
    inputs = {'A': False, 'B': True, 'C': True}
    vdd = Knoten('VDD', KnotenTyp.VDD)
    #NAND 1
    t1 = Knoten('T1', KnotenTyp.PMOS, gate='A')
    t2 = Knoten('T2', KnotenTyp.PMOS, gate='B')
    t3 = Knoten('T3', KnotenTyp.NMOS, gate='A')
    t4 = Knoten('T4', KnotenTyp.NMOS, gate='B')
    #NAND 2
    t5 = Knoten('T5', KnotenTyp.PMOS, gate='A')
    t6 = Knoten('T6', KnotenTyp.PMOS, gate='C')
    t7 = Knoten('T7', KnotenTyp.NMOS, gate='A')
    t8 = Knoten('T8', KnotenTyp.NMOS, gate='C')

    out1 = Knoten('OUT1', KnotenTyp.OUTPUT)
    out2 = Knoten('OUT2', KnotenTyp.OUTPUT)
    gnd = Knoten('GND', KnotenTyp.GND)

    add_knoten_to_graph(vdd)
    add_knoten_to_graph(t1)
    add_knoten_to_graph(t2)
    add_knoten_to_graph(t3)
    add_knoten_to_graph(t4)
    add_knoten_to_graph(t5)
    add_knoten_to_graph(t6)
    add_knoten_to_graph(t7)
    add_knoten_to_graph(t8)
    add_knoten_to_graph(out1)
    add_knoten_to_graph(gnd)

    add_edge(vdd, t1)
    add_edge(vdd, t2)
    add_edge(t1, t3)
    add_edge(t2, t3)
    add_edge(t1, out1)
    add_edge(t2, out1)
    add_edge(t3, t4)
    add_edge(vdd, t5)
    add_edge(vdd, t6)
    add_edge(t5, t7)
    add_edge(t6, t7)
    add_edge(t7, t8)
    add_edge(t8, gnd)
    add_edge(t5, out2)
    add_edge(t6, out2)

    add_edge(t4, gnd)

    visited, outputs = iterative_dfs(vdd)
    print(outputs)

    G = nx.MultiDiGraph()

    # Füge Knoten und Kanten aus der Adjazenzliste hinzu
    for knoten, nachbarn in graph.items():
        for nachbar in nachbarn:
            G.add_edge(knoten.name, nachbar.name)

    pos = graphviz_layout(G, prog='dot')

    # Bestimme die Farben und Formen der Knoten basierend auf dem Gate-Wert
    node_colors = {}
    node_shapes = {}
    node_labels = {}
    for node in G.nodes():
        for knoten in graph.keys():
            if knoten.name == node:
                if knoten.knoten_typ in [KnotenTyp.PMOS, KnotenTyp.NMOS]:
                    color = 'green' if inputs[knoten.gate] else 'red'
                    shape = '8' if knoten.knoten_typ == KnotenTyp.PMOS else 'o'
                else:
                    color = 'skyblue'
                    shape = 'o'
                node_colors[node] = color
                node_shapes[node] = shape
                node_labels[node] = knoten.gate
                break

    edge_colors = []
    for edge in G.edges():
        start_node, end_node = edge
        if start_node == 'VDD':
            edge_colors.append('green')
        else:
            for knoten in graph.keys():
                if knoten.name == start_node:
                    if ((knoten.knoten_typ == KnotenTyp.PMOS and not inputs[knoten.gate]) or
                            (knoten.knoten_typ == KnotenTyp.NMOS and inputs[knoten.gate])):
                        edge_colors.append('green')
                    else:
                        edge_colors.append('gray')
                    break

    fig, ax = plt.subplots()

    # Zeichne die Knoten und Kanten basierend auf ihren Eigenschaften
    for shape in set(node_shapes.values()):
        nodes_with_shape = [node for node, s in node_shapes.items() if s == shape]
        colors = [node_colors[node] for node in nodes_with_shape]
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=nodes_with_shape,
                               node_color=colors, node_shape=shape, alpha=0.4, node_size=500)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, arrows=True)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_color='black')

    # Füge die Input-Labels hinzu
    input_pos = {node: (x - 4, y - 1) for (node, (x, y)) in
                 pos.items()}  # Positioniere die Labels leicht unterhalb der Knoten
    nx.draw_networkx_labels(G, input_pos, labels=node_labels, ax=ax, font_size=11, font_color='blue')

    plt.box(False)
    plt.show()
