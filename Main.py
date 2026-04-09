import pygame as pg
import math as m
import random as r
from enum import Enum, auto
from dataclasses import dataclass, field
import time
from typing import Optional

pg.init()
window = pg.display.set_mode((1000, 700))
pg.display.set_caption("RPG Táctico - Demo")
estado_partida = 3  # Iniciar directamente en combate para probar

# paleta de colores: (se pueden cambiar)
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
    
    def __init__(self):
        self.front = None
        self.rear = None
        
    def empty(self):
        return self.front is None
        
    def first(self):
        if self.empty():
            raise IndexError('No se puede consultar una cola vacía')
        return self.front.dato
        
    def push(self, dato):
        nuevo = NodoCola(dato)
        if self.empty():
            self.front = nuevo
            self.rear = nuevo
        else:
            self.rear.siguiente = nuevo
            self.rear = nuevo
            
    def pop(self):
        if self.empty():
            raise IndexError('No se puede eliminar un elemento de una cola vacía')
        dato = self.front.dato
        self.front = self.front.siguiente
        
        if self.front is None:
            self.rear = None
        return dato
        
    def clear(self):
        self.front = None
        self.rear = None


class AnimationState(Enum):
    IDLE = auto()
    WALK = auto()
    ATTACK = auto()
    HURT = auto()
    FAINT = auto()
    SPECIAL = auto()


class tipo_Casilla(Enum):
    VACIA = auto()
    OBSTACULO = auto()
    PERSONAJE_JUGADOR = auto()
    PERSONAJE_ENEMIGO = auto()
    ZONA_MOVIMIENTO = auto()
    ZONA_ATAQUE = auto()
    SELECCIONADA = auto()
    MOVER = auto()


class Direccion(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)


@dataclass
class Casilla:
    fila: int
    col: int
    x: int
    y: int
    tamaño: int = 40
    tipo: tipo_Casilla = tipo_Casilla.VACIA
    entidad: Optional["Batalla"] = None
    obstaculo: bool = False
    distancia: int = 0
    visitada: bool = False
    padre: Optional[tuple[int, int]] = None
    
    def __post_init__(self):
        self.rect = pg.Rect(self.x, self.y, self.tamaño, self.tamaño)
        self.centro = (self.x + self.tamaño // 2, self.y + self.tamaño // 2)
        
    def color_casilla(self):
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


@dataclass
class AnimacionFrame:
    surface: pg.Surface
    duration: int
    offset: tuple[int, int] = (0, 0)


class spritesheets:
    def __init__(self, image_path: Optional[str] = None):
        self.sprite_size = 16
        self.sprites: list[pg.Surface] = []

        if image_path:
            self.load_from_file(image_path)
        else:
            self._create_placeholder_sprites()

    def _create_placeholder_sprites(self):
        sprite1 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite1.fill(GB_COLORS["white"])
        pg.draw.rect(sprite1, GB_COLORS["dark_gray"], (4, 4, 8, 8))
        pg.draw.rect(sprite1, GB_COLORS['black'], (5, 6, 2, 2))
        pg.draw.rect(sprite1, GB_COLORS['black'], (9, 6, 2, 2))
        self.sprites.append(sprite1)
        
        sprite2 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite2.fill(GB_COLORS['white'])
        pg.draw.rect(sprite2, GB_COLORS['dark_gray'], (4, 5, 8, 7))
        pg.draw.line(sprite2, GB_COLORS['black'], (5, 7), (6, 7))
        pg.draw.line(sprite2, GB_COLORS['black'], (9, 7), (10, 7))
        self.sprites.append(sprite2)
        
        sprite3 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite3.fill(GB_COLORS['white'])
        pg.draw.rect(sprite3, GB_COLORS['dark_gray'], (4, 4, 8, 8))
        pg.draw.rect(sprite3, GB_COLORS['black'], (5, 6, 2, 2))
        pg.draw.rect(sprite3, GB_COLORS['black'], (9, 6, 2, 2))
        pg.draw.rect(sprite3, GB_COLORS['black'], (6, 10, 4, 2))
        self.sprites.append(sprite3)
        
        sprite4 = pg.Surface((self.sprite_size, self.sprite_size))
        sprite4.fill(GB_COLORS['white'])
        pg.draw.rect(sprite4, GB_COLORS['light_gray'], (4, 4, 8, 8))
        pg.draw.rect(sprite4, GB_COLORS['white'], (5, 6, 2, 2))
        pg.draw.rect(sprite4, GB_COLORS['white'], (9, 6, 2, 2))
        self.sprites.append(sprite4)
    
    def get_sprite(self, index: int):
        return self.sprites[index % len(self.sprites)]
    
    def scale_sprite(self, sprite: pg.Surface, scale: int):
        size = sprite.get_size()
        return pg.transform.scale(sprite, (size[0] * scale, size[1] * scale))


class EjecAnimacion:
    def __init__(self, sprite_sheet: spritesheets):
        self.sprite_sheet = sprite_sheet
        self.current_state = AnimationState.IDLE
        self.frame_index = 0
        self.animation_timer = 0
        self.facing_right = True
        
        self.animations = {
            AnimationState.IDLE: {
                'frames': [0, 1],
                'durations': [30, 5],
                'loop': True
            },
            AnimationState.WALK: {
                'frames': [0, 1],
                'durations': [8, 8],
                'loop': True
            },
            AnimationState.ATTACK: {
                'frames': [2, 0],
                'durations': [10, 10],
                'loop': False,
                'callback': 'return_to_idle'
            },
            AnimationState.HURT: {
                'frames': [3, 0, 3, 0],
                'durations': [5, 5, 5, 5],
                'loop': False,
                'callback': 'return_to_idle'
            },
            AnimationState.FAINT: {
                'frames': [0, 1, 1, 1],
                'durations': [10, 10, 10, 999],
                'loop': False
            }
        }
        
        self.shake_offset = (0, 0)
        self.shake_intensity = 0
        self.blink = False
    
    def set_state(self, state: AnimationState):
        if state != self.current_state:
            self.current_state = state
            self.frame_index = 0
            self.animation_timer = 0
            self.shake_intensity = 0
    
    def update(self):
        anim_config = self.animations[self.current_state]
        current_frame_duration = anim_config['durations'][self.frame_index]
        
        self.animation_timer += 1
        
        if self.shake_intensity > 0:
            import random
            self.shake_offset = (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity)
            )
            self.shake_intensity = max(0, self.shake_intensity - 1)
        
        if self.animation_timer >= current_frame_duration:
            self.animation_timer = 0
            self.frame_index += 1
            
            if self.frame_index >= len(anim_config['frames']):
                if anim_config.get('loop', True):
                    self.frame_index = 0
                else:
                    self.frame_index = len(anim_config['frames']) - 1
                    if 'callback' in anim_config:
                        if anim_config['callback'] == 'return_to_idle':
                            self.set_state(AnimationState.IDLE)


class TipoTerreno(Enum):
    TIERRA = auto()
    HIERBA_ALTA = auto()
    HIERBA_SECA = auto()
    AGUA = auto()
    LAVA = auto()
    PIEDRA_CALIENTE = auto()
    HIELO = auto()
    ACIDO = auto()


class Elemento(Enum):
    NEUTRO = auto()
    FUEGO = auto()
    AGUA = auto()
    ELECTRICO = auto()
    HIELO = auto()
    VENENO = auto()


@dataclass
class ModificadorElemental:
    potenciacion: float = 1.0
    probabilidad_efecto: float = 0.0
    daño_por_turno: int = 0
    turnos_estado: int = 0


@dataclass
class EfectoTerreno:
    nombre: str
    descripcion: str
    caminable: bool = True
    modificadores: dict[Elemento, ModificadorElemental] = field(default_factory=dict)
    interacciones: dict[TipoTerreno, callable] = field(default_factory=dict)
    probabilidad_evento: float = 0.0
    requiere_objeto: Optional[str] = None
    
    def obtener_modificador(self, elemento: Elemento) -> ModificadorElemental:
        return self.modificadores.get(elemento, ModificadorElemental())


class EfectosTerrenoFactory:
    @staticmethod
    def crear_tierra() -> EfectoTerreno:
        return EfectoTerreno(
            nombre="Tierra",
            descripcion="Terreno normal sin efectos ni consecuencias especiales",
            caminable=True,
            modificadores={}
        )

@dataclass
class Entidad:
    id: int
    nombre: str
    velocidad_base: int
    hp: int = 100
    max_hp: int = 100
    equipo: str = "neutral"
    x: int = 0
    y: int = 0
    estados: list = field(default_factory=list)
    modificadores_vel: int = 0
    
    def velocidad(self): 
        return max(0, self.velocidad_base + self.modificadores_vel)
        
    def esta_vivo(self):
        return self.hp > 0
        
    def __lt__(self, other):
        return self.velocidad() > other.velocidad() 
        
    def __repr__(self):
        return f"{self.nombre}(Vel:{self.velocidad()}, HP:{self.hp})"
class Batalla:
    _id_counter = 0
    
    def __init__(self, nombre, base_ataque, base_defensa, base_velocidad, nivel=1, es_boss=False, equipo=None):
        Batalla._id_counter += 1
        self.id = Batalla._id_counter
        self.nombre = nombre
        self.nivel = nivel
        self.equipo = equipo
        self.velocidad_base = base_velocidad
        self.ataque = base_ataque + (2 * nivel) + m.log(nivel + 1)
        self.defensa = base_defensa + (1.5 * nivel) + m.log(nivel + 1)


        multiplicador_tpk = 20 if es_boss else 5
        self.hp_max = (self.ataque * multiplicador_tpk) + (5 * m.log(nivel + 1))
        self.hp_actual = self.hp_max

        self.x = 0
        self.y = 0

        self.progreso_atb = 0
        self.vivo = True
        self.estados = []
        self.modificadores_vel = 0
        
    def velocidad(self):
        return max(0.1, self.velocidad_base + (0.5 * self.nivel) + m.log(self.nivel + 1) + self.modificadores_vel)
    
    
    def esta_vivo(self):
        return self.vivo and self.hp_actual > 0
    
    def calcular_daño_base(self, objetivo):
        denominador = self.ataque + objetivo.defensa
        if denominador == 0:
            return 0
        daño_base = (self.ataque ** 2) / denominador
        return daño_base
    
    def realizar_ataque(self, objetivo, mod_elemental=1.0, es_critico=False):
        daño_base = self.calcular_daño_base(objetivo)
        mod_critico = 2.0 if es_critico else 1.0
        daño_final = daño_base * mod_elemental * mod_critico
        variacion = r.uniform(0.9, 1.1)
        daño_final *= variacion
        return round(daño_final, 2)
    
    def recibir_daño(self, cantidad):
        self.hp_actual -= cantidad
        if self.hp_actual <= 0:
            self.hp_actual = 0
            self.vivo = False
            print(f"{self.nombre} ha sido derrotado")
    
    def actualizar_atb(self, d_time=1):
        self.progreso_atb += self.velocidad() * d_time
        if self.progreso_atb >= 100:
            return True
        return False
    
    def reset_atb(self):
        self.progreso_atb = 0
        
    def __lt__(self, other):
        return self.velocidad() > other.velocidad()
    
    def __repr__(self):
        return f"{self.nombre}(V:{self.velocidad():.1f}, HP:{self.hp_actual:.0f}/{self.hp_max:.0f})"
    
    def __str__(self):
        atb_bar = int(self.progreso_atb / 10)
        barra = "█" * atb_bar + "░" * (10 - atb_bar)
        estado = "💀" if not self.vivo else "⚔️"
        return f"{estado} {self.nombre} | ATB:[{barra}] {self.progreso_atb:.0f}% | HP:{self.hp_actual:.0f}"


class enfrentamiento:
    def __init__(self, jugadores: list, mapa_tablero=None, enemigos: list = None):
        self._jugadas = 0
        self.tablero = mapa_tablero
        self.aliados = jugadores if jugadores else []
        self.enemigos = enemigos if enemigos else []
        self.todas_entidades = []
        self._actualizar_lista_entidades()
        self.orden = ColaEnlazada()
        self.entidad_actual = None
        self.historial_turnos = []
        self.activo = False
        self.ganador = None
        self.usar_atb = False
        
    def _actualizar_lista_entidades(self):
        self.todas_entidades = []
        for e in self.aliados + self.enemigos:
            if e.esta_vivo():
                self.todas_entidades.append(e)
                
    def calcular_orden(self):
        participantes = [e for e in self.todas_entidades if e.esta_vivo()]
        ordenados = sorted(participantes, key=lambda e: (-e.velocidad(), e.id))
        return ordenados
        
    def granTurno(self):
        self._actualizar_lista_entidades()
        if self._verificar_fin_combate():
            return False
        orden_iniciativa = self.calcular_orden()
        self.orden.clear()
        for entidad in orden_iniciativa:
            self.orden.push(entidad)
        self._jugadas += 1
        print(f"\\n RONDA {self._jugadas} ")
        print(f"Orden de iniciativa: {[e.nombre for e in orden_iniciativa]}")
        return True
        
    def pequeTurno(self):
        if self.orden.empty():
            return None
        self.entidad_actual = self.orden.pop()
        if not self.entidad_actual.esta_vivo():
            return self.pequeTurno()
        self.historial_turnos.append({
            "Ronda": self._jugadas,
            "Entidad": self.entidad_actual.nombre,
            "Equipo": self.entidad_actual.equipo
        })
        print(f"\\n -> Turno de: {self.entidad_actual.nombre} ({self.entidad_actual.equipo}) <<<")
        return self.entidad_actual
        
    def iniciar_combate(self, usar_atb=False):
        self.usar_atb = usar_atb
        self.activo = True
        for e in self.todas_entidades:
            e.reset_atb()
        if not usar_atb:
            self.granTurno()
            return self.pequeTurno()
        return None
        
    def finalizar_turno(self, acciones_realizadas=None):
        if self.entidad_actual:
            self.entidad_actual.reset_atb()
        if acciones_realizadas:
            self.historial_turnos[-1].update(acciones_realizadas)
        if not self.usar_atb and self.orden.empty():
            return self.granTurno()
        return True
        
    def _verificar_fin_combate(self) -> bool:
        aliados_vivos = any(e.esta_vivo() for e in self.aliados)
        enemigos_vivos = any(e.esta_vivo() for e in self.enemigos)
        
        if not aliados_vivos:
            self.ganador = "enemigos"
            self.activo = False
            print("¡Derrota! Todos los aliados han caído.")
            return True
            
        if not enemigos_vivos:
            self.ganador = "jugadores"
            self.activo = False
            print("¡Victoria! Todos los enemigos han sido derrotados.")
            return True
            
        return False
        
    def obtener_objetivos_validos(self, atacante=None):
        atacante = atacante or self.entidad_actual
        if not atacante:
            return []
        if atacante.equipo == "enemigo":
            return [e for e in self.aliados if e.esta_vivo()]
        return [e for e in self.enemigos if e.esta_vivo()]


# INICIALIZAR ENTIDADES DE PRUEBA
jugador1 = Batalla("Héroe", base_ataque=15, base_defensa=10, base_velocidad=12, nivel=1, equipo="jugador")
jugador2 = Batalla("Maga", base_ataque=20, base_defensa=5, base_velocidad=10, nivel=1, equipo="jugador")

enemigo1 = Batalla("Goblin", base_ataque=12, base_defensa=8, base_velocidad=8, nivel=1, equipo="enemigo")
enemigo2 = Batalla("Orco", base_ataque=18, base_defensa=12, base_velocidad=6, nivel=1, equipo="enemigo")

aliados = [jugador1, jugador2]
enemigos = [enemigo1, enemigo2]

enfrentamiento = enfrentamiento(aliados, None, enemigos)
entidad_actual = None

# FUENTE PARA TEXTO
font = pg.font.SysFont("consolas", 20)
clock = pg.time.Clock()

# BUCLE PRINCIPAL
running = True
while running:
    dt = clock.get_time() / 1000.0
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            # Controles simples para probar
            elif event.key == pg.K_1 and estado_partida == 3:
                # Atacar automáticamente con el jugador actual
                if entidad_actual and entidad_actual.equipo == "jugador":
                    objetivos = enfrentamiento.obtener_objetivos_validos(entidad_actual)
                    if objetivos:
                        objetivo = objetivos[0]
                        daño = entidad_actual.realizar_ataque(objetivo)
                        objetivo.recibir_daño(daño)
                        print(f"¡{entidad_actual.nombre} hace {daño:.1f} daño a {objetivo.nombre}!")
                        
                        enfrentamiento._actualizar_lista_entidades()
                        if enfrentamiento._verificar_fin_combate():
                            pass
                        else:
                            enfrentamiento.finalizar_turno()
                            entidad_actual = enfrentamiento.pequeTurno()
                            if entidad_actual is None:
                                if enfrentamiento.granTurno():
                                    entidad_actual = enfrentamiento.pequeTurno()
    
    # LÓGICA DEL JUEGO
    if estado_partida == 3:
        if not enfrentamiento.activo:
            print("="*40)
            print("  ⚔️  COMBATE INICIADO  ⚔️")
            print("="*40)
            entidad_actual = enfrentamiento.iniciar_combate(usar_atb=False)
        if entidad_actual and entidad_actual.esta_vivo() and entidad_actual.equipo == "enemigo":
            pg.time.delay(500)  # Pequeña pausa para ver la acción
            objetivos = enfrentamiento.obtener_objetivos_validos(entidad_actual)
            if objetivos:
                objetivo = min(objetivos, key=lambda x: x.hp_actual)
                daño = entidad_actual.realizar_ataque(objetivo)
                objetivo.recibir_daño(daño)
                print(f"¡{entidad_actual.nombre} hace {daño:.1f} daño a {objetivo.nombre}!")
                
                enfrentamiento._actualizar_lista_entidades()
                if not enfrentamiento._verificar_fin_combate():
                    enfrentamiento.finalizar_turno()
                    entidad_actual = enfrentamiento.pequeTurno()
                    if entidad_actual is None:
                        if enfrentamiento.granTurno():
                            entidad_actual = enfrentamiento.pequeTurno()
    
    # DIBUJAR
    window.fill(GB_COLORS['black'])
    
    if estado_partida == 3:
        # Dibujar estado del combate
        y_offset = 50
        
        titulo = font.render(f"RONDA {enfrentamiento._jugadas}", True, GB_COLORS['white'])
        window.blit(titulo, (50, y_offset))
        y_offset += 40
        
        # Aliados
        aliados_text = font.render("TUS PERSONAJES:", True, GB_COLORS['green_bright'])
        window.blit(aliados_text, (50, y_offset))
        y_offset += 30
        
        for e in enfrentamiento.aliados:
            barra_hp = int((e.hp_actual/e.hp_max)*10) if e.hp_max > 0 else 0
            hp_vis = "█"*barra_hp + "░"*(10-barra_hp)
            vivo = "💀" if not e.esta_vivo() else "⚔️"
            text = font.render(f"{vivo} {e.nombre:12} HP:[{hp_vis}] {e.hp_actual:.0f}/{e.hp_max:.0f}", True, GB_COLORS['white'])
            window.blit(text, (70, y_offset))
            y_offset += 25
        
        y_offset += 20
        enemigos_text = font.render("ENEMIGOS:", True, GB_COLORS['red_bright'])
        window.blit(enemigos_text, (50, y_offset))
        y_offset += 30
        
        for e in enfrentamiento.enemigos:
            barra_hp = int((e.hp_actual/e.hp_max)*10) if e.hp_max > 0 else 0
            hp_vis = "█"*barra_hp + "░"*(10-barra_hp)
            vivo = "💀" if not e.esta_vivo() else "👹"
            text = font.render(f"{vivo} {e.nombre:12} HP:[{hp_vis}] {e.hp_actual:.0f}/{e.hp_max:.0f}", True, GB_COLORS['white'])
            window.blit(text, (70, y_offset))
            y_offset += 25
        
        # Turno actual
        y_offset += 30
        if entidad_actual:
            turno_text = font.render(f"TURNO DE: {entidad_actual.nombre} ({entidad_actual.equipo})", True, GB_COLORS['yellow_bright'])
            window.blit(turno_text, (50, y_offset))
            
            if entidad_actual.equipo == "jugador" and entidad_actual.esta_vivo():
                y_offset += 30
                instruccion = font.render("Pulsa [1] para atacar al primer enemigo", True, GB_COLORS['light_gray'])
                window.blit(instruccion, (50, y_offset))
        
        if not enfrentamiento.activo and enfrentamiento.ganador:
            y_offset += 60
            if enfrentamiento.ganador == "jugadores":
                resultado = font.render("¡VICTORIA! Pulsa ESC para salir", True, GB_COLORS['green_bright'])
            else:
                resultado = font.render("DERROTA... Pulsa ESC para salir", True, GB_COLORS['red_bright'])
            window.blit(resultado, (50, y_offset))
    
    pg.display.update()
    clock.tick(60)

pg.quit()

