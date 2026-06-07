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
from personajes.creacion_personaje_ui import PantallaCreacionPersonajes
from personajes.subida_nivel_ui import PantallaRecompensa
from primera_mapa.mapa_juego.mapa import MapaProcedural
from Clase_Enemigo import Enemy
from config import ANCHO_PANTALLA, ALTO_PANTALLA, ALTO_PANEL, ALTO_MAPA, ANCHO_CASILLAS, ALTO_CASILLAS, TAMANO_CASILLA

pg.init()
pg.key.set_repeat(0)
window = pg.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
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

from panel_ataques import PanelAtaques

class Enfrentamiento:
    def __init__(self, jugadores: list):
        print(1)
        self._jugadas = 0
        self.tablero = MapaProcedural(8, 8)
        print(2)
        self.aliados = jugadores
        for i in self.aliados:
            print(i.nombre)
        print(3)
        self.enemigos = self.tablero.enemigos
        print(4)
        self.orden = ColaEnlazada()
        self.todas_entidades = []
        self._actualizar_lista_entidades()
        print(5)
        self.entidad_actual = None
        self.historial_turnos = []
        self.activo = False
        self.ganador = None
        self.usar_atb = False
        self.panel_ui = PanelAtaques(0, 350, 800, 250)
        print(6)
        for i in self.aliados:
            self.tablero.colocar_jugador(i)
        self.paso_de_ronda()
        print(7)
        
    def _actualizar_lista_entidades(self):
        self.todas_entidades = []
        for e in self.aliados + self.enemigos:
            if e.esta_vivo():
                self.todas_entidades.append(e)
        if self.orden.empty():
            for i in self.calcular_orden():
                self.orden.push(i)
                
    def calcular_orden(self):
        ordenados = sorted(self.todas_entidades, key=lambda e: (-e.velocidad(), e.id))
        return ordenados
        
    def paso_de_ronda(self):##paso de ronda
        self._actualizar_lista_entidades()
        if self._verificar_fin_combate():
            return False
        
        self._jugadas += 1
        self.entidad_actual = self.orden.pop()
        
    def paso_de_turno(self):#Solo hace el cambio de turno
        if self.orden.empty():
            self.paso_de_ronda()
            return None
        self.entidad_actual = self.orden.pop()
        if self.entidad_actual.equipo == "jugador":
            self.entidad_actual.recuperacion_por_turnos()
       
        self.panel_ui.actualizar_jugador(self.entidad_actual)
        
        self.historial_turnos.append({
            "Ronda": self._jugadas,
            "Entidad": self.entidad_actual.nombre,
            "Equipo": self.entidad_actual.equipo
        })
        
    def ataque_real(self, indice, destino):#lo de real es para diferenciarlo de todo ataque existente, y lo de destino es a donde termina, porque el origen ya lo tendremos que es el self.activo o algo asi, me da pereza vuscar como estaba llamada el personaje que le toca atacar
        if type(self.entidad_actual) == Arquero:
            if self.entidad_actual.atacar(indice):
                self.tablero.casillas(destino).entidad.recivir_daño(self.entidad_actual.ataques[indice].potencia()*self.entidad_actual.ataque)
            else:
                pass
        else:# por si da tiempo, para hacer que el resto de personajes solo ataquen a una distancia realista
            if self.entidad_actual.atacar(indice):
                self.tablero.casillas(destino).entidad.recibir_daño(self.entidad_actual.ataques[indice].potencia()*self.entidad_actual.ataque)
            else:
                pass

    def iniciar_combate(self, usar_atb=False):#Falta revisar, de momento no usar
        self.usar_atb = usar_atb
        self.activo = True
        for e in self.todas_entidades:
            e.reset_atb()
        if not usar_atb:
            self.granTurno()
            return self.pequeTurno()
        return None
        
    def finalizar_turno(self, acciones_realizadas=None):#Falta revisar, de momento no usar
        if self.entidad_actual:
            self.entidad_actual.reset_atb()
        if acciones_realizadas:
            self.historial_turnos[-1].update(acciones_realizadas)
        if not self.usar_atb and self.orden.empty():
            return self.granTurno()
        return True
    
    def _verificar_fin_combate(self) -> bool: #Se usa en el bucle while cada iteracion
        aliados_vivos = any(e.esta_vivo() for e in self.aliados)
        enemigos_vivos = any(e.esta_vivo() for e in self.enemigos)
        
        if not aliados_vivos:
            return True, 'derrota'
            
        if not enemigos_vivos:
            return True, 'victoria'
            
        return False, False
        
    def obtener_objetivos_validos(self, atacante=None):#Falta el mapa y falta revisar, de momento no usar
        atacante = atacante or self.entidad_actual
        if not atacante:
            return []
        if atacante.equipo == "enemigo":
            return [e for e in self.aliados if e.esta_vivo()]
        return [e for e in self.enemigos if e.esta_vivo()]

    def lo_que_se_ve(self, window):#Muestra todo el mapa y la interfaz que puede ver el usuario
        self.tablero.dibujar(window)#En esta linea va el metodo que hace que el objeto del mapa, se muestre
        self.mostrar_ui(window)
        #No se si en mostrar mapa estará tambien mostrar aliados y enemigos

    def mostrar_ui(self, window):
        pass
        #self.panel_ui.dibujar(window, self._jugadas, self.entidad_actual)






# INICIALIZAR ENTIDADES DE PRUEBA

# FUENTE PARA TEXTO
font = pg.font.SysFont("consolas", 20)
clock = pg.time.Clock()

# Para mostrar la pantalla de inicio
def pantalla_inicio():
    window.blit(font.render("Bienvenido al juego", True, GB_COLORS["white"]), (380, 200))
    window.blit(font.render("Pulse espacio para pasar a la creacion de personaje", True, GB_COLORS["white"]), (200, 600))

# Para mostrar la pantalla de cambio
def pantalla_cambio():
    window.blit(font.render("toca enfrentarse a algo", True, GB_COLORS["white"]), (380, 200))
    window.blit(font.render("buena suerte", True, GB_COLORS["white"]), (200, 600))

# Para mostrar la pantalla de creacion de personajes, esta hecha de forma temporal para ser modificada si la quieres cambiar hazlo, no tengas miedo
def pantalla_derrota():
    window.blit(font.render("Fuiste derrotado", True, GB_COLORS["white"]), (380, 200))
    window.blit(font.render("No se admiten perdedores, cierra la ventana", True, GB_COLORS["white"]), (200, 600))

from personajes.creacion_personaje_ui import PantallaCreacionPersonajes

pantalla_creacion = PantallaCreacionPersonajes(font, GB_COLORS)
aliados = []
pantalla_recompensa = None
indice_recompensa = 0

# BUCLE PRINCIPAL
running = True
while running:
    dt = clock.get_time() / 1000.0
    pos_raton = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                aliados = pantalla_creacion.obtener_personajes()
                pantalla_recompensa = PantallaRecompensa(font, GB_COLORS, aliados)
                estado_partida = 4
            # Controles simples para probar
            elif estado_partida == 0:
                if event.key == pg.K_SPACE:
                    estado_partida = 1

            elif estado_partida == 1:
                terminado = pantalla_creacion.manejar_evento(event)

                if terminado:
                    aliados = pantalla_creacion.obtener_personajes()
                    personaje_a_mejorar = aliados[indice_recompensa]
                    pantalla_recompensa = PantallaRecompensa(font, GB_COLORS, personaje_a_mejorar)
                    estado_partida = 2
                
            elif estado_partida == 4:
                terminado = pantalla_recompensa.manejar_evento(event)

                if terminado:
                    estado_partida = 2

        if estado_partida == 3:
            if type(peleilla.entidad_actual) == Enemy:
                peleilla.entidad_actual.ejecutar_turno_ia(peleilla.aliados, peleilla.tablero, peleilla)

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1: # Botón izquierdo del ratón presionado
                    if pos_raton[1] > 550:# es temporal, se encargará de saber si el raton está por debajo del mapa o no
                        pass
                    else:
                        col = pos_raton[0] // peleilla.tablero.tamaño_casilla
                        fila = pos_raton[1] // peleilla.tablero.tamaño_casilla
                        destino = (fila, col)
                        if 0 <= fila < peleilla.tablero.alto and 0 <= col < peleilla.tablero.ancho:
                            casilla_clickada = peleilla.tablero.casillas[fila][col]
                            casilla_actual = peleilla.tablero.casillas[peleilla.entidad_actual.current_node[0]][peleilla.entidad_actual.current_node[1]]
                            
                            if casilla_clickada.entidad is not None and casilla_clickada.entidad.equipo == "enemigo":
                                dist, camino = peleilla.tablero.encontrar_camino( peleilla.entidad_actual.current_node, destino)
                                if dist <= peleilla.entidad_actual.velocidad():
                                    casilla_clickada.entidad.take_damage(
                                peleilla.entidad_actual.ataque
                                )
                                peleilla.paso_de_turno()
                            elif not casilla_clickada.esta_ocupada() and not casilla_clickada.obstaculo:
                                dist, camino = peleilla.tablero.encontrar_camino(
                                peleilla.entidad_actual.current_node, destino
                            )
                                if dist <= peleilla.entidad_actual.max_mobility:
                                    casilla_actual.remover_entidad()
                                    casilla_clickada.colocar_entidad(peleilla.entidad_actual)
                                    peleilla.paso_de_turno()    

                elif event.button == 2: # Botón medio del ratón presionado
                    pass
                elif event.button == 3: # Botón derecho del ratón presionado
                    pass
            '''if event.key == pg.K_1:
                # Atacar automáticamente con el jugador actual
                if entidad_actual and entidad_actual.equipo == "jugador":
                    objetivos = Enfrentamiento.obtener_objetivos_validos(entidad_actual)
                    if objetivos:
                        objetivo = objetivos[0]
                        daño = entidad_actual.realizar_ataque(objetivo)
                        objetivo.recibir_daño(daño)
                        print(f"¡{entidad_actual.nombre} hace {daño:.1f} daño a {objetivo.nombre}!")
                        
                        Enfrentamiento._actualizar_lista_entidades()
                        if Enfrentamiento._verificar_fin_combate():
                            pass
                        else:
                            Enfrentamiento.finalizar_turno()
                            entidad_actual = Enfrentamiento.pequeTurno()
                            if entidad_actual is None:
                                if Enfrentamiento.granTurno():
                                    entidad_actual = Enfrentamiento.pequeTurno()
'''
    
    # LÓGICA DEL JUEGO
    if estado_partida == 0:#corresponde con la pantalla de inicio
        pass
    elif estado_partida == 1:
        pass
    elif estado_partida ==2:# la animacion que no se si quitar
        pantalla_cambio()
        estado_partida = 3
        peleilla = Enfrentamiento(aliados)
    elif estado_partida == 3:
        true_o_false, berificador = peleilla._verificar_fin_combate()
        if true_o_false:
            if berificador == 'victoria':
                estado_partida=4
            else:
                estado_partida=9
                
        pg.time.delay(500)  # Pequeña pausa para ver la acción
            
    elif estado_partida == 4:
        pass
    
    # DIBUJAR
    window.fill(GB_COLORS['black'])
    
    if estado_partida == 0:
        pantalla_inicio()
    elif estado_partida == 1:
        pantalla_creacion.dibujar(window)
    elif estado_partida == 2:
        pass
    elif estado_partida == 3:
        # Dibujar estado del combate
        peleilla.lo_que_se_ve(window)
    elif estado_partida == 4:
        pantalla_recompensa.dibujar(window)

        '''y_offset = 50
        
        titulo = font.render(f"RONDA {Enfrentamiento._jugadas}", True, GB_COLORS['white'])
        window.blit(titulo, (50, y_offset))
        y_offset += 40
        
        # Aliados
        aliados_text = font.render("TUS PERSONAJES:", True, GB_COLORS['green_bright'])
        window.blit(aliados_text, (50, y_offset))
        y_offset += 30
        
        for e in Enfrentamiento.aliados:
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
        
        for e in Enfrentamiento.enemigos:
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
        
        if not Enfrentamiento.activo and Enfrentamiento.ganador:
            y_offset += 60
            if Enfrentamiento.ganador == "jugadores":
                resultado = font.render("¡VICTORIA! Pulsa ESC para salir", True, GB_COLORS['green_bright'])
            else:
                resultado = font.render("DERROTA... Pulsa ESC para salir", True, GB_COLORS['red_bright'])
            window.blit(resultado, (50, y_offset))'''
    elif estado_partida == 9:
        pantalla_derrota()
    pg.display.update()
    clock.tick(60)

pg.quit()

