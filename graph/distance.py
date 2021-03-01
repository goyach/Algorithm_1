from Algorithm_1.structure.graph_struct import GraphNotAimed, Vertex, Graph
from Algorithm_1.structure.list_struct import TwoWayList
from Algorithm_1.structure.heap import BinaryHeap
from Algorithm_1.graph.mst import BinaryHeapPrim
from Algorithm_1.graph.dfs import topology
import numpy as np


def dijkstra(G, s):
    """
    dijkstra algorithm:
        if |E| * 0.75  < |V|^2 : the struct will be min heap
        else:                    the struct will be array

        this method work only with positive edges

    @params:
        @G: graph
        @s: vertex to start

    return:
        return pi dict
        if restore=True the mst graph (=Minimal spreadsheet graph) will be return also

    efficiency:
        if |E| * 0.75  < |V|^2: => O(Vlog V)
        if |E| * 0.75  > |V|^2: => O(E) = O(|V|^2)
    """
    struct = 'heap' if len(G.E) < (len(G.V) ** 2) * 0.75 else 'array'
    pi = {v: None for v in G.V}
    _init(G, s)
    key = lambda v: v.data['key']
    Q = BinaryHeapPrim(arr=G.V, compare=min, key=key) if struct == 'heap' else [v for v in G.V]

    while struct == 'heap' and Q.arr or struct == 'array' and Q:
        v, v.data['in heap'] = Q.extract() if struct == 'heap' else Q.pop(Q.index(min(Q, key=key))), False
        for e in v.edges:
            if e.to.data['in heap']:
                relax(e, pi)
                if struct == 'heap':
                    Q.add(Q.pop(e.to.data['i']))

    return pi


def bellman_ford(G, s):
    """
        bellman ford algorithm:
            found distance between s and all other vertex
            this method work also with negative edges

        @params:
            @G: graph
            @s: vertex to start

        return:
            return pi dict or False if there is negative circle in the graph

        efficiency: O(|E|*|V|)
        """
    pi = {v: None for v in G.V}
    _init(G, s)

    for i in range(len(G.V) - 1):
        for e in G.E:
            relax(e, pi)
    for e in G.E:
        if e.to.data['key'] > e.from_.data['key'] + e.weight:
            print('negative circle in the graph')
            return False

    return pi


def dag(G, s):
    """
    dag algorithm:
        found distance between s and all other vertex
        this method work only with graph without circle

    @params:
        @G: graph
        @s: vertex to start

    return:
        return pi dict or False if there is circle in the graph

    efficiency: O(|E|+|V|)
    """
    topology_order = topology(G)
    if not topology_order:
        return
    pi = {v: None for v in G.V}
    _init(G, s)
    for v in topology_order:
        for e in v.edges:
            relax(e, pi)
    return pi


def relax(e, pi):
    if e.to.data['key'] > e.weight + e.from_.data['key']:
        e.to.data['key'], pi[e.to] = e.weight + e.from_.data['key'], e.from_


def _init(G, s):
    '''
    help method for bellman_ford() and dijkstra()
    init all vertex in G:
        insert dictionary with key=inf , and in heap=True
        the key in the start vertex (=s) will be 0

    @param:
        G: graph
        s: vertex to start from
    '''
    for v in G.V:
        v.data = {'key': float('inf'), 'in heap': True}
    s.data['key'] = 0


'''------------------------------   all pairs distance  -------------------------------------'''


def floyd_warshall(G):
    """
    bellman ford algorithm:
        found distance between all pairs of vertex
        this method work also with negative edges

    @params:
        @G: graph

    return (matrix of distances,matrix of pi)

    the algorithm:
        In any external iteration the algorithm try to check for all pairs of
        vertex if the the passage through the G.V[k] will shorten the way

    efficiency: O(|V|^3)
    """
    D, PI = init_all_pairs(G)
    for k in range(len(G.V)):
        for i in range(len(G.V)):
            for j in range(len(G.V)):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j], PI[i][j] = D[i][k] + D[k][j], PI[k][j]

    return D, PI


def all_pairs_dijkstra(G):
    """
    run dijkstra from the all vertex of G:
        found distance between all pairs of vertex
        this method work only with positive edges

    @params:
        @G: graph

    return (matrix of distances,matrix of pi)

    efficiency:
           if |E| * 0.75  < |V|^2: => O(V^2*log V)
           if |E| * 0.75  > |V|^2: => O(V*E) = O(|V|^3)
    """
    D, PI = [], []
    for v in G.V:
        PI.append(list(dijkstra(G, v).values()))
        D.append([v.data['key'] for v in G.V])
    return D, PI


def all_pairs_bellman_ford(G):
    """
    run bellman ford from the all vertex of G:
        found distance between all pairs of vertex
        this method work also with negative edges

    @params:
       @G: graph

    return: (matrix of distances,matrix of pi)

    efficiency: O(|V|*|E|*|V|) = O(|E||V|^2)
    """
    D, PI = [], []
    for v in G.V:
        PI.append(list(bellman_ford(G, v).values()))
        D.append([v.data['key'] for v in G.V])
    return D, PI


def all_pairs_dynamic_slow(G):
    """
    dynamic algorithm (=slow version):
        found distance between all pairs of vertex
        this method work also with negative edges

    @params:
        @G: graph

    return: (matrix of distances,matrix of pi)

    the algorithm:
        In any iteration the algorithm expand the all shorted path with +1 edge
        so max iterations in the external loop will be |V|

    efficiency: O(|V|^4)
    """
    D, PI = init_all_pairs(G)
    W = D
    for i in range(2, len(G.V) - 1):
        expand(D, W, PI)
    return D, PI


def all_pairs_dynamic_fast(G):
    """
    dynamic algorithm (=fast version):
        found distance between all pairs of vertex
        this method work also with negative edges

    the algorithm:
        In any iteration the algorithm expand the all shorted path *2
        so max iterations in the external loop will be log|V|

    @params:
        @G: graph

    return: (matrix of distances,matrix of pi)

    efficiency: O(|V|^3*log|V|)
    """
    D, PI = init_all_pairs(G)
    m = 1
    while m < len(G.V) - 1:
        expand(D, D, PI)
        m *= 2
    return D, PI


def expand(D, W, PI):
    """
    expand the short path for all pairs
    """
    for i in range(len(G.V)):
        for j in range(len(G.V)):
            for k in range(len(G.V)):
                if D[i][k] + W[k][j] < D[i][j]:
                    D[i][j], PI[i][j] = D[i][k] + W[k][j], PI[k][j]


def init_all_pairs(G):
    D, PI = [[float('inf') for v in G.V] for v in G.V], [[None for v in G.V] for v in G.V]
    for i, v in zip(range(len(G.V)), G.V):
        v.data = {'i': i}
    for v in G.V:
        D[v.data['i']][v.data['i']] = 0
        for e in v.edges:
            D[v.data['i']][e.to.data['i']], PI[v.data['i']][e.to.data['i']] = e.weight, v
    return D, PI


def johnson(G):
    pass


if __name__ == '__main__':
    V = [Vertex(name=str(i)) for i in range(8)]
    V[1].name, V[2].name, V[3].name, V[4].name, V[5].name, V[6].name = '1', '2', '3', '4', '5', '6'
    # r = Edge(from_=V[0], to=V[1], weight=3)
    # G = GraphNotAimed(V=V)
    # G.connect(from_=V[0], to=V[1], weight=4)
    # G.connect(from_=V[0], to=V[4], weight=3)
    # G.connect(from_=V[0], to=V[3], weight=2)
    # G.connect(from_=V[1], to=V[2], weight=5)
    # G.connect(from_=V[1], to=V[4], weight=4)
    # G.connect(from_=V[1], to=V[5], weight=6)
    # G.connect(from_=V[2], to=V[5], weight=1)
    # G.connect(from_=V[3], to=V[4], weight=6)
    # G.connect(from_=V[4], to=V[5], weight=8)
    # ---------------------
    # G.connect(from_=V[0], to=V[2], weight=8)
    # G.connect(from_=V[0], to=V[5], weight=8)
    # G.connect(from_=V[1], to=V[0], weight=8)
    # G.connect(from_=V[1], to=V[3], weight=8)
    # G.connect(from_=V[2], to=V[3], weight=8)
    # G.connect(from_=V[2], to=V[4], weight=8)
    # pi = dijkstra(G, G.V[0])
    # print('------------------------')
    # print([v.data['key'] for v in G.V])
    # print(pi.values())
    # pi = bellman_ford(G, G.V[0])
    # print('------------------------')
    # print([v.data['key'] for v in G.V])
    # print(pi.values())
    G = Graph()
    for i in range(1, 7):
        G.V.append(V[i])
    G.connect(from_=V[1], to=V[2], weight=4)
    G.connect(from_=V[2], to=V[3], weight=6)
    G.connect(from_=V[2], to=V[5], weight=16)
    G.connect(from_=V[2], to=V[6], weight=20)
    G.connect(from_=V[3], to=V[5], weight=5)
    G.connect(from_=V[4], to=V[1], weight=2)
    G.connect(from_=V[4], to=V[2], weight=8)
    G.connect(from_=V[5], to=V[1], weight=7)
    G.connect(from_=V[5], to=V[4], weight=9)
    G.connect(from_=V[5], to=V[6], weight=7)
    G.connect(from_=V[6], to=V[3], weight=8)

    # print(np.array([floyd_warshall(G)]))
    # print('-------------------')
    # print(np.array([all_pairs_dijkstra(G)]))
    D, PI = floyd_warshall(G)
    D_, PI_ = all_pairs_dijkstra(G)
    D_1, PI_1 = all_pairs_bellman_ford(G)
    D_2, PI_2 = all_pairs_dynamic_slow(G)
    D_3, PI_3 = all_pairs_dynamic_fast(G)
    print(np.array_equal([D, PI], [D_, PI_]))
    print(np.array_equal([D, PI], [D_1, PI_1]))
    print(np.array_equal([D, PI], [D_2, PI_2]))
    print(np.array_equal([D, PI], [D_3, PI_3]))

    # print(np.array([D, PI], [D_3, PI_3]))

    # dijkstra(G, G.V[1])
    # pi = dag(G, V[0])
    # print([v.data['key'] for v in G.V])
    # print(pi.values())
