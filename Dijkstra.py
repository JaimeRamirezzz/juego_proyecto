import numpy as np

na = np.nan
inf = np.inf

def dijkstra(graph, start):
    distances = np.fromiter((0 if i == start else np.inf for i in range(len(graph))), dtype='float')
    visited = np.full_like(graph[start], 0, dtype='bool')

    paths = {nodo: [start] for nodo in range(len(graph))}

    for _ in range(len(graph)):
        
        # --- SOLUCIÓN AL BUG DIRECCIONAL ---
        # 1. Obtenemos una lista segura SOLO con los índices de los nodos no visitados
        nodos_no_visitados = np.where(~visited)[0] 
        
        # 2. Encontramos el nodo con la distancia mínima estrictamente dentro de esa lista
        min_distance_node = nodos_no_visitados[np.argmin(distances[nodos_no_visitados])]
        # -----------------------------------

        for node in range(len(graph)):
            if not graph[min_distance_node, node] > 0:
                continue
            distance_to_node = distances[min_distance_node] + graph[min_distance_node, node]

            if distance_to_node < distances[node] and visited[node] == False:
                distances[node] = distance_to_node
                paths[node] = paths[min_distance_node].copy()
                paths[node].append(node)

        visited[min_distance_node] = True

    distances_dict = {node: distances[node] for node in range(len(graph))}

    return paths, distances_dict
