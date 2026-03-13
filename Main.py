import pygame as pg
pg.init()

window = pg.display.set_mode((1000, 700))

print("hola") 
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

            #modificar 