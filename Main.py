import pygame as pg
pg.init()
print("prueba")
window = pg.display.set_mode((1000, 700))



class enfrentamiento:
    def __init__(self, ej1, ej2, ej3, ej4, mapa_tablero, enemigos_mapa = list):#ej = entidad jugable
        self._jugadas = 0
        self._noEntidades = 4+len(enemigos_mapa) #para tener como de grande es la cola
        self.tablero = mapa_tablero # porbisional asta el tablero
        self.ej1 = ej1 #de momento se queda así, pero se puede modificar en el futuro
        self.orden = Cola() # cola ordenada en funcion de la velocidad
    def turno(self):
        pass # self.orden.primer = la entidad a la que le toca atacar

        
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

            #modificar 