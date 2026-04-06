import pygame as pg
import math as m
import random as r
from enum import Enum as e
from dataclasses import dataclass, field
import time
from typing import Optional

pg.init()
window = pg.display.set_mode((1000, 700))
estado_partida = 0 # para controlar que se va a mostrar por pantalla y tambien si estamos en combate o en tienda o cosas asi

#espacio para las variables:


# Paleta de colores: (se pueden cambiar)
GB_COLORS = {
    'white': (224, 248, 208),
    'light_gray': (136, 192, 112),
    'dark_gray': (52, 104, 86),
    'black': (8, 24, 32),
    "green_bright": (120, 200, 80),    # Zona movimiento
    "red_bright": (200, 80, 80),       # Zona ataque  
    "yellow_bright": (255, 220, 80),   # Seleccionada
    "blue_bright": (100, 150, 255),    # Hover
}


class NodoCola:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
    
class ColaEnlazada: #Me suena que era mejor que la otra"
    def __init__(self):
        self.front = None
        self.rear = None
    def empty(self):
        return self.front is None
    def first(self):
        if self.empty:
            raise IndexError('No se puede consultar una cola vacía')
        return self.front.dato
    def push(self, dato):
        nuevo = NodoCola(dato)
        if self.empty:
            #el nuevo nodo sera el front u rear
            self.front = nuevo
            self.rear = nuevo
        else:
            self.rear.siguiente = nuevo
            self.rear = nuevo
    def pop(self):
        if self.empty:
            raise IndexError('No se puede eliminar un elementode una cola vacía')
        dato = self.front.dato
        self.front = self.front.siguiente
        
        if self.front is None:
            self.rear = None
        return dato

class AnimationState(e): # Estados de animación
    IDLE = e.auto() # Quieto (2 frames: parpadeo)
    WALK = e.auto() # Caminando (2-4 frames)
    ATTACK = e.auto() # Ataque (2-3 frames, rápido)
    HURT = e.auto() # Daño recibido (2 frames, flash)
    FAINT = e.auto() # Debilitado (2-4 frames, caída)
    SPECIAL = e.auto() # Movimiento especial (3-4 frames)
   
class tipo_Casilla(e):
    VACIA = e.auto()
    OBSTACULO = e.auto()
    PERSONAJE_JUGADOR = e.auto()
    PERSONAJE_ENEMIGO = e.auto()
    ZONA_MOVIMIENTO = e.auto()
    ZONA_ATAQUE = e.auto()
    SELECCIONADA = e.auto()
    MOVER = e.auto()
class Direccion(e):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)
class Casilla:
    fila: int          # Todo esto puede cambiarse pero de momento lo dejo asi
    col: int
    x: int
    y: int
    tamaño: int = 40
    tipo: tipo_Casilla = tipo_Casilla.VACIA
    entidad: Optional["Batalla"] = None # referencia a clase batalla
    obstaculo: bool = False
    # pathfinding
    distancia: int = 0
    visitada: bool = False
    padre: Optional[tuple[int, int]] = None
    def __post_init__(self):
        self.rect = pg.Rect(self.x, self.y, self.tamaño, self.tamaño)
        self.centro = (self.x + self.tamaño // 2, self.y +self.tamaño // 2)
    def color_casilla(self): # Devuelve color segun el tipo de casilla
        colores = {
        tipo_Casilla.VACIA: GB_COLORS["white"],
        tipo_Casilla.OBSTACULO: GB_COLORS["dark_gray"],
        tipo_Casilla.PERSONAJE_JUGADOR: GB_COLORS["light_gray"],
        tipo_Casilla.PERSONAJE_ENEMIGO: GB_COLORS["dark_gray"],
        tipo_Casilla.ZONA_MOVIMIENTO: GB_COLORS["green_bright"],
        tipo_Casilla.ZONA_ATAQUE: GB_COLORS["red_bright"],
        tipo_Casilla.SELECCIONADA: GB_COLORS["yellow_bright"],
        tipo_Casilla.MOVER: GB_COLORS["blue_bright"]
        }
        return colores.get(self.tipo, GB_COLORS["white"])
  #  def dibujar(self, superficie: , hover: bool = False): Para cuando tengamos en mapa definido 
#class SistemaGRid:
# def __init__(self, filas: int = 10, columnas: int = 10, 
#                 tamaño_casilla: int = 40, offset_x: int = 50, offset_y: int = 100):
#        self.filas = filas
#       self.columnas = columnas
#        self.tamaño_casilla = tamaño_casilla
#        self.offset_x = offset_x
#         self.offset_y = offset_y
        
        # Crear matriz de casillas
#        self.casillas: List[List[Casilla]] = []
#        self._crear_grid()
        
        # Estado de interacción
#        self.casilla_hover: Optional[Casilla] = None
#        self.casilla_seleccionada: Optional[Casilla] = None
#        self.entidad_seleccionada: Optional['Batalla'] = None

# continuará en cuanto estemos mas avanzados en el tema del mapa

class AnimacionFrame: # representa un frame de animacion
    surface: pg.surface
    duration: int # duracion ciclos de animacion
    offset: tuple[int, int] = (0, 0) # Offset de posición para efectos

class spritesheets: # hoja de sprites
    def __init__(self, image_path: r[str] = None):
        self.sprite_size = 16
        self.sprites: list[pg.Surface] = []

        if image_path:
            self.load_from_file(image_path)
        else:
          # Crear sprites placeholder estilo pokémon si no hay archivo  
          self._create_placeholder_sprites()

    def _create_placeholder_sprites(self): #Crea sprites placeholder
        # Posición base:
        sprite1 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite1.fill(GB_COLORS["white"])
        # cuerpo
        pg.draw.rect(sprite1, GB_COLORS["dark_gray"], (4, 4, 8, 8))
        # ojos
        pg.draw.rect(sprite1, GB_COLORS['black'], (5, 6, 2, 2))
        pg.draw.rect(sprite1, GB_COLORS['black'], (9, 6, 2, 2))
        self.sprites.append(sprite1)
        
        # Frame alternativo (ojos cerrados/posición diferente)
        sprite2 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite2.fill(GB_COLORS['white'])
        pg.draw.rect(sprite2, GB_COLORS['dark_gray'], (4, 5, 8, 7))  # Ligeramente más bajo
        # Ojos cerrados (líneas)
        pg.draw.line(sprite2, GB_COLORS['black'], (5, 7), (6, 7))
        pg.draw.line(sprite2, GB_COLORS['black'], (9, 7), (10, 7))
        self.sprites.append(sprite2)
        
        # Ataque (brazo/boca extendida)
        sprite3 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite3.fill(GB_COLORS['white'])
        pg.draw.rect(sprite3, GB_COLORS['dark_gray'], (4, 4, 8, 8))
        pg.draw.rect(sprite3, GB_COLORS['black'], (5, 6, 2, 2))
        pg.draw.rect(sprite3, GB_COLORS['black'], (9, 6, 2, 2))
        # Boca abierta/ataque
        pg.draw.rect(sprite3, GB_COLORS['black'], (6, 10, 4, 2))
        self.sprites.append(sprite3)
        
        # Daño
        sprite4 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite4.fill(GB_COLORS['white'])
        # (colores invertidos)
        pg.draw.rect(sprite4, GB_COLORS['light_gray'], (4, 4, 8, 8))
        pg.draw.rect(sprite4, GB_COLORS['white'], (5, 6, 2, 2))
        pg.draw.rect(sprite4, GB_COLORS['white'], (9, 6, 2, 2))
        self.sprites.append(sprite4)
    
    def get_sprite(self, index: int):
        return self.sprites[index % len(self.sprites)]
    
    def scale_sprite(self, sprite: pg.Surface, scale: int): # escala sprites sin romper la imagen
        size = sprite.get_size()
        return pg.transform.scale(sprite, (size[0] * scale, size[1] * scale))

class EjecAnimacion: # sistema de animacion limitado
    def __init__(self, sprite_sheet: spritesheets ):
        self.sprite_sheet = sprite_sheet
        self.current_state = AnimationState.IDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        
        # Configuración de animaciones (frame indices y duraciones)
        self.animations = {
            AnimationState.IDLE: {
                'frames': [0, 1],  # Parpadeo
                'durations': [30, 5],  # Mucho tiempo abierto, poco cerrado
                'loop': True
            },
            AnimationState.WALK: {
                'frames': [0, 1],
                'durations': [8, 8],  # Más rápido
                'loop': True
            },
            AnimationState.ATTACK: {
                'frames': [2, 0],  # Frame de ataque y vuelta
                'durations': [10, 10],
                'loop': False,
                'callback': 'return_to_idle'  # volver a idle al terminar
            },
            AnimationState.HURT: {
                'frames': [3, 0, 3, 0],  # flash de daño
                'durations': [5, 5, 5, 5],
                'loop': False,
                'callback': 'return_to_idle'
            },
            AnimationState.FAINT: {
                'frames': [0, 1, 1, 1],  # Caida gradual
                'durations': [10, 10, 10, 999],  # Último frame infinito
                'loop': False
            }
        }
        
        # Shake effect para daño
        self.shake_offset = (0, 0)
        self.shake_intensity = 0
        
        # Blink effect (para daño)
        self.blink = False
    
    def set_state(self, state: AnimationState):
        # Cambia el estado de animación
        if state != self.current_state:
            self.current_state = state
            self.frame_index = 0
            self.animation_timer = 0
            self.shake_intensity = 0
    
    def update(self):
        # Actualiza la animación (llamar cada frame)
        anim_config = self.animations[self.current_state]
        current_frame_duration = anim_config['durations'][self.frame_index]
        
        self.animation_timer += 1
        
        # Efecto de shake si hay daño
        if self.shake_intensity > 0:
            import random
            self.shake_offset = (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity)
            )
            self.shake_intensity = max(0, self.shake_intensity - 1)
        
        # Cambiar frame si es tiempo
        if self.animation_timer >= current_frame_duration:
            self.animation_timer = 0
            self.frame_index += 1
            
            # Manejar fin de animación
            if self.frame_index >= len(anim_config['frames']):
                if anim_config.get('loop', True):
                    self.frame_index = 0
                else:
                    self.frame_index = len(anim_config['frames']) - 1
                    # Callback para volver a idle
                    if 'callback' in anim_config:
                        if anim_config['callback'] == 'return_to_idle':
                            self.set_state(AnimationState.IDLE)

# Todavia hay que añadir cosas pero como no tenemos personajes definidos de momento se queda asi.
class sistemagrid:
    def __init__(self):
        self.animacion = None # referencia opcional
    def casilla_a_pixel(self, fila, col): # convierte grid a pixeles para las animaciones
        casilla = self.obtener_casilla(fila, col)
        return casilla.centro
    def mover_entidad_con_animacion(self, entidad, nueva_fila, nueva_col, sistema_animacion, EjecAnimacion):
        x_orig, y_orig = self.casilla_a_pixel(entidad.fila, entidad.col)
        x_dest, y_dest = self.casilla_a_pixel(nueva_fila, nueva_col)
        sistema_animacion.animar_movimiento(entidad, x_dest, y_dest) # Llamar al sistema de animacion existente
        self.mover_entidad(entidad, nueva_fila, nueva_col) # Actualizar posicion logica

class TipoTerreno(e):
    TIERRA = e.auto()
    HIERBA_ALTA = e.auto()
    HIERBA_SECA = e.auto()
    AGUA = e.auto()
    LAVA = e.auto()
    PIEDRA_CALIENTE = e.auto()
    HIELO = e.auto()
    ACIDO = e.auto()
class Elemento(e):
    NEUTRO = e.auto()
    FUEGO = e.auto()
    AGUA = e.auto()
    ELECTRICO = e.auto()
    HIELO = e.auto()
    VENENO = e.auto()

@dataclass
class ModificadorElemental: # Como afecta el terreno a cada elemento 
    potenciacion: float = 1.0
    probabilidad_efecto: float = 0.0
    daño_por_turno: int = 0
    turnos_estado: int = 0

@dataclass
class EfectoTerreno:
    nombre: str
    descripcion: str
    caminable: bool = True
    modificadores: dict[Elemento, ModificadorElemental] = field(default_factory = dict)
    interacciones: dict[TipoTerreno, callable] = field(default_factory = dict) # Qué pasa cuando interactúa con otro terreno
    probabilidad_evento: float = 0.0 # Probabilidad de evento especial (resbalón, etc.)
    requiere_objeto: Optional[str] = None # Objeto que anula efectos negativos
    def obtener_modificador(self, elemento: Elemento) -> ModificadorElemental:
        return self.modificadores.get(elemento, ModificadorElemental())

class EfectosTerrenoFactory: # Crea configuraciones de terreno predefinidas
    @staticmethod
    def crear_tierra() -> EfectoTerreno:
        return EfectoTerreno(
            nombre = "Tierra",
            descripcion = "Terreno normal sin efectos ni consecuencias especiales",
            caminable = True,
            modificadores = {} # sin modificadores
        )
    @staticmethod
    def crear_hierba_alta() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Hierba Alta",
            descripcion="El fuego se propaga fácilmente aquí. Ataques de fuego potenciados.",
            caminable=True,
            modificadores={
                Elemento.FUEGO: ModificadorElemental(
                    potenciacion=1.5,
                    probabilidad_efecto=0.3,
                    daño_por_turno=5,
                    turnos_estado=2
                )
            },
            interacciones={
                # Si entra fuego, se convierte en hierba seca
                TipoTerreno.HIERBA_SECA: lambda casilla: casilla.cambiar_terreno(TipoTerreno.HIERBA_SECA)
            }
        )
    
    @staticmethod
    def crear_hierba_seca() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Hierba Seca",
            descripcion="¡Peligro de incendio! El fuego es extremadamente potente.",
            caminable=True,
            modificadores={
                Elemento.FUEGO: ModificadorElemental(
                    potenciacion=2.0,
                    probabilidad_efecto=0.6,
                    daño_por_turno=8,
                    turnos_estado=3
                ),
                Elemento.AGUA: ModificadorElemental(
                    potenciacion=1.0,  # Normal
                    probabilidad_efecto=1.0  # Siempre apaga el fuego
                )
            },
            interacciones={
                # Agua vuelve a hierba normal
                TipoTerreno.TIERRA: lambda casilla: casilla.cambiar_terreno(TipoTerreno.TIERRA)
            }
        )
    
    @staticmethod
    def crear_agua() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Agua",
            descripcion="Apaga el fuego y potencia ataques eléctricos. Se propaga.",
            caminable=True,  # Asumimos que pueden nadar o es poco profunda
            modificadores={
                Elemento.FUEGO: ModificadorElemental(
                    potenciacion=0.5,  # Mitad de daño
                    probabilidad_efecto=1.0,  # Siempre apaga
                    daño_por_turno=0,
                    turnos_estado=0
                ),
                Elemento.ELECTRICO: ModificadorElemental(
                    potenciacion=1.5,  # Afecta área
                    probabilidad_efecto=0.4,
                    daño_por_turno=0,
                    turnos_estado=0
                )
            },
            interacciones={
                # Agua + Lava = Piedra caliente
                TipoTerreno.PIEDRA_CALIENTE: lambda casilla: casilla.cambiar_terreno(TipoTerreno.PIEDRA_CALIENTE),
                # Agua + Hierba seca = Tierra
                TipoTerreno.TIERRA: lambda casilla: casilla.cambiar_terreno(TipoTerreno.TIERRA)
            }
        )
    
    @staticmethod
    def crear_lava() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Lava",
            descripcion="Daño extremo por fuego. El agua la solidifica.",
            caminable=True,  # Solo inmunes al fuego
            modificadores={
                Elemento.FUEGO: ModificadorElemental(
                    potenciacion=2.5,
                    probabilidad_efecto=0.0,  # Ya están en lava
                    daño_por_turno=15,
                    turnos_estado=0
                ),
                Elemento.AGUA: ModificadorElemental(
                    potenciacion=0.0,  # No daño directo, pero transforma terreno
                    probabilidad_efecto=1.0
                )
            },
            interacciones={
                # Agua convierte lava en piedra caliente
                TipoTerreno.PIEDRA_CALIENTE: lambda casilla: casilla.cambiar_terreno(TipoTerreno.PIEDRA_CALIENTE)
            }
        )
    
    @staticmethod
    def crear_piedra_caliente() -> EfectoTerreno:
        """Lava + Agua = Obstáculo dañino"""
        return EfectoTerreno(
            nombre="Piedra Caliente",
            descripcion="Restos de lava solidificada. Causa quemaduras. Agua menos efectiva.",
            caminable=True,  # Se puede caminar pero duele
            modificadores={
                Elemento.FUEGO: ModificadorElemental(
                    potenciacion=1.0,  # Normal para fuego
                    probabilidad_efecto=0.0,
                    daño_por_turno=5,  # Daño residual por calor
                    turnos_estado=2
                ),
                Elemento.AGUA: ModificadorElemental(
                    potenciacion=0.5,  # Eficacia reducida 50%
                    probabilidad_efecto=0.0
                )
            }
        )
    
    @staticmethod
    def crear_hielo() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Hielo",
            descripcion="Superficie resbaladiza. El electricidad se debilita.",
            caminable=True,
            modificadores={
                Elemento.ELECTRICO: ModificadorElemental(
                    potenciacion=0.7,  # Menos conducción
                    probabilidad_efecto=0.0
                ),
                Elemento.FUEGO: ModificadorElemental(
                    potenciacion=1.3,  # Derrite hielo
                    probabilidad_efecto=0.5,
                    daño_por_turno=0,
                    turnos_estado=0
                )
            },
            probabilidad_evento=0.25,  # 25% de resbalarse
            requiere_objeto="botas_anti_resbalantes"
        )
    
    @staticmethod
    def crear_acido() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Ácido",
            descripcion="Sustancia corrosiva. Daño continuo sin cura conocida.",
            caminable=True,
            modificadores={
                Elemento.VENENO: ModificadorElemental(
                    potenciacion=2.0,
                    probabilidad_efecto=0.8,
                    daño_por_turno=10,
                    turnos_estado=5
                )
            },
            # No tiene interacciones - no se puede eliminar
        )





class Entidad:
    id: int
    nombre: str
    velocidad_base: int
    hp: int = 100
    max_hp: int = 100
    equipo: str = "neutral"  # "jugador", "enemigo", "neutral" o los equipos que pongamos
    x: int = 0
    y: int = 0
    # estado de combate
    estados: list[str] = pg.field(default_factory=list) # tipo aturdido o envenenado o algo asi
    modificadores_vel: int = 0
    def velocidad(self):
        return max(0, self.velocidad_base + self.modificadores_vel)
    def estar_vivo(self):
        return self.hp > 0
    def __lt__(self, other): # ordena por velocidad, osea el mayor primero.
        return self.velocidad() > other.velocidad()
    def __repr__(self):
        return f"{self.nombre}(Vel:{self.velocidad()}, HP:{self.hp})"
        
class enfrentamiento:
    def __init__(self, jugadores: list[Batalla], mapa_tablero, enemigos: list[Batalla]):#ej = entidad jugable
        self._jugadas = 0
        self.tablero = mapa_tablero # provisional hasta el tablero
        self.aliados = jugadores #de momento se queda así, pero se puede modificar en el futuro
        self.enemigos = enemigos
        self.todas_entidades = list[Batalla] = []
        self._actualizar_lista_entidades()
        # cola de turnos ordenada por velocidad:
        self.orden = ColaEnlazada() # cola ordenada en funcion de la velocidad
        self.entidad_actual = e.Optional[Entidad] = None
        # historial de turnos
        self.historial_turnos = []
        # estado de enfrentamiento:
        self.activo = False
        self.ganador = None
    def _actualizar_lista_entidades(self): # actualiza la lista uniendo aliados y enemigos
        self.todas_entidades = []
        for e in self.aliados + self.enemigos:
            if e.esta_viva():
                self.todas_entidades.append(e)
    def _noEntidades(self):
        return len(self.todas_entidades)
    def calcular_orden(self):
        participantes = [e for e in self.todas_entidades if e.esta_viva()]
        # Ordenar por velocidad descendente (usando __lt__ de Entidad)
        # Si hay empate, el que tenga menor ID va primero (más estable)
        ordenados = sorted(participantes, key=lambda e: (-e.velocidad(), e.id))
        return ordenados
    def granTurno(self): #aún me queda por introducir y me faltan como me van a llegar las cosas para el enfrentamiento
        self._actualizar_lista_entidades() # actualiza la lista de entidades vivas
        if self._verificar_fin_combate():
            return False # combate terminado
        # para calcular nuevo orden:
        orden_iniciativa = self.calcular_orden_iniciativa()
        #limpiar y rellenar cola:
        self.orden.clear()
        for entidad in orden_iniciativa:
            self.orden.push(entidad)
        self._jugadas +=1
        print(f"\n RONDA {self._jugadas} ")
        print(f"Orden de iniciativa: {[e.nombre for e in orden_iniciativa]}")
        return True
    def actualizar_atb_todos(self):
        # Sistema ATB: actualiza la barra de todos y retorna quién listo para actuar
        # Llama esto en un loop o cada frame de tu juego
        if not self.usar_atb:
            return None
            
        listos = []
        for entidad in self.todas_entidades:
            if entidad.esta_viva() and entidad.actualizar_atb(self.delta_time):
                listos.append(entidad)
        
        # Si hay múltiples listos, el más rápido actúa primero
        if listos:
            listos.sort(key=lambda e: -e.velocidad())
            return listos[0]
        return None
    def pequeTurno(self): # Avanza al siguiente turno dentro de la ronda actual y retorna la entidad a la que le toca actuar, o none si hay que iniciar nueva ronda.
       if self.orden.empty():
           return None
       self.entidad_actual = self.orden.pop() # obtener la siguiente entidad
       # verificacion de supervivencia
       if not self.entidad_actual.esta_viva():
           return self.pequeTurno() # saltar al siguiente
       #historial:
       self.historial_turnos.append({
           "Ronda": self._jugadas,
           "Entidad": self.entidad_actual.nombre,
           "Equipo": self.entidad_actual.equipo # esto se puede modificar dependiendo de como sea el juego al final
       })
       print(f"\n -> Turno de: {self.entidad_actual.nombre} ({self.entidad_actual.equipo})")
       return self.entidad_actual
    def iniciar_combate(self, usar_atb = False):
       # Inicializa el primer granTurno
       self.usar_atb = usar_atb
       self.activo = True
       for e in self.todas_entidades:
            e.reset_atb()
        
       if not usar_atb:
        self.granTurno()
        return self.pequeTurno()
       return None # # En ATB, el primer listo se determina por actualizar_atb_todos()
    
    def finalizar_turno(self, acciones_realizadas = None):
       # Llamar cuando una entidad termina su turno.
       # opcionalmente registra que hizo.
        if self.entidad_actual:
            self.entidad_actual.reset_atb()  # Importante para ATB
        
        if acciones_realizadas:
            self.historial_turnos[-1].update(acciones_realizadas)
        
        if not self.usar_atb and self.orden.empty():
            return self.granTurno()
        return True
    
    def _verificar_fin_combate(self) -> bool:
       # Verifica si el combate ha terminado
        aliados_vivos = any(e.esta_viva() for e in self.aliados)
        enemigos_vivos = any(e.esta_viva() for e in self.enemigos)
        
        if not aliados_vivos:
            self.ganador = "enemigos"
            self.activo = False
            print("¡Derrota! , Todos los aliados han caído.")
            return True
        
        if not enemigos_vivos:
            self.ganador = "jugadores"
            self.activo = False
            print("¡Victoria! , Todos los enemigos han sido derrotados.")
            return True
        
        return False
    
    def get_entidad_actual(self):
        # Obtiene quién tiene el turno actual sin avanzar
        return self.entidad_actual
    
    def es_turno_jugador(self):
       # Verifica si el turno actual es de un aliado
        return self.entidad_actual and self.entidad_actual in self.aliados
    
    def obtener_objetivos_validos(self, atacante: Batalla = None):
        # obtiene objetivos válidos para atacar
        atacante = atacante or self.entidad_actual
        if not atacante:
            return []
        
        if atacante.equipo == "aliados":
            return [e for e in self.enemigos if e.esta_viva()]
        return [j for j in self.aliados if j.esta_viva()]
    def mostrar_estado(self):
       #  Visualizacion del combate
        print(f"\n ESTADO RONDA {self._jugadas}")
        print("ALIADOS:")
        for j in self.aliados:
            print(f"  {j}")
        print("ENEMIGOS:")
        for e in self.enemigos:
            print(f"  {e}")
class Batalla:
    _id_counter = 0 # para generar ids unicos
    def __init__(self, nombre, base_ataque, base_defensa, base_velocidad, nivel=1, es_boss = False, equipo = None):
        Batalla._id_counter += 1
        self.id = Batalla._id_counter
        self.nombre = nombre
        self.nivel = nivel
        self.equipo = equipo
        # stats "orignales"
        self.ataque = base_ataque + (2 * nivel) + m.log(nivel + 1)
        self.defensa = base_defensa + (1.5 * nivel) + m.log(nivel + 1)
        self.velocidad = base_velocidad + (0.5 * nivel) + m.log(nivel + 1)

        multiplicador_tpk = 20 if es_boss else 5
        self.hp_max = (self.ataque * multiplicador_tpk) + (5 * m.log(nivel + 1))
        self.hp_actual = self.hp_max
        # posición en el mapa
        self.x = 0
        self.y = 0

        self.progreso_atb = 0 # Acumulador para el sistema de velocidad (active time battle)
        self.vivo = True

        # Estados y modificadores (para compatibilidad con Enfrentamiento)
        self.estados = []
        self.modificadores_vel = 0
    def velocidad(self):
        return max(0.1, self.velocidad_base + self.modificadores_vel)  # Evitar 0 o negativo
    
    def esta_vivo(self):
        return self.vivo and self.hp_actual > 0
    
    def calcular_daño_base(self, objetivo):
        denominador = self.ataque + objetivo.defensa
        if denominador == 0: return 0

        daño_base = (self.ataque ** 2) / denominador
        return daño_base
    
    def realizar_ataque(self, objetivo, mod_elemental = 1.0, es_critico = False):
        daño_base = self.calcular_daño_base(objetivo)

        mod_critico = 2.0 if es_critico else 1.0
        daño_final = daño_base * mod_elemental * mod_critico

        variacion = r.uniform(0.9, 1.1) # variacion de +/- 10 %
        daño_final *= variacion

        return round(daño_final, 2)
    
    def recibir_daño(self, cantidad):
        self.hp_actual -= cantidad
        if self.hp_actual <= 0:
            self.hp_actual = 0
            self.vivo = False
            print(f"{self.nombre} ha sido derrotado")

    def actualizar_atb(self, d_time = 1):
        self.progreso_atb += self.velocidad * d_time
        if self.progreso_atb >= 100:
            return True # puede actuar
        return False
    
    def reset_atb(self):
        #reset manual del ATB (util al inicio de combate)
        self.progreso_atb = 0
    def __lt__(self, other):
        #Para ordenar por velocidad en "iniciativa"
        return self.velocidad() > other.velocidad()
    
    def __repr__(self):
        return f"{self.nombre}(V:{self.velocidad():.1f}, HP:{self.hp_actual:.0f}/{self.hp_max:.0f})"
    
    def __str__(self): # barra de vida 
        atb_bar = int(self.progreso_atb / 10)  # 0-10 barras
        barra = "█" * atb_bar + "░" * (10 - atb_bar)
        estado = "💀" if not self.vivo else "⚔️"
        return f"{estado} {self.nombre} | ATB:[{barra}] {self.progreso_atb:.0f}% | HP:{self.hp_actual:.0f}"

         
clock = pg.time.Clock()       
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
    if estado_partida == 0:#para la parte recien iniciado el programa
        pass
    elif estado_partida == 1: # corresponde a la creacion de personajes
        pass
    elif estado_partida == 2:# corresponde a mostrar el recorrido del mundo en el que te encuentres
        pass
    elif estado_partida == 3:# corresponde con un enfrentamiento/batalla
        dt = clock.get_time() / 1000.0
        if not enfrentamiento.activo:
            print("\n" + "="*40)
            print("  ⚔️  COMBATE INICIADO  ⚔️")
            print("="*40)
            entidad_actual = enfrentamiento.iniciar_combate(usar_atb=False)
        
        # mostar estado
        print(f"\n--- RONDA {enfrentamiento._jugadas} ---")
        print("TUS PERSONAJES:")
        for e in enfrentamiento.aliados:
            barra_hp = int((e.hp_actual/e.hp_max)*10)
            hp_vis = "█"*barra_hp + "░"*(10-barra_hp)
            vivo = "💀" if not e.esta_viva() else "⚔️"
            print(f"  {vivo} {e.nombre:12} HP:[{hp_vis}] {e.hp_actual:.0f}")
        
        print("ENEMIGOS:")
        for e in enfrentamiento.enemigos:
            barra_hp = int((e.hp_actual/e.hp_max)*10)
            hp_vis = "█"*barra_hp + "░"*(10-barra_hp)
            vivo = "💀" if not e.esta_viva() else "👹"
            print(f"  {vivo} {e.nombre:12} HP:[{hp_vis}] {e.hp_actual:.0f}")
        
        # procesar turno:
        if entidad_actual and entidad_actual.esta_viva():
            print(f"\n TURNO DE: {entidad_actual.nombre} ({entidad_actual.equipo}) <<<")
            
            # Si es enemigo -> IA automática
            if entidad_actual.equipo == "enemigo":
                print(f"{entidad_actual.nombre} ataca...")
                time.sleep(1)
                
                objetivos = enfrentamiento.obtener_objetivos(entidad_actual)
                if objetivos:
                    # atacar al que tenga menos HP
                    objetivo = min(objetivos, key=lambda x: x.hp_actual)
                    daño = entidad_actual.realizar_ataque(objetivo)
                    print(f"  ¡{objetivo.nombre} recibe {daño} de daño!")
                    time.sleep(1)
            
            # Si es jugador -> Input
            else:
                print("\n¿Qué harás?")
                print("1) Atacar")
                print("2) Usar habilidad (no implementado)")
                print("3) Usar objeto (no implementado)")
                print("4) Huir")
                
                opcion = input("> ").strip()
                
                if opcion == "1":
                    objetivos = enfrentamiento.obtener_objetivos(entidad_actual)
                    if not objetivos:
                        print("No hay objetivos...")
                        continue
                    
                    print("\nObjetivos:")
                    for i, obj in enumerate(objetivos, 1):
                        print(f"  {i}. {obj.nombre} (HP: {obj.hp_actual:.0f})")
                    
                    try:
                        sel = int(input("Elige objetivo: ")) - 1
                        if 0 <= sel < len(objetivos):
                            daño = entidad_actual.realizar_ataque(objetivos[sel])
                            print(f"\n ¡{daño} de daño a {objetivos[sel].nombre}!")
                            time.sleep(1)
                        else:
                            continue  # Turno inválido, repetir
                    except ValueError:
                        continue
                
                elif opcion == "4":
                    # Huir (30% de éxito)
                    if r.random() < 0.3:
                        print("\n  🏃 ¡Escapaste del combate!")
                        time.sleep(1)
                        partida = 2
                        break
                    else:
                        print("\n ¡No pudiste huir!")
                        time.sleep(1)
                
                else:
                    print("Opción no válida")
                    continue  # Repetir turno
        
        # Verificar si alguien murió este turno
        enfrentamiento._actualizar_lista_entidades()
        
        if not enfrentamiento.activo or enfrentamiento._verificar_fin_combate():
            if enfrentamiento.ganador == "jugadores":
                print("\n  ¡VICTORIA! ")
                # Aquí: dar experiencia, drops, etc.
            else:
                print("\n  DERROTA ")
                # Aquí: game over o volver al último checkpoint
            
            input("\nPresiona Enter para continuar...")
            partida = 2  # Volver al mapa
            break
        
        # Avanzar al siguiente turno
        enfrentamiento.finalizar_turno()
        entidad_actual = enfrentamiento.pequeTurno()
        
        # Si se acabó la ronda, nueva iniciativa
        if entidad_actual is None:
            if enfrentamiento.granTurno():
                entidad_actual = enfrentamiento.pequeTurno()
 
    elif estado_partida == 4:# corresponde con la tienda
        pass
    elif estado_partida == 5:# para cuando subes de nivel un personaje y tienes que escojer el ataque que puede aprender
        pass # este se puede eliminar para agregarlo al estado_partida = 1
    pg.display.update()
    clock.tick(60) #60 frame per sec (fps)
