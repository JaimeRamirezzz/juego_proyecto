import pygame as pg
pg.init()
print("prueba")
window = pg.display.set_mode((1000, 700))

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

        
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

            #modificar 