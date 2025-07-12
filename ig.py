import numpy as np
import seed_tournament
from score_sequences import score_sequences
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import os
import json

#Creates interchange graph for a given score sequence and kind
def interchange_graph(seq, kind, abort=False, abort_threshold=200):
    if kind in ['A','B','D','C']:
        ig_v = [] #Vertices of ig
        ig_e = [] #Edges of ig

        seed = seed_tournament.construct_tournament(seq, kind)
        que = [seed]
        ig_v.append(seed)

        while que != []:
            curr = que.pop()
            gens = generators(curr, kind)

            for gen in gens:
                flipped = reverse(curr, gen)
                ig_e.append([curr,flipped,gen[0]])

                repeat = False
                for tour in ig_v:
                    if np.array_equal(flipped, tour):
                        repeat = True

                if repeat == False:
                    ig_v.append(flipped)
                    que.append(flipped)

            if abort and len(ig_v) > abort_threshold:
                print("Aborting interchange graph creation due to too many vertices.")
                return None

        # Create a mapping from vertices to integers
        vertex_mapping = {str(v.tolist()): i for i, v in enumerate(ig_v)}
        IG = nx.Graph()
        # Add nodes to the graph with their corresponding integer labels
        for v in ig_v:
            IG.add_node(vertex_mapping[str(v.tolist())])
        # Add edges to the graph with their corresponding integer labels
        unique_edges = set()
        for e in ig_e:
            source = vertex_mapping[str(e[0].tolist())]
            target = vertex_mapping[str(e[1].tolist())]
            edge = (source, target)
            edge2 = (target, source)
            if edge not in unique_edges:
              unique_edges.add(edge)
              unique_edges.add(edge2)
              IG.add_edge(*edge, kind=e[2])

        return IG





def generators(tour, kind):
    ### First parameter of elements of return lists indicates kind of gen,
    ### Second is the tuple of vertices
    ### Third is extra description of which gen it is.
    n, _ = tour.shape
    gens = []

    if kind == 'A' or kind == 'D' or kind == 'B' or kind == 'C':
        for i in range(n):
            for j in range(i+1,n):
                for k in range(j+1,n):
                    if tour[i,j] == tour[j,k] == -tour[i,k]:
                        gens.append(('A', (i,j,k), '_'))

    ### Last index in D-gen indicates the vertex between collaborative games
    if kind == 'D' or kind == 'B' or kind == 'C':
        for i in range(n):
            for j in range(i+1,n):
                for k in range(j+1,n):
                    if -tour[j,i] == tour[k,i] == tour[j,k]:
                        gens.append(('D', (i,j,k), i))
                    if -tour[j,i] == tour[i,k] == tour[k,j]:
                        gens.append(('D', (i,j,k), j))
                    if tour[i,j] == -tour[k,i] == tour[k,j]:
                        gens.append(('D', (i,j,k), k))

    ### Third parameter indicates if the game between i,j is comp (A) or coll (D)
    if kind == 'B':
        for i in range(n):
            for j in range(i+1,n):
                if -2*tour[i,i] == 2*tour[j,j] == tour[i,j]:
                    gens.append(('B', (i,j), 'A'))
                if 2*tour[i,i] == 2*tour[j,j] == -tour[j,i]:
                    gens.append(('B', (i,j), 'D'))

    ### In 'C' kind matrix entries on diagonal are twos
    ### Third parameter indicates loop attachment in the gen
    if kind == 'C':
        for i in range(n):
            for j in range(i+1,n):
                if 2*tour[i,i] + tour[i,j] + tour[j,i] == 0:
                    gens.append(('C', (i,j), i))
                if 2*tour[j,j] + tour[j,i] - tour[i,j] == 0:
                    gens.append(('C', (i,j), j))

    return gens


### We use the encoding of gens as in generators()
def reverse(tour, gen):
    rev_tour = tour.copy()
    kind, vertices, extra = gen
    to_be_reversed = []

    if kind == 'A':
        i, j, k = vertices
        to_be_reversed = [(i,j), (i,k), (j,k)]
    elif kind == 'D':
        i, j, k = vertices
        if extra == i:
            to_be_reversed = [(j,i), (k,i), (j,k)]
        elif extra == j:
            to_be_reversed = [(j,i), (i,k), (k,j)]
        elif extra == k:
            to_be_reversed = [(i,j), (k,i), (k,j)]
    elif kind == 'B':
        i, j = vertices
        if extra == 'A':
            to_be_reversed = [(i,i), (j,j), (i,j)]
        elif extra == 'D':
            to_be_reversed = [(i,i), (j,j), (j,i)]
    elif kind == 'C':
        i, j = vertices
        if extra == i:
            to_be_reversed = [(i,j), (j,i), (i,i)]
        elif extra == j:
            to_be_reversed = [(i,j), (j,i), (j,j)]

    for x, y in to_be_reversed:
        rev_tour[x,y] = -tour[x,y]

    return rev_tour





###############################
### Drawing graphs
################################

def draw_interchange_graph(int_sequence, graph_type):
    if graph_type == 'C':
        directed_gr = True
    else:
        directed_gr = False

    # Initialize PyVis Network object with physics enabled
    net = Network(notebook=True, height="100%", width="100%", directed=directed_gr)
    net.set_edge_smooth('dynamic') ### For non-overlap of multiple edges
    
    graph = interchange_graph(int_sequence, graph_type)

    # Set the size of nodes and edges
    if len(graph.edges()) > 500:
        node_size = 9
        edge_width = 2
    elif len(graph.edges()) > 100:
        node_size = 10
        edge_width = 4
    elif len(graph.edges()) > 50:
        node_size = 12
        edge_width = 6
    elif len(graph.edges()) > 20:
        node_size = 18
        edge_width = 7
    else:
        node_size = 20
        edge_width = 10
    
    # Add nodes to the network
    for node in graph.nodes():
        net.add_node(node, label=None, size=node_size, color='#000000')

    for i, (source, target, data) in enumerate(graph.edges(data=True)):
        if data['kind'] == 'C':
            edge_color = '#009E73'
        elif data['kind'] == 'A':
            edge_color = '#56B4E9'
        elif data['kind'] == 'D':
            edge_color = '#E69F00'
        elif data['kind'] == 'B':
            edge_color = '#009E73'  

        # Multiple edges for kind 'C'
        # and single edges for other kinds
        if data['kind'] == 'C':
            net.add_edge(source, target, color=edge_color, arrows="no", width=edge_width)
            net.add_edge(source, target, color=edge_color, arrows="no", width=edge_width)
        else:
            net.add_edge(source, target, color=edge_color, arrows="no", width=edge_width)

    # Enable physics for force-directed layout
    # net.show_buttons(filter_=['physics'])  # Allows you to toggle physics options in the visualization
    #net.show_buttons(filter_=[])  # disables built-in menus
    net.force_atlas_2based(spring_length=100, spring_strength=0.08, gravity=-50, central_gravity=0.01)
    # net.set_options("""
    # var options = {
    # "physics": {
    #     "enabled": true,
    #     "solver": "forceAtlas2Based",
    #     "forceAtlas2Based": {
    #     "gravitationalConstant": -50,
    #     "centralGravity": 0.01,
    #     "springLength": 100,
    #     "springConstant": 0.08,
    #     "damping": 0.4,
    #     "avoidOverlap": 0.5
    #     },
    #     "stabilization": {
    #     "enabled": true,
    #     "iterations": 2,
    #     "updateInterval": 1
    #     }
    # }
    # }
    # """)


    os.makedirs("static", exist_ok=True)
    net.save_graph("static/graph.html")