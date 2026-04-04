import pygame as pg
import math as m
import random as r
from enum import Enum as e # para la clase animación, permite crearn grupos de constantes con nombre que son fáciles de leer y usar.

pg.init()
window = pg.display.set_mode((1000, 700))
estado_partida = 0 # para controlar que se va a mostrar por pantalla y tambien si estamos en combate o en tienda o cosas asi

#espacio variables:


# Paleta de colores: (se pueden cambiar)
GB_COLORS = {
    'white': (224, 248, 208),
    'light_gray': (136, 192, 112),
    'dark_gray': (52, 104, 86),
    'black': (8, 24, 32)
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
            raise IndexError('No se puede consultar una cola vacia')
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
            raise IndexError('No se puede eliminar un elementode una ola vacía')
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
                'callback': 'return_to_idle'  # Volver a idle al terminar
            },
            AnimationState.HURT: {
                'frames': [3, 0, 3, 0],  # Flash de daño
                'durations': [5, 5, 5, 5],
                'loop': False,
                'callback': 'return_to_idle'
            },
            AnimationState.FAINT: {
                'frames': [0, 1, 1, 1],  # Caída gradual
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
    def __init__(self, ej1, ej2, ej3, ej4, mapa_tablero, enemigos_mapa: list = None):#ej = entidad jugable
        self._jugadas = 0
        self.tablero = mapa_tablero # provisional hasta el tablero
        self.aliados = [ej1, ej2, ej3, ej4] #de momento se queda así, pero se puede modificar en el futuro
        self.enemigos = enemigos_mapa
        self.todas_entidades = list[Entidad] =[]
        self._actualizar_lista_entidades()
        # cola de turnos ordenada por velocidad:
        self.orden = ColaEnlazada() # cola ordenada en funcion de la velocidad
        self.entidad_actual = e.Optional[Entidad] = None
        # historial de turnos
        self.historial_turnos: list[dict] = []
        # estado de enfrentamiento:
        self.activo = False
        self.ganador = e.Optional[str] = None
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
class Batalla:
    def __init__(self, nombre, base_ataque, base_defensa, base_velocidad, nivel=1, es_boss = False):
        self.nombre = nombre
        self.nivel = nivel
        self.ataque = base_ataque + (2 * nivel) + m.log(nivel + 1)
        self.defensa = base_defensa + (1.5 * nivel) + m.log(nivel + 1)
        self.velocidad = base_velocidad + (0.5 * nivel) + m.log(nivel + 1)

        multiplicador_tpk = 20 if es_boss else 5
        self.hp_max = (self.ataque * multiplicador_tpk) + (5 * m.log(nivel + 1))
        self.hp_actual = self.hp_max

        self.progreso_atb = 0 # Acumulador para el sistema de velocidad
        self.vivo = True
    
    
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
       # for personaje in lista_combatientes:
           # if personaje.actualizar_atb(dt):
               # if personaje.es_jugador:
                 #   esperando_input_jugador = True
                   # personaje_actual = personaje
                   # daño = personaje.realizar_ataque(objetivo)
                  #  objetivo.recibir_daño(daño)
                  #  personaje.progreso_atb = 0
               # else:
                   # ejetucar_ia_enemigo(personaje)
                  #  personaje.progreso_atb = 0
 
    elif estado_partida == 4:# corresponde con la tienda
        pass
    elif estado_partida == 5:# para cuando subes de nivel un personaje y tienes que escojer el ataque que puede aprender
        pass # este se puede eliminar para agregarlo al estado_partida = 1
    pg.display.update()
    clock.tick(60) #60 frame per sec (fps)
    
