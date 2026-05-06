class Enemy:
    def __init__(self, start_node, health, mobility, level=1):
        self.current_node = start_node
        self.health = health
        self.max_health = health
        self.max_mobility = mobility
        self.current_mobility = mobility
        self.color = () #colocar color
        self.base_damage = 100
        
        # subir nivel
        self.level = level
        self.experience = 0

    def level_up(self, exp_gained):

        self.experience += exp_gained
        
        exp_needed = int(100 * (self.level ** 1.5)) 

        if self.experience >= exp_needed:
            self.level += 1
            self.experience -= exp_needed
            self.max_health = int(self.max_health * 1.25) 
            self.health = self.max_health                
            print(f"Enemy leveled up to Level {self.level}!")

    def calculate_damage(self):

        progressive_damage = int(self.base_damage * (1.15 ** (self.level - 1)))
        return progressive_damage

    def attack(self, target):

        actual_damage = self.calculate_damage()
        target.health -= actual_damage
        print(f"Daño del {self.name} {actual_damage}")

    def take_damage(self, amount):
  
        self.health -= amount
        print(f"Daño recibido {amount}! vida {self.health}")

    def evaluate_routes(self, routes_dict):
        """
        NUEVA FUNCIÓN: Recibe un diccionario de nodos del mapa y devuelve los vecinos válidos.
        Formato de diccionario esperado: {node_id: [neighbor_id1, neighbor_id2, ...]}

        poner en funcion de mi otra funcion de busqueda simplemente cambiar nombres self.current_node y routes_dict
        """
        if self.current_node in routes_dict:
            available_paths = routes_dict[self.current_node]
            print(f"Rutas disponibles {self.current_node}: {available_paths}")
            return available_paths
        else:
            print(f"Nodo {self.current_node} no encontrado")
            return []

    def take_turn(self, target_node, path_table):
        # Resetea la mobilidad
        self.current_mobility = self.max_mobility

        # chequeo de seguiridad para evitar errores
        if self.current_node in path_table and target_node in path_table[self.current_node]:
            # mira las rutas del mapa

            path_table = master_path_table[self.current_node][target_node]

            
            distance_to_path = master_distance_table[self.current_node][target_node]

            self.max_mobility -= distance_to_path
 

            print(f"\n-Turno enemigo-")
            print(f"objetivo: {target_node} | camino: {path}")
        else:
            print(f"\n-Turno enemigo")
            print("No encontrado")
