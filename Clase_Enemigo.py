

class Enemy:
    _id_counter = 10000 # para dar prioridad a los personajes jugables
    
    # MODIFICADO: Añadido 'nombre' a los parámetros, ya que el bucle lo necesita para los prints
    def __init__(self, nombre, start_node, health, mobility, velocidad, level=1, equipo="enemigo"):
        self.nombre = nombre # <--- NUEVO
        self.current_node = start_node
        #Cambiado a hp_actual y hp_max para coincidir con la lógica gráfica
        self.hp_max = max_health
        self.hp_actual = max_health
        self.max_mobility = mobility
        self.current_mobility = mobility
        self.color = () 
        self.base_damage = 10 
        # guardamos la velocidad en una variable interna
        self._velocidad = stat_velocidad
        self.equipo = equipo
        self.id = Enemy._id_counter
        Enemy._id_counter += 1
        
        # NOTA: self.turn ha sido eliminado. ¡El árbitro (Enfrentamiento) ahora controla los turnos!
        
        # subir nivel
        self.level = level
        self.experience = 0
#  Enfrentamiento necesita que esto sea un método para calcular_orden()
    def velocidad(self):
        return self._velocidad

# +Comprueba hp_actual en lugar de una variable booleana separada
    def esta_vivo(self):
        return self.hp_actual > 0

    def level_up(self, exp_gained):
        self.experience += exp_gained
        exp_needed = int(100 * (self.level ** 1.5)) 

        if self.experience >= exp_needed:
            self.level += 1
            self.experience -= exp_needed
            self.max_health = int(self.max_health * 1.25) 
            self.health = self.max_health                
            print(f"Enemy {self.nombre} leveled up to Level {self.level}!")


    def calculate_damage(self):
        progressive_damage = int(self.base_damage * (1.15 ** (self.level - 1)))
        return progressive_damage

    # MODIFICADO: Se llama realizar_ataque. 
    # Ahora SOLO devuelve el número de daño. Pygame se encarga de aplicarlo.
    def realizar_ataque(self, objetivo):
        daño = self.calculate_damage()
        return daño

    # MODIFICADO: Se llama recibir_daño y usa hp_actual
    def recibir_daño(self, amount):
        self.hp_actual -= amount
        if self.hp_actual < 0:
            self.hp_actual = 0
        print(f"🩸 {self.nombre} recibió {amount} de daño! Vida restante: {self.hp_actual}/{self.hp_max}")
    

    def evaluate_routes(self, routes_dict):
        # MODIFICADO: Quitamos el "if self.turn == True:" porque si el juego llama
        # a esta función durante su turno en el bucle, ya damos por hecho que es su turno.
        if self.current_node in routes_dict:
            available_paths = routes_dict[self.current_node]
            print(f"Rutas disponibles {self.current_node}: {available_paths}")
            return available_paths
        return []


    def take_turn(self, master_path_table, master_distance_table, target_node, graph):
        # Verificamos que existan datos de ruta desde donde estamos hasta el objetivo
        if self.current_node in master_path_table and target_node in master_path_table[self.current_node]:
            path = master_path_table[self.current_node][target_node]
            
            print(f"\n-Movimiento enemigo {self.nombre}-")
            print(f"Objetivo final: {target_node} | Ruta ideal: {' -> '.join(path)}")

            # path[0] es el nodo en el que ya estamos, así que empezamos a iterar desde path[1]
            if len(path) > 1:
                ruta_a_seguir = path[1:]
            else:
                print(f"{self.nombre} ya está junto al objetivo.")
                return

            # Nos movemos nodo a nodo a lo largo del camino trazado por Dijkstra
            for paso_str in ruta_a_seguir:
                paso = int(paso_str) # Convertimos el string de Dijkstra a entero
                
                # Obtenemos cuánto cuesta moverse de nuestro nodo actual al siguiente paso
                # Usamos el grafo original (o tabla de distancias directas) para ver el coste de ese salto
                costo_paso = graph[self.current_node][paso]

                # Verificamos si tenemos movilidad suficiente para dar este salto
                if self.current_mobility >= costo_paso:
                    self.current_mobility -= costo_paso
                    self.current_node = paso # ACTUALIZAMOS POSICIÓN
                    print(f" {self.nombre} avanza al nodo {paso}. (Movilidad restante: {self.current_mobility})")
                else:
                    print(f" {self.nombre} agotó su movilidad. Se detiene en el nodo {self.current_node}.")
                    break # Rompemos el bucle porque ya no puede moverse más este turno
