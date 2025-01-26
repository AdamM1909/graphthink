from backend.db import *
from backend.db_ops import make_anki_deck, anki2graphsync

vs = [
   ("What are |E| and |V| in their most basic form?", 
    "|V| = number of vertices (nodes) - the points in your graph\n|E| = number of edges (connections) - the lines between points\nLike particles (V) and forces/interactions between them (E)"),

   ("What is the maximum possible number of edges in different graph types?",
    "Undirected: |E|max = |V|(|V|-1)/2 (each vertex connects to all others except itself)\nDirected: |E|max = |V|² (each vertex can connect to all vertices including itself)"),
   
   ("What makes a graph \"sparse\" vs \"dense\"?",
    "Sparse: |E| ≈ |V| (most nodes connect to few others)\nDense: |E| ≈ |V|² (most nodes connect to most other nodes)\nPhysical analogy: Short-range vs long-range forces between particles"),
   
   ("What are the three essential questions for any graph problem?",
    "1. How dense is the graph? (|E| vs |V|²)\n2. What invariants must remain true throughout?\n3. What special conditions exist? (Negative weights? Cycles? Disconnected parts?)"),
   
   ("How does density affect data structure choice?",
    "Dense (|E| ≈ |V|²): Use matrix (like Cartesian coordinates)\nSparse (|E| ≈ |V|): Use adjacency list (like sparse matrix)\nChoose based on memory vs access time trade-off"),
   
   ("What are the fundamental conservation laws in graphs?",
    "1. Visited + unvisited nodes = total nodes\n2. In spanning tree: edges = vertices - 1\n3. Triangle inequality: distance[v] ≥ distance[u] + weight(u,v)\nLike conservation laws in physics"),
   
   ("How does BFS differ from DFS physically?",
    "BFS: Like wave propagation on a surface\n\nFinds shortest paths (unweighted)\nExplores in layers\nDFS: Like following a single path until stuck\nMemory efficient (only depth needed)\nNatural for recursive problems"),
   
   ("Why do negative weights break Dijkstra's algorithm?",
    "Like time travel paradox:\n\nPositive weights: Can't arrive before leaving\nNegative weights: Later paths could be shorter\nExample: A→B(5), B→C(-10) better than A→C(2)"),
   
   ("What's the relationship between paths and physical systems?",
    "Shortest path ≈ Principle of least action\nPath capacity ≈ Conductance\nMultiple paths ≈ Parallel circuits\nEdge weights ≈ Resistance/Distance"),
   
   ("How do weighted vs unweighted graphs differ?",
    "Unweighted: Like digital (discrete) systems\n\nBFS finds shortest paths\nAll edges equal\nWeighted: Like analog (continuous) systems\nNeed Dijkstra/Bellman-Ford\nEdges have varying strengths"),
   
   ("What is the physical meaning of a strongly connected component?",
    "Like bound states in physics:\n\nAll points mutually reachable\nForm \"atomic\" units of graph\nInternal cycles possible\nUsed in: Circuit analysis, Web clustering"),
   
   ("How do bipartite graphs relate to physical systems?",
    "Two-colorable system properties:\n\nNo odd cycles\nVertices split into two sets\nLike: Alternating charges, Spin systems\nUsed in: Matching problems, Resource allocation"),
   
   ("What makes tree structures special in graphs?",
    "Properties:\n\nNo cycles\n|E| = |V| - 1\nUnique path between any two points\nLike hierarchical systems in nature"),
   
   ("What is special about minimum spanning trees?",
    "Like minimum energy state:\n\nConnects all vertices\nNo cycles\nMinimum total weight\n|V|-1 edges exactly"),
   
   ("How do adjacency matrices relate to physical operators?",
    "Like quantum operators:\n\nMatrix element (i,j) = interaction strength\nSymmetric for undirected graphs\nPowers show path lengths\nEigenvalues reveal structure"),
   
   ("What is the meaning of graph degree?",
    "Degree = number of connections\n\nLike coordination number in crystals\nIn-degree/out-degree for directed graphs\nAverage degree relates to density"),
   
   ("How do cycles affect graph algorithms?",
    "Cycles create:\n\nMultiple possible paths\nPotential infinite loops\nNeed for visited tracking\nLike closed orbits in physics"),
   
   ("What determines graph traversal efficiency?",
    "Key factors:\n\nMemory access patterns\nCache utilization\nBranch prediction\nLike optimizing physical measurements"),
   
   ("How do you handle graphs too large for memory?",
    "Three strategies:\n\nSampling (statistical approach)\nStreaming (one-pass algorithms)\nPartitioning (divide-and-conquer)\nLike handling large physical systems"),
   
   ("What makes dynamic graphs challenging?",
    "Like time-dependent systems:\n\nStructure changes over time\nNeed to update computations\nBalance update cost vs recomputation\nLocal vs global changes"),
   
   ("How do edge weights affect path finding?",
    "Like finding least action path:\n\nWeights = distance/cost/time\nTriangle inequality must hold\nOptimal subpath property\nNon-negative for Dijkstra"),
   
   ("What is the significance of graph connectivity?",
    "Like phase transitions:\n\nConnected vs disconnected components\nCritical thresholds\nPercolation behavior\nRelated to system stability"),
   
   ("How do directed vs undirected graphs differ fundamentally?",
    "Directed: Like one-way interactions\n\nAsymmetric relationships\nPossible cycles\nUndirected: Like mutual interactions\nSymmetric relationships\nSimpler paths"),
   
   ("What determines algorithm choice for graph problems?",
    "Key factors:\n\nGraph density (|E| vs |V|²)\nMemory constraints\nRequired accuracy\nSpecial properties (weights, cycles)"),
   
   ("How do graph partitions relate to physical systems?",
    "Like system decomposition:\n\nNatural communities\nMinimal coupling between parts\nBalance size vs connectivity\nUsed in: Parallel processing, Community detection")
]

if __name__ == "__main__":
    with AnkiDB() as adb: make_anki_deck(adb, vs, "GraphThink: Graph Algorithms")
    with AnkiDB() as adb, GraphDB() as gdb: anki2graphsync(adb, gdb)
