import pygame # Importa la librería Pygame para manejar gráficos
from enum import Enum, auto 
import random as r
import opensimplex
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
import os

# Clase para definir las propiedades de cada tipo de suelo/terreno de manera aleatoria
class TipoBioma(Enum):
    AGUA_PROFUNDA = auto()
    PRADERA = auto()
    BOSQUE = auto()
    MONTAÑA = auto()
    NIEVE = auto()
    LAVA = auto()
    PANTANO = auto()
class Tipo_casilla(Enum):
    VACIA = auto()
    OBSTACULO = auto()
    ZONA_MOVIMIENTO = auto()
    ZONA_ATAQUE = auto()
    SELECCIONADA = auto()
    PERSONAJE_JUGADOR = auto()
    PERSONAJE_ENEMIGO = auto()
class TipoEnemigo(Enum): # estos son solo ejemplos para asignar a cada bioma pero se pueden cambiar
    SLIME_AGUA = auto()
    LOBO_BOSQUE = auto()
    GOLEM_MONTAÑA = auto()
    ESQUELETO_NIEVE = auto()
    ELEMENTAL_FUEGO = auto()
    COCODRILO_PANTANO = auto()
    BANDIDO_PRADERA = auto()
ENEMIGOS_POR_BIOMA = {
    TipoBioma.PRADERA: [TipoEnemigo.BANDIDO_PRADERA],
    TipoBioma.BOSQUE: [TipoEnemigo.LOBO_BOSQUE],
    TipoBioma.MONTAÑA: [TipoEnemigo.GOLEM_MONTAÑA],
    TipoBioma.NIEVE: [TipoEnemigo.ESQUELETO_NIEVE],
    TipoBioma.LAVA: [TipoEnemigo.ELEMENTAL_FUEGO],
    TipoBioma.PANTANO: [TipoEnemigo.COCODRILO_PANTANO],
}
@dataclass
class Configuracionmapa:
    semilla: int = None
    escala: float = 25.0
    octavas: int = 4
    persistencia: float = 0.5
    lacunaridad: float = 2.0
    nivel_agua_profunda: float = -0.6
    nivel_pradera: float = 0.2
    nivel_bosque: float = 0.4
    nivel_montaña: float = 0.7
    nivel_lava_temp: float = 0.5

    def __post_init__(self):
        if self.semilla is None:
            self.semilla = r.randint(0, 100000)
# Clase para gestionar la construcción y el dibujo del nivel 
# si queremos que los enemigos se generen por el tipo de mapa, hay que indicar
# que tipo de enemigo queremos que se genere dependiendo del bioma y meter la class enemigo aqui
class Enemy:
    _id_counter = 10000 # para dar prioridad a los personajes jugables
    def __init__(self, start_node, health, mobility, velocidad, level=1, equipo="enemigo"):
        self.current_node = start_node
        self.health = health
        self.max_health = health
        self.max_mobility = mobility
        self.current_mobility = mobility
        self.color = () #colocar color
        self.base_damage = 10 # nerf importante
        self.turn = False
        self.velocidad = velocidad
        self.equipo = equipo
        self._vivo = True
        self.id = Enemy._id_counter
        Enemy._id_counter +=1
        
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

    def attack(self, Combat_Manager, target):
        #combat manager lo cree en otra carpeta

        if self.turn:
            actual_damage = self.calculate_damage()
            target.health -= actual_damage
            print(f"Daño del {self.name} {actual_damage}")
            Combat_manager.next_turn()
        else:
            pass

    def take_damage(self, amount):

        self.health -= amount
        if self.health <= 0:
            self._vivo=False
        print(f"Daño recibido {amount}! vida {self.health}")
    
    def esta_vivo(self):
        return self._vivo

    def evaluate_routes(self, routes_dict):
        """
        NUEVA FUNCIÓN: Recibe un diccionario de nodos del mapa y devuelve los vecinos válidos.
        Formato de diccionario esperado: {node_id: [neighbor_id1, neighbor_id2, ...]}

        poner en funcion de mi otra funcion de busqueda simplemente cambiar nombres self.current_node y routes_dict
        """
        if self.turn == True:
            if self.current_node in routes_dict:
                available_paths = routes_dict[self.current_node]
                print(f"Rutas disponibles {self.current_node}: {available_paths}")
            return available_paths

    def take_turn(self, master_path_table, master_distance_table, target_node, path_table, Combat_manager):
        
        

        # chequeo de seguiridad para evitar errores

        if self.turn: 
            if self.current_node in path_table and target_node in path_table[self.current_node]:
            # mira las rutas del mapa

                path_table = master_path_table[self.current_node][target_node]

            
                distance_to_path = master_distance_table[self.current_node][target_node]

                self.max_mobility -= distance_to_path
 

                print(f"\n-Turno enemigo-")
                print(f"objetivo: {target_node} | camino: {path}")
                Combat_manager.next_turn()
                self.current_mobility = self.max_mobility 


# necesitamos definir la clase casilla para que hayan vacias, con obstaculos, movimiento, zona de ataque
# zona seleccionada, casilla en donde este el jugador y la casilla donde este el enemigo.
class Casilla:
    COLORES_TIPO = {
        Tipo_casilla.VACIA: (200, 200, 200),
        Tipo_casilla.OBSTACULO: (50, 50, 50),
        Tipo_casilla.ZONA_MOVIMIENTO: (100, 200, 255, 128),
        Tipo_casilla.ZONA_ATAQUE: (255, 100, 100, 128),
        Tipo_casilla.SELECCIONADA: (255, 255, 100),
        Tipo_casilla.PERSONAJE_JUGADOR: (100, 255, 100),
        Tipo_casilla.PERSONAJE_ENEMIGO: (255, 50, 50),
    }

    def __init__(self, fila: int, col: int, x: int, y: int, tamaño: int, 
                 tipo: Tipo_casilla, obstaculo: bool = False):
        self.fila = fila
        self.col = col
        self.x = x  # posición en píxeles
        self.y = y
        self.tamaño = tamaño
        self.tipo = tipo
        self.obstaculo = obstaculo
        self.entidad = None  # puede ser Enemigo o Jugador
        self.bioma = TipoBioma.PRADERA
        # propiedades de terreno
        self.costo_movimiento = 1.0
        self.cobertura = 0
        self.resbaladizo = False
        self.daño_terreno = 0
        self.prob_veneno = 0.0

    def color_casilla(self):
        return self.COLORES_TIPO.get(self.tipo, (200, 200, 200))

    def esta_ocupada(self):
        return self.entidad is not None
    def colocar_entidad(self, entidad):
       # método seguro para colocar entidades sin que se crashsee nada
        if not self.esta_ocupada() and not self.obstaculo:
            self.entidad = entidad
            if hasattr(entidad, 'current_node'):
                entidad.current_node = (self.fila, self.col)
            return True
        return False

    def remover_entidad(self):
        # método seguro para remover entidades sinque se crashsee nada.
        entidad = self.entidad
        self.entidad = None
        return entidad

# ya que tenemos el mapa definido, generamos lo que lo hara procedural
class GeneradorMapaProcedural:
    def __init__(self, config: Configuracionmapa = None):
        self.config = config or Configuracionmapa()
        self.ancho = 0
        self.alto = 0
        self.grid_altura = []
        self.grid_temperatura = []
        self.grid_humedad = []
        self._generar_ruido = opensimplex.OpenSimplex(seed =self.config.semilla)
    def generar_mapa(self, ancho:int, alto:int):
        self.ancho = ancho
        self.alto = alto
        self.grid_altura = [[0.0 for _ in range(ancho)] for _ in range(alto)]
        self.grid_humedad = [[0.0 for _ in range(ancho)] for _ in range(alto)]
        self.grid_temperatura = [[0.0 for _ in range(ancho)] for _ in range(alto)]
        biomas = [[TipoBioma.PRADERA for _ in range(ancho)] for _ in range(alto)]
        for y in range(alto):
            for x in range(ancho):
                # Generar altura (terreno base)
                self.grid_altura[y][x] = self._generar_ruido(x, y, 0)

                # Generar humedad (offset diferente para variedad)
                self.grid_humedad[y][x] = self._generar_ruido(x + 1000, y + 1000, 1)

                # Generar temperatura
                self.grid_temperatura[y][x] = self._generar_ruido(x + 2000, y + 2000, 2)

                # Determinar bioma
                biomas[y][x] = self._determinar_bioma(
                    self.grid_altura[y][x],
                    self.grid_humedad[y][x],
                    self.grid_temperatura[y][x]
                )

        # Suavizar biomas aislados (osea los que se queden como un pixel o algo así)
        biomas = self._suavizar_biomas(biomas)

        return biomas
    def _determinar_bioma(self, altura, humedad, temperatura): # esto determinará que bioma se generará
        cfg = self.config
        if altura < cfg.nivel_agua_profunda:
            return TipoBioma.AGUA_PROFUNDA
        elif altura > cfg.nivel_montaña:
            if temperatura > cfg.nivel_lava_temp:
                return TipoBioma.LAVA
            elif temperatura < -0.3:
                return TipoBioma.NIEVE
            return TipoBioma.MONTAÑA
        elif altura > cfg.nivel_bosque and temperatura > cfg.nivel_lava_temp:
            return TipoBioma.LAVA
        if humedad > 0.6 and temperatura > 0.0:
            if altura < cfg.nivel_pradera:
                return TipoBioma.PANTANO
            return TipoBioma.BOSQUE
        if humedad > 0.3 and altura > cfg.nivel_pradera:
            return TipoBioma.BOSQUE
        return TipoBioma.PRADERA # este es el default
        
    def _suavizar_biomas(self, biomas): #evita que aparezcan casillas sueltas de un bioma rodeadas completamente por otro bioma diferente,es como quitar los "píxeles sueltos" o manchas aisladas que quedan feas y no tienen sentido lógico.   
        resultado = [fila[:] for fila in biomas]
        for y in range(1, self.alto - 1):
            for x in range(1, self.ancho - 1):
                actual = biomas[y][x]
                vecinos = [
                    biomas[y-1][x], biomas[y+1][x], 
                    biomas[y][x-1], biomas[y][x+1]
                ]
                if all(v != actual for v in vecinos):
                    if actual == TipoBioma.AGUA_PROFUNDA:
                        resultado[y][x] = TipoBioma.AGUA_PROFUNDA
                    else:
                        resultado[y][x] = max(set(vecinos), key=vecinos.count)
        return resultado
    def obtener_altura(self, x: int, y: int): 
        # Simplemente devuelve el valor de la altura que ya calculó el generador para cada casilla.
        if 0 <= y < self.alto and 0 <= x < self.ancho:
            return self.grid_altura[y][x]
        return 0.0
class MapaProcedural:
    COLORES_BIOMA = {
        TipoBioma.AGUA_PROFUNDA: (20, 40, 80),
        TipoBioma.PRADERA: (120, 180, 80),
        TipoBioma.BOSQUE: (40, 100, 40),
        TipoBioma.MONTAÑA: (80, 80, 90),
        TipoBioma.NIEVE: (240, 250, 255),
        TipoBioma.LAVA: (200, 60, 20),
        TipoBioma.PANTANO: (100, 140, 100),
    } # por si no hay pngs de respaldo
    IMAGENES_BIOMA = {
        TipoBioma.AGUA_PROFUNDA: "imagen/agua(2).png",
        TipoBioma.PRADERA: "imagen/hierba(1).png",
        TipoBioma.LAVA: "imagen/lava(4).png",
        TipoBioma.PANTANO: "imagen/tierra(0).png"
    }

    PROPIEDADES_BIOMA = {
        TipoBioma.PRADERA: {'caminable': True, 'costo': 1.0},
        TipoBioma.BOSQUE: {'caminable': True, 'costo': 1.5, 'cobertura': 20},
        TipoBioma.MONTAÑA: {'caminable': False, 'costo': 2.9},
        TipoBioma.NIEVE: {'caminable': True, 'costo': 2.5},
        TipoBioma.LAVA: {'caminable': False, 'costo': 3.9},
        TipoBioma.PANTANO: {'caminable': True, 'costo': 3.0},
    }
    def __init__(self, ancho: int, alto: int, tamaño_casilla: int = 40, 
                 config: Configuracionmapa = None, carpeta_sprites: str = "imagen"):
        self.ancho = ancho
        self.alto = alto
        self.tamaño_casilla = tamaño_casilla
        
        # Generar mapa procedural
        self.generador = GeneradorMapaProcedural(config)
        self.biomas = self.generador.generar_mapa(ancho, alto)
        
        # Cargar imágenes de biomas
        self.imagenes_bioma = {}
        self._cargar_imagenes(carpeta_sprites)
        
        # Crear casillas
        self.casillas = []
        self.entidades_posiciones = {}
        self.enemigos = []
        self._crear_casillas()
        
        # Generar enemigos según biomas
        self._generar_enemigos()

    def _cargar_imagenes(self, imagen: str):
        #carga las imágenes PNG para cada bioma.
        #si una imagen no existe, usa el color de respaldo.
        for bioma, ruta_relativa in self.IMAGENES_BIOMA.items():
            ruta_completa = os.path.join(imagen, os.path.basename(ruta_relativa))
            
            # Intentar cargar desde la ruta especificada
            if os.path.exists(ruta_relativa):
                ruta_final = ruta_relativa
            elif os.path.exists(ruta_completa):
                ruta_final = ruta_completa
            else:
                # Si no existe, dejar como None (usará color)
                self.imagenes_bioma[bioma] = None
                print(f"⚠️  No se encontró imagen para {bioma.name}: {ruta_relativa}")
                continue
            
            try:
                imagen = pygame.image.load(ruta_final).convert_alpha()
                # Escalar al tamaño de casilla
                imagen_escalada = pygame.transform.scale(imagen, (self.tamaño_casilla, self.tamaño_casilla))
                self.imagenes_bioma[bioma] = imagen_escalada
                print(f"✅ Cargada imagen para {bioma.name}: {ruta_final}")
            except pygame.error as e:
                print(f"❌ Error cargando {ruta_final}: {e}")
                self.imagenes_bioma[bioma] = None

    def _crear_casillas(self):
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                px = x * self.tamaño_casilla
                py = y * self.tamaño_casilla
                bioma = self.biomas[y][x]
                props = self.PROPIEDADES_BIOMA[bioma]
                
                casilla = Casilla(
                    fila=y, col=x, x=px, y=py,
                    tamaño=self.tamaño_casilla,
                    tipo=Tipo_casilla.OBSTACULO if not props['caminable'] else Tipo_casilla.VACIA,
                    obstaculo= not props['caminable']
                )
                
                casilla.bioma = bioma
                casilla.costo_movimiento = props['costo']
                casilla.cobertura = props.get('cobertura', 0)
                fila.append(casilla)
            self.casillas.append(fila)

    def _generar_enemigos(self, densidad: float = 0.05):
        id_enemigo = 0
        
        for y in range(self.alto):
            for x in range(self.ancho):
                casilla = self.casillas[y][x]
                
                if casilla.tipo == Tipo_casilla.OBSTACULO or casilla.esta_ocupada():
                    continue
                
                if r.random() < densidad:
                    bioma = casilla.bioma
                    tipos_posibles = ENEMIGOS_POR_BIOMA.get(bioma, [])
                    
                    if tipos_posibles:
                        tipo_enemigo = r.choice(tipos_posibles)
                        enemigo = self._crear_enemigo(tipo_enemigo, id_enemigo, x, y)
                        casilla.colocar_entidad(enemigo)
                        self.enemigos.append(enemigo)
                        id_enemigo += 1

    def _crear_enemigo(self, tipo: TipoEnemigo, id_enemigo: int, x: int, y: int) -> Enemy:
        stats_base = {
            TipoEnemigo.SLIME_AGUA: {"nombre": "Slime de Agua", "vida": 4, "ataque": 8, "defensa": 5, "velocidad": 3},
            TipoEnemigo.LOBO_BOSQUE: {"nombre": "Lobo del Bosque", "vida": 45, "ataque": 15, "defensa": 8, "velocidad": 6},
            TipoEnemigo.GOLEM_MONTAÑA: {"nombre": "Golem de Piedra", "vida": 10, "ataque": 20, "defensa": 25, "velocidad": 10},
            TipoEnemigo.ESQUELETO_NIEVE: {"nombre": "Esqueleto Helado", "vida": 13, "ataque": 12, "defensa": 6, "velocidad": 17},
            TipoEnemigo.ELEMENTAL_FUEGO: {"nombre": "Elemental de Fuego", "vida": 5, "ataque": 25, "defensa": 10, "velocidad": 25},
            TipoEnemigo.COCODRILO_PANTANO: {"nombre": "Cocodrilo del Pantano", "vida": 10, "ataque": 18, "defensa": 15, "velocidad": 12},
            TipoEnemigo.BANDIDO_PRADERA: {"nombre": "Bandido", "vida": 8, "ataque": 14, "defensa": 10},
        }
        
        stats = stats_base.get(tipo, {"nombre": "Desconocido", "vida": 10, "ataque": 5, "defensa": 2})
        
        return Enemy(
            start_node=(x, y),
            health=stats["vida"],
            mobility=10,
            level=1
        )
