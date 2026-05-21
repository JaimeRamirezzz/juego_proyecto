import numpy as np
import random as r

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
# 1. EL CEREBRO DEL ENEMIGO (algoritmo cadena de markov)
        # Lo guardamos aquí para que este enemigo recuerde sus propias probabilidades
        self.matriz_comportamiento = np.array([
            [0.7, 0.2, 0.1], # Fila 0 - Vida Alta:  [Ataque, Defensa, Huir]
            [0.4, 0.5, 0.1], # Fila 1 - Vida Media: [Ataque, Defensa, Huir]
            [0.2, 0.3, 0.5]  # Fila 2 - Vida Baja:  [Ataque, Defensa, Huir]
        ])
        self.lista_acciones = ["Ataque", "Defensa", "Huida"]


# traductor:
    # Esta función traduce la vida matemática a la fila de la matriz
    def evaluar_estado_salud(self):
        porcentaje_vida = self.hp_actual / self.hp_max
        
        if porcentaje_vida > 0.66:
            return 0  # Vida Alta -> Fila 0
        elif porcentaje_vida > 0.33:
            return 1  # Vida Media -> Fila 1
        else:
            return 2  # Vida Baja -> Fila 2
    
    
    #  Enfrentamiento necesita que esto sea un método para calcular_orden
    
    def decidir_accion(self):
        # Averiguamos en qué estado (fila) está basándonos en su vida real
        estado_actual = self.evaluar_estado_salud()
        
        # Sacamos las probabilidades de esa fila
        probabilidades = self.matriz_comportamiento[estado_actual]
        
        #  Elige 0, 1 o 2 según las probabilidades de numpy
        eleccion = np.random.choice([0, 1, 2], p=probabilidades)
        
        accion_elegida = self.lista_acciones[eleccion]
        
        print(f"🧠 {self.nombre} (HP: {self.hp_actual}/{self.hp_max}) evalúa su situación...")
        print(f"Decisión tomada: {accion_elegida}")
        
        return accion_elegida

    def ejecutar_turno_ia(self, objetivos_validos, master_path_table, graph):
        # NUEVO: Este es el método MAESTRO que llamará tu clase Enfrentamiento.
        
        self.en_defensa = False # Reseteamos la defensa al inicio de su turno
        self.current_mobility = self.max_mobility # Reseteamos movilidad
        
        accion = self.decidir_accion()
        
        if accion == "Ataque":
            if objetivos_validos:
                # Ataca al más débil (puedes cambiar esta lógica luego Jaime)
                objetivo = min(objetivos_validos, key=lambda x: x.hp_actual)
                daño = self.calculate_damage()
                
                # Faltaría la lógica de Moverse hacia él antes de atacar usando take_turn()
                print(f"⚔️ {self.nombre} se lanza al ataque contra {objetivo.nombre}.")
                objetivo.recibir_daño(daño)
            else:
                print(f"❓ {self.nombre} quiere atacar pero no hay objetivos. Se defiende en su lugar.")
                self.defender()
                
        elif accion == "Defensa":
            self.defender()
            
        elif accion == "Huida":
            self.huir(master_path_table, graph)



    
#para crear nuevas acciones sketch
    def defender(self):
        # NUEVO: Activa la bandera de defensa y termina su turno
        self.en_defensa = True
        print(f" ¡{self.nombre} adopta una postura defensiva! Recibirá menos daño el próximo turno.")

    def huir(self, master_path_table, graph):
        # NUEVO: Lógica básica de huida. Busca alejarse a un nodo aleatorio o "seguro".
        print(f"💨 ¡{self.nombre} entra en pánico e intenta huir!")
        
        # Como no tenemos las coordenadas del jugador aquí, una huida simple es 
        # elegir un nodo al azar al que pueda llegar con su movilidad actual.
        if self.current_node in master_path_table:
            nodos_alcanzables = list(master_path_table[self.current_node].keys())
            if nodos_alcanzables:
                # Elige un nodo al azar para escapar
                nodo_escape = r.choice(nodos_alcanzables)
                self.take_turn(master_path_table, master_path_table, nodo_escape, graph)
            else:
                print(f" {self.nombre} está acorralado y no puede huir.")

    

    
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
            self.hp_max = int(self.self.hp_max * 1.25) 
            self.hp_actual =  self.hp_max               
            print(f"Enemy {self.nombre} leveled up to Level {self.level}!")


    def calculate_damage(self):
        progressive_damage = int(self.base_damage * (1.15 ** (self.level - 1)))
        return progressive_damage


    # MODIFICADO: Se llama recibir_daño y usa hp_actual
    def recibir_daño(self, amount):
        # MODIFICADO: Ahora comprueba si el enemigo se está defendiendo
        daño_final = amount
        if self.en_defensa:
            daño_final = int(amount * 0.5) # Reduce el daño a la mitad
            print(f" ¡Bloqueo! {self.nombre} mitigó parte del daño.")

        self.hp_actual -= daño_final
        if self.hp_actual < 0: self.hp_actual = 0
        print(f" {self.nombre} recibió {daño_final} de daño! Vida restante: {self.hp_actual}/{self.hp_max}")
    
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
