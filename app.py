import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

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
    gate: bool = False

    def __hash__(self):
        return hash(self.name + str(self.knoten_typ) + str(self.gate))


# Für jeden Knoten

def add_edge(knoten1: Knoten, knoten2: Knoten):
    if knoten1 not in graph:
        graph[knoten1] = []
    if knoten2 not in graph:
        graph[knoten2] = []

    graph[knoten1].append(knoten2)


if __name__ == '__main__':
    inputs = {'A': True, 'B': False, 'C': True}

    vdd = Knoten('VDD', KnotenTyp.VDD)
    t1 = Knoten('T1', KnotenTyp.PMOS, gate=inputs['A'])
    t2 = Knoten('T2', KnotenTyp.PMOS, gate=inputs['B'])
    t3 = Knoten('T3', KnotenTyp.NMOS, gate=inputs['A'])
    t4 = Knoten('T4', KnotenTyp.NMOS, gate=inputs['B'])
    out = Knoten('Out', KnotenTyp.OUTPUT)
    gnd = Knoten('GND', KnotenTyp.GND)

    add_edge(vdd, t1)
    add_edge(vdd, t2)
    add_edge(t1, t3)
    add_edge(t2, t3)
    add_edge(t1, out)
    add_edge(t2, out)
    add_edge(t3, t4)
    add_edge(t4, gnd)

    G = nx.MultiDiGraph()

    # Füge Knoten und Kanten aus der Adjazenzliste hinzu
    for knoten, nachbarn in graph.items():
        for nachbar in nachbarn:
            G.add_edge(knoten.name, nachbar.name)

    pos = graphviz_layout(G, prog='dot')

    # Bestimme die Farben und Formen der Knoten basierend auf dem Gate-Wert
    node_colors = {}
    node_shapes = {}
    for node in G.nodes():
        for knoten in graph.keys():
            if knoten.name == node:
                if knoten.knoten_typ in [KnotenTyp.PMOS, KnotenTyp.NMOS]:
                    color = 'green' if knoten.gate else 'red'
                    shape = '8' if knoten.knoten_typ == KnotenTyp.PMOS else 'o'
                else:
                    color = 'skyblue'
                    shape = 'o'
                node_colors[node] = color
                node_shapes[node] = shape
                break

    edge_colors = []
    for edge in G.edges():
        start_node, end_node = edge
        if start_node == 'VDD':
            edge_colors.append('green')
        else:
            for knoten in graph.keys():
                if knoten.name == start_node:
                    if ((knoten.knoten_typ == KnotenTyp.PMOS and not knoten.gate) or
                            (knoten.knoten_typ == KnotenTyp.NMOS and knoten.gate)):
                        edge_colors.append('green')
                    else:
                        edge_colors.append('gray')
                    break

    input_labels = {'T1': 'A', 'T2': 'B', 'T3': 'A', 'T4': 'B'}
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
    input_pos = {node: (x-4, y-1) for (node, (x, y)) in pos.items()}  # Positioniere die Labels leicht unterhalb der Knoten
    nx.draw_networkx_labels(G, input_pos, labels=input_labels, ax=ax, font_size=11, font_color='blue')

    plt.show()
