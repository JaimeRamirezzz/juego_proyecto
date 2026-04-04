import pygame as pg
import math as m
import random as r
pg.init()
window = pg.display.set_mode((1000, 700))
estado_partida = 0 # para controlar que se va a mostrar por pantalla y tambien si estamos en combate o en tienda o cosas asi


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


class enfrentamiento:
    def __init__(self, ej1, ej2, ej3, ej4, mapa_tablero, enemigos_mapa = list):#ej = entidad jugable
        self._jugadas = 0
        self._noEntidades = 4+len(enemigos_mapa) #para tener como de grande es la cola
        self.tablero = mapa_tablero # porbisional asta el tablero
        self.ej1 = ej1 #de momento se queda así, pero se puede modificar en el futuro
        self.orden = ColaEnlazada() # cola ordenada en funcion de la velocidad
#    def granTurno(self): ##aún me queda por introducir y me faltan como me van a llegar las cosas para el enfrentamiento
#        if self.orden.empty():
#            self.recuentoEntidades = self._noEntidades
#            entidad_mas_rapida_de_las_restantes = todas_las_entidades[1]
#            for i in range(1,self._noEntidades):
#                for j in todas_las_entidades_para_orden:
#                    if entidad_mas_rapida_de_las_restantes.velocidad() < j
#                        pass
#                    else:
#                        entidad_mas_rapida_de_las_restantes = j
#                self.orden.push(entidad_mas_rapida_de_las_restantes)
#                todas_las_entidades_para_orden.pop(entidad_mas_rapida_de_las_restantes)

    def pequeTurno(self):
        pass # self.orden.first = la entidad a la que le toca atacar

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
    
