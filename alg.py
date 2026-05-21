import numpy as np
from primera_mapa.mapa_juego.mapa import MapaProcedural
na = np.nan
inf = np.inf

lista = [MapaProcedural.generar_matriz_adyacencia]

graph = np.array(lista)

def dijkstra(graph, start):
    distances = np.fromiter((0 if i == start else np.inf for i in range(len(graph))), dtype='float')
    visited = np.full_like(graph[start], 0, dtype='bool')

    paths = {nodo: [start] for nodo in range(len(graph))}

    for _ in range(len(graph)):
        min_distance_node = np.where(distances == distances[~visited].min())[0][0]

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


master_path_table = {}
master_distance_table = {}

for i in range(len(graph)):
    paths, distances = dijkstra(graph, start=i)
    master_path_table[i] = paths
    master_distance_table[i] = distances



# distance
distanceto = master_distance_table[0][1]
print(f"distancia mas corta de {distanceto}")

# path
path_table = master_path_table[0][1]
print(f"camino tomado {path_table}")