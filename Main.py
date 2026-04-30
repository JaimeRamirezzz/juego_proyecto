import pygame as pg
import math as m
import random as r
#from enum import Enum, auto
from dataclasses import dataclass, field
#import time
#from typing import Optional
from personajes.caballero import Caballero
from personajes.tanque import Tanque
from personajes.arquero import Arquero

altura_ventana = 700
anchura_ventana = 1000

pg.init()
window = pg.display.set_mode((anchura_ventana, altura_ventana))
pg.display.set_caption("RPG Táctico - Demo")
estado_partida = 0  # Iniciar en pantalla de inicio

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

class Ataque:
    def __init__(self, potencia, nombre, grupo_ataque, descripcion):
        self._potencia = potencia
        self._nombre = nombre
        self._grupo_ataque = grupo_ataque
        self._descripcion = descripcion
    def nombre(self):
        return self._nombre
    def potencia(self):
        return self._potencia
    def grupo_ataque(self):
        return self._grupo_ataque
    def descripcion(self):
        return self._descripcion
    
    def atacar(self, personaje, enemigo):#Cuando esten definidos tanto los personajes como los enemigos, podre sacar sus estadisticas para poder enviar el daño
        pass
#Ataques para la creacion de personajes, no se que vamos ha hacer para crear tantos ataques si metemos muchos
#se me ocurre sacar la clase del main(y guardarla en otro archivo) y luego exportarla dentro del main, para despues definir todos los ataques dentro del main
Flecha_precisa = Ataque(25, 'Flecha precisa', 'arquero', 'Disparo de una flecha con la máxima tensión del arco que causa un gran daño, siempre acierta en lugares vulnerables, de ahí su gran daño')
Espadazo = Ataque(20, 'Espadazo', 'caballero', 'Ataque sencillo y preciso con la espada, que produce un gran daño')
Martillazo = Ataque(15, 'Martillazo', 'Tanque', 'Potente ataque descendente con un martillo pesado')


class NodoCola:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
    
class ColaEnlazada:
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


class enfrentamiento:
    def __init__(self, jugadores: list, mapa_tablero=None):
        self._jugadas = 0
        self.tablero = mapa_tablero
        self.aliados = jugadores
        self.enemigos = mapa_tablero.lista_enemigos()
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

# FUENTE PARA TEXTO
font = pg.font.SysFont("consolas", 20)
clock = pg.time.Clock()

# Para mostrar la pantalla de inicio
def pantalla_inicio():
    window.blit(font.render("Bienvenido al juego", True, GB_COLORS["white"]), (380, 200))
    window.blit(font.render("Pulse espacio para pasar a la creacion de personaje", True, GB_COLORS["white"]), (200, 600))

# Para mostrar la pantalla de creacion de personajes, esta hecha de forma temporal para ser modificada si la quieres cambiar hazlo, no tengas miedo
def pantalla_creacion_de_personajes():
    window.blit(font.render("Creación de personajes", True, GB_COLORS["white"]), (380, 200))
    window.blit(font.render("Pulsa espacio para pasar a la batalla", True, GB_COLORS["white"]), (200, 600))

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
            elif event.key == pg.K_SPACE:
                if estado_partida == 0 or estado_partida == 1:
                    estado_partida += 1
    
    # LÓGICA DEL JUEGO
    if estado_partida == 0:#corresponde con la pantalla de inicio
        pass
    elif estado_partida == 1:# corresponde con la creacion de personajes
        pass
    elif estado_partida ==2:# la animacion que no se si quitar
        estado_partida = 3
    elif estado_partida == 3:
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
    
    if estado_partida == 0:
        pantalla_inicio()
    elif estado_partida == 1:
        pantalla_creacion_de_personajes()
    elif estado_partida == 2:
        pass
    elif estado_partida == 3:
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

#CLASES JUGADORES
jugador1 = Caballero("Caballero")
jugador2 = Tanque("Tanque")
jugador3 = Arquero("Arquero")

aliados = [jugador1, jugador2, jugador3]