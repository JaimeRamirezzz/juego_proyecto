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
