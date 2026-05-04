from enum import Enum, auto 
import random as r
class TipoBioma(Enum):
    AGUA_PROFUNDA = auto()
    PRADERA = auto()
    BOSQUE = auto()
    MONTAÑA = auto()
    NIEVE = auto()
    LAVA = auto()
    PANTANO = auto()
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

    def __post_init__(self):
        if self.semilla is None:
            self.semilla = r.randint(0, 100000)


class GeneradorMapaProcedural:
    def __init__(self, config: Configuracionmapa = None):
        self.config = config or Configuracionmapa()
        self.ancho = 0
        self.alto = 0
        self.grid_altura = []
        self.grid_humedad = []
        self.grid_temperatura = []
        self._noise_gen = opensimplex.OpenSimplex(seed=self.config.semilla)

    def generar_mapa(self, ancho: int, alto: int):
        self.ancho = ancho
        self.alto = alto

        self.grid_altura = [[0.0 for _ in range(ancho)] for _ in range(alto)]
        self.grid_humedad = [[0.0 for _ in range(ancho)] for _ in range(alto)]
        self.grid_temperatura = [[0.0 for _ in range(ancho)] for _ in range(alto)]
        biomas = [[TipoBioma.PRADERA for _ in range(ancho)] for _ in range(alto)]

        for y in range(alto):
            for x in range(ancho):
                altura = 0.0
                amplitud = 1.0
                frecuencia = 1.0
                for _ in range(self.config.octavas):
                    altura += amplitud * self._noise_gen.noise2(
                        (x * frecuencia) / self.config.escala,
                        (y * frecuencia) / self.config.escala
                    )
                    amplitud *= self.config.persistencia
                    frecuencia *= self.config.lacunaridad

                altura = altura / (2 - self.config.persistencia)

                detalle = self._noise_gen.noise2(
                    (x + 1000) / self.config.escala,
                    (y + 1000) / self.config.escala
                ) * 0.3
                altura_final = altura + detalle

                humedad = self._noise_gen.noise2(
                    (x + 5000) / self.config.escala,
                    (y + 5000) / self.config.escala
                )

                temp_base = 1.0 - (y / alto) * 2
                temp_noise = self._noise_gen.noise2(
                    (x + 10000) / self.config.escala,
                    (y + 10000) / self.config.escala
                ) * 0.4
                temperatura = temp_base + temp_noise

                self.grid_altura[y][x] = altura_final
                self.grid_humedad[y][x] = humedad
                self.grid_temperatura[y][x] = temperatura
                biomas[y][x] = self._determinar_bioma(altura_final, humedad, temperatura)

        biomas = self._suavizar_biomas(biomas)
        return biomas

    def _determinar_bioma(self, altura, humedad, temperatura):
        cfg = self.config
        if altura < cfg.nivel_agua_profunda:
            return TipoBioma.AGUA_PROFUNDA
        elif altura > cfg.nivel_montaña:
            if temperatura < -0.3:
                return TipoBioma.NIEVE
            return TipoBioma.MONTAÑA
        if humedad > 0.6 and temperatura > 0.0:
            if altura < cfg.nivel_pradera:
                return TipoBioma.PANTANO
            return TipoBioma.BOSQUE
        if humedad > 0.3 and altura > cfg.nivel_pradera:
            return TipoBioma.BOSQUE
        return TipoBioma.PRADERA

    def _suavizar_biomas(self, biomas):
        resultado = [fila[:] for fila in biomas]
        for y in range(1, self.alto - 1):
            for x in range(1, self.ancho - 1):
                actual = biomas[y][x]
                vecinos = [biomas[y-1][x], biomas[y+1][x], biomas[y][x-1], biomas[y][x+1]]
                if all(v != actual for v in vecinos):
                    if actual == TipoBioma.AGUA_PROFUNDA:
                        resultado[y][x] = TipoBioma.AGUA_PROFUNDA
                    else:
                        resultado[y][x] = max(set(vecinos), key=vecinos.count)
        return resultado

    def obtener_altura(self, x: int, y: int) -> float:
        if 0 <= y < self.alto and 0 <= x < self.ancho:
            return self.grid_altura[y][x]
        return 0.0


class MapaTactico:
    COLORES_BIOMA = {
        TipoBioma.AGUA_PROFUNDA: (20, 40, 80),
        TipoBioma.PRADERA: (120, 180, 80),
        TipoBioma.BOSQUE: (40, 100, 40),
        TipoBioma.MONTAÑA: (80, 80, 90),
        TipoBioma.NIEVE: (240, 250, 255),
        TipoBioma.LAVA: (200, 60, 20),
        TipoBioma.PANTANO: (100, 140, 100),
    }

    PROPIEDADES = {
        TipoBioma.AGUA_PROFUNDA: {'caminable': False, 'costo': 99},
        TipoBioma.PRADERA: {'caminable': True, 'costo': 100.0},
        TipoBioma.BOSQUE: {'caminable': True, 'costo': 1.5, 'cobertura': 20},
        TipoBioma.MONTAÑA: {'caminable': False, 'costo': 99},
        TipoBioma.NIEVE: {'caminable': True, 'costo': 2.5, 'resbaladizo': True},
        TipoBioma.LAVA: {'caminable': False, 'costo': 99, 'daño': 20},
        TipoBioma.PANTANO: {'caminable': True, 'costo': 3.0, 'veneno': 0.1},
    }

    def __init__(self, ancho: int, alto: int, tamaño_casilla: int = 40):
        self.ancho = ancho
        self.alto = alto
        self.tamaño_casilla = tamaño_casilla
        self.generador = GeneradorMapaProcedural()
        self.biomas = self.generador.generar_mapa(ancho, alto)
        self.casillas = []
        self._crear_casillas()
        self.entidades_posiciones = {}

    def _crear_casillas(self):
        for y in range(self.alto):
            fila = []
            for x in range(self.ancho):
                px = x * self.tamaño_casilla
                py = y * self.tamaño_casilla
                bioma = self.biomas[y][x]
                props = self.PROPIEDADES[bioma]
                casilla = Casilla(
                    fila=y, col=x, x=px, y=py,
                    tamaño=self.tamaño_casilla,
                    tipo=tipo_Casilla.OBSTACULO if not props['caminable'] else tipo_Casilla.VACIA,
                    obstaculo=not props['caminable']
                )
                casilla.bioma = bioma
                casilla.costo_movimiento = props['costo']
                casilla.cobertura = props.get('cobertura', 0)
                casilla.ventaja_altura = props.get('ventaja_altura', False)
                casilla.resbaladizo = props.get('resbaladizo', False)
                casilla.daño_terreno = props.get('daño', 0)
                casilla.prob_veneno = props.get('veneno', 0.0)
                fila.append(casilla)
            self.casillas.append(fila)

    def obtener_casilla(self, x: int, y: int) -> Optional[Casilla]:
        if 0 <= y < self.alto and 0 <= x < self.ancho:
            return self.casillas[y][x]
        return None

    def es_caminable(self, x: int, y: int) -> bool:
        casilla = self.obtener_casilla(x, y)
        return casilla is not None and not casilla.obstaculo

    def colocar_entidad(self, entidad, x: int, y: int) -> bool:
        casilla = self.obtener_casilla(x, y)
        if not casilla or casilla.obstaculo or casilla.entidad is not None:
            return False
        if hasattr(entidad, 'id') and entidad.id in self.entidades_posiciones:
            old_x, old_y = self.entidades_posiciones[entidad.id]
            old_casilla = self.obtener_casilla(old_x, old_y)
            if old_casilla:
                old_casilla.entidad = None
                old_casilla.tipo = tipo_Casilla.VACIA
        casilla.entidad = entidad
        casilla.tipo = (tipo_Casilla.PERSONAJE_JUGADOR
                        if getattr(entidad, 'equipo', None) == 'jugador'
                        else tipo_Casilla.PERSONAJE_ENEMIGO)
        entidad.x = x
        entidad.y = y
        self.entidades_posiciones[getattr(entidad, 'id', id(entidad))] = (x, y)
        return True

    def mover_entidad(self, entidad, nuevo_x: int, nuevo_y: int) -> bool:
        if not self.es_caminable(nuevo_x, nuevo_y):
            return False
        casilla_destino = self.obtener_casilla(nuevo_x, nuevo_y)
        if casilla_destino.entidad is not None:
            return False
        casilla_origen = self.obtener_casilla(entidad.x, entidad.y)
        if casilla_origen:
            casilla_origen.entidad = None
            casilla_origen.tipo = tipo_Casilla.VACIA
        return self.colocar_entidad(entidad, nuevo_x, nuevo_y)

    def calcular_alcance_movimiento(self, x_origen, y_origen, puntos_mov):
        from heapq import heappush, heappop
        inicio = self.obtener_casilla(x_origen, y_origen)
        if not inicio:
            return []
        frontera = [(0.0, x_origen, y_origen)]
        costos = {(x_origen, y_origen): 0.0}
        visitados = set()
        alcanzables = []
        direcciones = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        while frontera:
            costo, x, y = heappop(frontera)
            if (x, y) in visitados:
                continue
            visitados.add((x, y))
            casilla = self.obtener_casilla(x, y)
            if casilla and casilla != inicio:
                alcanzables.append(casilla)
                casilla.tipo = tipo_Casilla.ZONA_MOVIMIENTO
            for dx, dy in direcciones:
                nx, ny = x + dx, y + dy
                vecina = self.obtener_casilla(nx, ny)
                if not vecina or vecina.obstaculo or vecina.entidad is not None:
                    continue
                mult = 1.4 if dx != 0 and dy != 0 else 1.0
                nuevo_costo = costo + (vecina.costo_movimiento * mult)
                if nuevo_costo <= puntos_mov and nuevo_costo < costos.get((nx, ny), float('inf')):
                    costos[(nx, ny)] = nuevo_costo
                    heappush(frontera, (nuevo_costo, nx, ny))
        return alcanzables

    def limpiar_zonas(self):
        for fila in self.casillas:
            for casilla in fila:
                if casilla.tipo in (tipo_Casilla.ZONA_MOVIMIENTO, tipo_Casilla.ZONA_ATAQUE):
                    casilla.tipo = tipo_Casilla.OBSTACULO if casilla.obstaculo else tipo_Casilla.VACIA

    def dibujar(self, superficie, offset_x=0, offset_y=0, modo_exploracion=False):
        for fila in self.casillas:
            for casilla in fila:
                if casilla.tipo in (tipo_Casilla.ZONA_MOVIMIENTO, tipo_Casilla.ZONA_ATAQUE,
                                    tipo_Casilla.SELECCIONADA, tipo_Casilla.PERSONAJE_JUGADOR,
                                    tipo_Casilla.PERSONAJE_ENEMIGO):
                    color = casilla.color_casilla()
                else:
                    color = self.COLORES_BIOMA.get(casilla.bioma, (200, 200, 200))
                rect = pg.Rect(
                    casilla.x + offset_x,
                    casilla.y + offset_y,
                    self.tamaño_casilla - (0 if modo_exploracion else 1),
                    self.tamaño_casilla - (0 if modo_exploracion else 1)
                )
                pg.draw.rect(superficie, color, rect)
                if not modo_exploracion:
                    altura = self.generador.obtener_altura(casilla.col, casilla.fila)
                    if altura > 0.5:
                        sombra = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
                        sombra.fill((0, 0, 0, int(altura * 40)))
                        superficie.blit(sombra, rect)
                if casilla.obstaculo and not modo_exploracion:
                    pg.draw.rect(superficie, (30, 30, 30), rect, 2)


class TipoTerreno(Enum):
    TIERRA = auto()
    HIERBA_ALTA = auto()
    HIERBA_SECA = auto()
    AGUA = auto()
    LAVA = auto()
    PIEDRA_CALIENTE = auto()
    HIELO = auto()
    ACIDO = auto()