import pygame # Importa la librería Pygame para manejar gráficos
from enum import Enum, auto 
import random as r
import opensimplex
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
import os
from panel_ataques import PanelAtaques
from Combat_manager import Combat_Manager
import numpy as np
from alg import dijkstra
from config import ANCHO_PANTALLA, ALTO_PANTALLA, ALTO_PANEL, ALTO_MAPA, TAMANO_CASILLA
from Clase_Enemigo import Enemy
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
        opensimplex.seed(self.config.semilla)
        self._generar_ruido = opensimplex.noise3
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
        TipoBioma.BOSQUE: "imagen/madera(3).png",  
        TipoBioma.LAVA: "imagen/lava(4).png",
        TipoBioma.PANTANO: "imagen/tierra(0).png"
    }

    PROPIEDADES_BIOMA = {
        TipoBioma.AGUA_PROFUNDA: {'caminable': False, 'costo': 5.0},
        TipoBioma.PRADERA: {'caminable': True, 'costo': 1.0},
        TipoBioma.BOSQUE: {'caminable': True, 'costo': 1.5, 'cobertura': 20},
        TipoBioma.MONTAÑA: {'caminable': False, 'costo': 2.9},
        TipoBioma.NIEVE: {'caminable': True, 'costo': 2.5},
        TipoBioma.LAVA: {'caminable': False, 'costo': 3.9},
        TipoBioma.PANTANO: {'caminable': True, 'costo': 3.0},
    }
    def __init__(self, ancho: int, alto: int, tamaño_casilla: int = 40, 
                 config: Configuracionmapa = None, carpeta_sprites: str = "imagen", offset_y: int = 0):
        self.ancho = ancho
        self.alto = alto
        self.tamaño_casilla = tamaño_casilla
        self.offset_y = offset_y
        
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
                img_temp = pygame.image.load(ruta_final).convert_alpha()
                imagen_escalada = pygame.transform.scale(img_temp, (self.tamaño_casilla, self.tamaño_casilla))
                self.imagenes_bioma[bioma] = imagen_escalada
                print(f"✅ Cargada imagen para {bioma.name}: {ruta_final}")
            except pygame.error as e:
                print(f"❌ Error cargando {ruta_final}: {e}")
                self.imagenes_bioma[bioma] = None

    def _crear_casillas(self):
        self.grid_costos = np.zeros((self.alto, self.ancho))
        self.grid_caminable = np.zeros((self.alto, self.ancho), dtype=bool)
        
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                px = x * self.tamaño_casilla
                py = y * self.tamaño_casilla + self.offset_y
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
                
                # ← AÑADIR estas 2 líneas al final del for x
                self.grid_costos[y, x] = casilla.costo_movimiento
                self.grid_caminable[y, x] = not casilla.obstaculo
            
            self.casillas.append(fila)
            self.matriz_adyacencia = self.generar_matriz_adyacencia()
            self.master_path_table = {}
            self.master_distance_table = {}

            for i in range(len(self.matriz_adyacencia)):
              paths, distances = dijkstra(self.matriz_adyacencia, start=i)
              self.master_path_table[i] = paths
              self.master_distance_table[i] = distances

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
            TipoEnemigo.SLIME_AGUA: {"nombre": "Slime de Agua", "vida": 4, "ataque": 2, "defensa": 5, "velocidad": 6},
            TipoEnemigo.LOBO_BOSQUE: {"nombre": "Lobo del Bosque", "vida": 9, "ataque": 15, "defensa": 8, "velocidad": 20},
            TipoEnemigo.GOLEM_MONTAÑA: {"nombre": "Golem de Piedra", "vida": 25, "ataque": 20, "defensa": 25, "velocidad": 4},
            TipoEnemigo.ESQUELETO_NIEVE: {"nombre": "Esqueleto Helado", "vida": 13, "ataque": 12, "defensa": 6, "velocidad": 13},
            TipoEnemigo.ELEMENTAL_FUEGO: {"nombre": "Elemental de Fuego", "vida": 5, "ataque": 25, "defensa": 10, "velocidad": 25},
            TipoEnemigo.COCODRILO_PANTANO: {"nombre": "Cocodrilo del Pantano", "vida": 10, "ataque": 18, "defensa": 15, "velocidad": 12},
            TipoEnemigo.BANDIDO_PRADERA: {"nombre": "Bandido", "vida": 8, "ataque": 14, "defensa": 10, "velocidad": 15},
        }
        
        stats = stats_base.get(tipo, {"nombre": "Desconocido", "vida": 10, "ataque": 5, "defensa": 2})
        
        return Enemy(
            start_node=(x, y),
            max_health=stats["vida"],
            mobility=10,
            velocidad=stats.get("velocidad", 10),
            level=1,
            equipo="enemigo",
            nombre=stats.get("nombre", "Enemigo")
        )

    def colocar_jugador(self, jugador):
        """
        Busca la primera casilla vacía y caminable, coloca al jugador.
        
        jugador: instancia de Jugador
        Retorna: True si se colocó, False si no hay espacio
        """
        for fila in self.casillas:
            for casilla in fila:
                # Casilla vacía, caminable, sin obstáculo, sin entidad
                if not casilla.obstaculo and not casilla.esta_ocupada(): # colocar_jugador ya usa propiedades_bioma automaticamente, la casilla ya tiene obstaculo
                    
                    casilla.colocar_entidad(jugador)
                    casilla.tipo = Tipo_casilla.PERSONAJE_JUGADOR
                    jugador.current_node = (casilla.fila, casilla.col)
                    return True

        return False
    def dibujar(self, pantalla):
    # dibuja el mapa completo: biomas, imágenes, entidades...
     for fila in self.casillas:
        for casilla in fila:
            rect = pygame.Rect(casilla.x, casilla.y, casilla.tamaño, casilla.tamaño)
            
            # Dibujar bioma (imagen o color sólido)
            if (casilla.bioma in self.imagenes_bioma and 
                self.imagenes_bioma[casilla.bioma] is not None):
                
                pantalla.blit(self.imagenes_bioma[casilla.bioma], (casilla.x, casilla.y))
            else:
                # Color de respaldo según bioma
                color = self.COLORES_BIOMA.get(casilla.bioma, (200, 200, 200))
                pygame.draw.rect(pantalla, color, rect)
            
            # Borde sutil para distinguir casillas
            pygame.draw.rect(pantalla, (100, 100, 100), rect, 1)
            
            # Dibujar entidad si hay
            if casilla.entidad:
                self._dibujar_entidad(pantalla, casilla)

    def _dibujar_entidad(self, pantalla, casilla):
        # Dibuja un círculo (jugador) o cuadrado (enemigo) en la casilla.
        centro_x = casilla.x + casilla.tamaño // 2
        centro_y = casilla.y + casilla.tamaño // 2
        radio = casilla.tamaño // 3

        entidad = casilla.entidad

        if getattr(entidad, 'equipo', None) == 'jugador':
            color = getattr(entidad, 'color', (100, 200, 255))
            pygame.draw.circle(pantalla, color, (centro_x, centro_y), radio)
            pygame.draw.circle(pantalla, (255, 255, 255), (centro_x, centro_y), radio, 2)
        else:
            color = getattr(entidad, 'color', (255, 50, 50))
            rect_entidad = pygame.Rect(
                centro_x - radio,
                centro_y - radio,
                radio * 2,
                radio * 2
            )
            pygame.draw.rect(pantalla, color, rect_entidad)
            pygame.draw.rect(pantalla, (50, 0, 0), rect_entidad, 2)

    def encontrar_camino(self, origen, destino):
        origen_id = origen[0] * self.ancho + origen[1]
        destino_id = destino[0] * self.ancho + destino[1]

        distancia = self.master_distance_table[origen_id][destino_id]
        camino_ids = self.master_path_table[origen_id][destino_id]

        camino = [(nodo // self.ancho, nodo % self.ancho) for nodo in camino_ids]

        return distancia, camino

    def get_rutas_disponibles(self, nodo_actual, max_distancia):
        """
        Para IA de enemigos: todas las casillas alcanzables dentro de distancia.

        nodo_actual: (fila, col)
        max_distancia: movilidad del personaje

        Retorna: dict {(fila,col): distancia, ...}
        """
        alto, ancho = self.grid_costos.shape
        rutas = {}

        for y in range(alto):
            for x in range(ancho):
                if (y, x) == nodo_actual:
                    continue
                if not self.grid_caminable[y, x]:
                    continue

                dist, camino = dijkstra(
                    self.grid_costos,
                    self.grid_caminable,
                    nodo_actual,
                    (y, x)
                )

                if dist <= max_distancia and camino:
                    rutas[(y, x)] = dist

        return rutas
    def actualizar_grid(self, fila, col):
    #actualiza los grids numpy cuando una casilla cambia.
    #Llama esto después de mover/colocar/quitar entidades.

        casilla = self.casillas[fila][col]
        self.grid_costos[fila, col] = casilla.costo_movimiento
        self.grid_caminable[fila, col] = not casilla.obstaculo

    def generar_matriz_adyacencia(self) -> np.ndarray:
        """
        Traduce el grid 2D del mapa actual a una matriz de adyacencia de nodos numéricos.
        Las casillas no caminables o sin conexión directa se marcan como np.inf.
        """
        total_nodos = self.alto * self.ancho
        
        # 1. Crear matriz llena de infinitos e inicializar la diagonal en 0
        matriz_adyacencia = np.full((total_nodos, total_nodos), np.inf)
        np.fill_diagonal(matriz_adyacencia, 0)
        
        # Direcciones: Arriba, Abajo, Izquierda, Derecha
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Función interna para convertir (fila, columna) -> ID único indexado
        def obtener_id(f, c):
            return f * self.ancho + c

        # 2. Recorrer el mapa para conectar los vecinos
        for f in range(self.alto):
            for c in range(self.ancho):
                nodo_origen = obtener_id(f, c)
                
                # Si la casilla origen es un obstáculo, nadie transita por ella
                if not self.grid_caminable[f, c]:
                    continue
                    
                for df, dc in direcciones:
                    nf, nc = f + df, c + dc
                    
                    # Validar límites del mapa
                    if 0 <= nf < self.alto and 0 <= nc < self.ancho:
                        # Si el vecino es caminable, registramos el costo de su bioma
                        if self.grid_caminable[nf, nc]:
                            nodo_destino = obtener_id(nf, nc)
                            costo = self.grid_costos[nf, nc]
                            
                            matriz_adyacencia[nodo_origen, nodo_destino] = costo

        return matriz_adyacencia


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Mapa Procedural - Juego y Panel")

    ANCHO_CASILLAS = 16  
    ALTO_CASILLAS_MAPA = 8   
    TAMANO_CASILLA = 62  

   
    ALTO_MAPA_PIXELES = ALTO_CASILLAS_MAPA * TAMANO_CASILLA 
    ALTO_PANEL_PIXELES = ALTO_MAPA_PIXELES // 2             
    
    ANCHO_VENTANA = ANCHO_CASILLAS * TAMANO_CASILLA
    ALTO_VENTANA = ALTO_MAPA_PIXELES + ALTO_PANEL_PIXELES   

    
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))

    import random

    tematicas = [
        Configuracionmapa(), # Normal
        Configuracionmapa(nivel_agua_profunda=0.2, nivel_montaña=0.9), # Agua
        Configuracionmapa(nivel_agua_profunda=-1.0, nivel_montaña=-0.5, nivel_lava_temp=-1.0), # Lava
        Configuracionmapa(nivel_agua_profunda=-1.0, nivel_pradera=-1.0, nivel_montaña=1.0) # Madera
    ]
    
    nivel_actual = 0 
    
    config_inicial = tematicas[nivel_actual]
    config_inicial.semilla = random.randint(0, 100000)

    mapa_del_juego = MapaProcedural(
        ancho=ANCHO_CASILLAS, 
        alto=ALTO_CASILLAS_MAPA, 
        tamaño_casilla=TAMANO_CASILLA, 
        config=config_inicial,
        carpeta_sprites="primera mapa/imagen" 
    )

    ejecutando = True
    reloj = pygame.time.Clock()

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    nivel_actual += 1
                    if nivel_actual >= len(tematicas):
                        nivel_actual = 0 
                        
                    print(f"Cambiando al nivel {nivel_actual}...")
                    
                    nueva_config = tematicas[nivel_actual]
                    nueva_config.semilla = random.randint(0, 100000) 

                    mapa_del_juego = MapaProcedural(
                        ancho=ANCHO_CASILLAS, 
                        alto=ALTO_CASILLAS_MAPA, 
                        tamaño_casilla=TAMANO_CASILLA, 
                        config=nueva_config,
                        carpeta_sprites="primera mapa/imagen"
                    )

        pantalla.fill((0, 0, 0)) 
        
        mapa_del_juego.dibujar(pantalla)

        rect_panel = pygame.Rect(0, ALTO_MAPA_PIXELES, ANCHO_VENTANA, ALTO_PANEL_PIXELES)
        pygame.draw.rect(pantalla, (40, 40, 40), rect_panel) 
        pygame.draw.rect(pantalla, (150, 150, 150), rect_panel, 4) 

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    if __name__ == "__main__":
     pygame.init()
    
    pantalla = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Mapa Procedural Generata")
    color_fondo = (30, 150, 50)
    
  
    mi_mapa = MapaProcedural(ancho=14, alto=7, tamaño_casilla=62, carpeta_sprites="imagen")
    
    ejecutando = True
    reloj = pygame.time.Clock()

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    print("Genera un nuovo mapa casual...")
                    mi_mapa = MapaProcedural(ancho=25, alto=18, tamaño_casilla=32, carpeta_sprites="imagen")

        pantalla.fill(color_fondo) 
        
        mi_mapa.dibujar(pantalla)

        pygame.display.flip()
        
        reloj.tick(60)

    pygame.quit()