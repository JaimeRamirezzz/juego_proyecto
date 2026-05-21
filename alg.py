import numpy as np

"""
lo pongo asi para que se vea mejor:
    he adaptado el dijkstra original para que use los grids del mapa procedural.
    
    grid_costos: np.array 2D con costos de movimiento
    grid_caminable: np.array 2D bool (True = caminable)
    inicio/destino: tuplas (fila, col)
    
    retorna: (distancia_total, lista_de_nodos_como_tuplas)
"""
na = np.nan
def dijkstra(grid_costos, grid_caminable, inicio, destino):
     alto, ancho = grid_costos.shape
     inicio_y, inicio_x = inicio
     destino_y, destino_x = destino
    
     # Verificar límites y si son caminables
     if not (0 <= inicio_y < alto and 0 <= inicio_x < ancho):
        return float('inf'), []
     if not (0 <= destino_y < alto and 0 <= destino_x < ancho):
        return float('inf'), []
     if not grid_caminable[destino_y, destino_x]:
        return float('inf'), []
    
     # Convertir (fila,col) a índice único para el algoritmo
     def nodo_a_idx(y, x):
        return y * ancho + x
    
     def idx_a_nodo(idx):
        return (idx // ancho, idx % ancho)
    
     n = alto * ancho
     start_idx = nodo_a_idx(inicio_y, inicio_x)
     dest_idx = nodo_a_idx(destino_y, destino_x)
    
     # Crear matriz de adyacencia en formato del dijkstra original
     # na = no conectado, 0 = diagonal (mismo nodo), costo = conectado
     graph = np.full((n, n), np.nan)
     np.fill_diagonal(graph, 0)
    
     # llenar conexiones (4 direcciones: arriba, abajo, izquierda, derecha)
     for y in range(alto):
        for x in range(ancho):
            if not grid_caminable[y, x]:
                continue
            
            idx = nodo_a_idx(y, x)
            vecinos = [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
            
            for vy, vx in vecinos:
                if 0 <= vy < alto and 0 <= vx < ancho:
                    if grid_caminable[vy, vx]:
                        vidx = nodo_a_idx(vy, vx)
                        # Costo = costo de la casilla DESTINO
                        graph[idx, vidx] = grid_costos[vy, vx]
    
     distances = np.fromiter((0 if i == start_idx else np.inf for i in range(len(graph))), dtype='float')
     visited = np.full_like(graph[start_idx], 0, dtype='bool')
    # Esto crea una lista UNICA e independiente para cada nodo
     paths = {nodo: [str(start_idx)] for nodo in range(len(graph))}


     for _ in range(len(graph)):
        min_distance_node = np.where(distances == distances[~visited].min())[0][0]
        
        for node in range(len(graph)):
            if not graph[min_distance_node, node] > 0:
                continue
            distance_to_node = distances[min_distance_node] + graph[min_distance_node, node]
            if distance_to_node < distances[node] and visited[node] == False:
                distances[node] = distance_to_node
                paths[node] = paths[min_distance_node].copy()
                paths[node].append(str(node))

        visited[min_distance_node] = True

     for node, path in paths.items():
        print(f'The shortest path from node {start_idx} to node {node} is:\n{' -> '.join(path)}\nTotal distance: {distances[node]}', end='\n\n')

     return distances[dest_idx], paths
