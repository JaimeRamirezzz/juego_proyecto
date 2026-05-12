import random # Necesario para que la IA elija un objetivo al azar

class Enemy:
    _id_counter = 10000 # para dar prioridad a los personajes jugables
    
    # MODIFICADO: Añadido 'nombre' a los parámetros, ya que el bucle lo necesita para los prints
    def __init__(self, nombre, start_node, health, mobility, velocidad, level=1, equipo="enemigo"):
        self.nombre = nombre # <--- NUEVO
        self.current_node = start_node
        self.health = health
        self.max_health = health
        self.max_mobility = mobility
        self.current_mobility = mobility
        self.color = () 
        self.base_damage = 10 
        self.velocidad = velocidad
        self.equipo = equipo
        self._vivo = True
        self.id = Enemy._id_counter
        Enemy._id_counter += 1
        
        # NOTA: self.turn ha sido eliminado. ¡El árbitro (Enfrentamiento) ahora controla los turnos!
        
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
            print(f"Enemy {self.nombre} leveled up to Level {self.level}!")

    def calculate_damage(self):
        progressive_damage = int(self.base_damage * (1.15 ** (self.level - 1)))
        return progressive_damage

    # NUEVO: El bucle llama a este método para que la IA decida a quién golpear
    def ia_decidir_objetivo(self, aliados):
        # Filtramos para asegurarnos de que el enemigo no ataque a un aliado que ya está muerto
        aliados_vivos = [aliado for aliado in aliados if aliado.esta_vivo()]
        
        if aliados_vivos:
            # Lógica básica: Elige un aliado al azar. 
            # (En el futuro puedes cambiar esto para que ataque al de menos vida, por ejemplo)
            return random.choice(aliados_vivos)
        return None

    # MODIFICADO: Se cambió el nombre de 'attack' a 'atacar' para coincidir con el bucle.
    # Además, se eliminó el parámetro Combat_Manager. El enemigo solo se preocupa de hacer daño.
    def atacar(self, target):
        if target:
            actual_damage = self.calculate_damage()
            
            # Lo ideal es usar el método take_damage del objetivo si lo tiene
            if hasattr(target, 'take_damage'):
                target.take_damage(actual_damage)
            else:
                target.health -= actual_damage
                
            print(f"Daño de {self.nombre}: {actual_damage}")

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self._vivo = False
        print(f"{self.nombre} recibió {amount} de daño! Vida restante: {self.health}")
    
    def esta_vivo(self):
        return self._vivo

    def evaluate_routes(self, routes_dict):
        # MODIFICADO: Quitamos el "if self.turn == True:" porque si el juego llama
        # a esta función durante su turno en el bucle, ya damos por hecho que es su turno.
        if self.current_node in routes_dict:
            available_paths = routes_dict[self.current_node]
            print(f"Rutas disponibles {self.current_node}: {available_paths}")
            return available_paths
        return []

    # MODIFICADO: Limpieza de parámetros obsoletos. 
    # Igual que en atacar(), se elimina el Combat_manager de aquí.
    def take_turn(self, master_path_table, master_distance_table, target_node):
        if self.current_node in master_path_table and target_node in master_path_table[self.current_node]:
            path = master_path_table[self.current_node][target_node]
            distance_to_path = master_distance_table[self.current_node][target_node]

            self.max_mobility -= distance_to_path
            
            print(f"\n-Movimiento enemigo {self.nombre}-")
            print(f"objetivo: {target_node} | camino: {path}")
            self.current_mobility = self.max_mobility
