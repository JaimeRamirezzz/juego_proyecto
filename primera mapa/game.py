import pygame # Importa las funciones principales de Pygame
from map import TipoTerreno, Mapa # Importa las clases que creamos en mapa.py

# Configuración inicial
pygame.init() # Inicializa todos los módulos internos de Pygame

# Configura el título de la ventana
pygame.display.set_caption("Juego Proyecto")
# Crea la ventana de juego con una resolución de píxeles
pantalla = pygame.display.set_mode((1000, 700))

# Define un color de fondo usando formato RGB (Rojo, Verde, Azul)
color_fondo = (30, 150, 50)
# Variable de control para mantener el juego activo
ejecutando = True

# Definición de la paleta de terrenos disponibles en el juego
tipos_terreno = [
    TipoTerreno("tierra(0)", "imagen/tierra(0).png", False), # Índice 0
    TipoTerreno("hierba(1)", "imagen/hierba(1).png", False), # Índice 1
    TipoTerreno("agua(2)", "imagen/agua(2).png", False), # Índice 2
    TipoTerreno("madera(3)", "imagen/madera(3).png", False), # Índice 3
    TipoTerreno("lava(4)", "imagen/lava(4).png", True)     # Índice 4 (Sólido)
]

# 1. Definir una lista con las rutas de los archivos de tus mapas en orden
archivos_niveles = [
    "primera mapa/start.map",
    "primera mapa/nivel2.map", # Asegúrate de crear este archivo
]

# 2. Cargar todos los mapas en una lista
mapas_del_juego = [] #Es una lista que contiene todos tus objetos Mapa ya cargados en la memoria.
for archivo in archivos_niveles:
    # Creamos el objeto mapa y lo añadimos a la lista (asumo 32 como tamaño)
    nuevo_mapa = Mapa(archivo, tipos_terreno, 52) 
    mapas_del_juego.append(nuevo_mapa)

# 3. Variable para controlar en qué nivel está el jugador (0 es el primer nivel)
nivel_actual = 0 #Funciona como un puntero. Si vale 0, el juego dibuja mapas_del_juego[0] (tu start.map). Si vale 1, dibuja mapas_del_juego[1].

# Bucle Principal del Juego
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        # Usaremos la tecla ESPACIO para probar el cambio de mapa
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:#una
                # Verificamos que no estemos en el último nivel
                if nivel_actual < len(mapas_del_juego) - 1:
                    nivel_actual += 1 # Pasamos al siguiente nivel
                    print(f"Avanzaste al nivel {nivel_actual + 1}")
                else:
                    print("¡Has terminado todos los niveles!")

    # Código de Dibujo
    pantalla.fill(color_fondo) 
    
    # 4. Dibujar SOLO el mapa que corresponde al nivel actual
    mapas_del_juego[nivel_actual].dibujar(pantalla)

    # Actualiza la pantalla
    pygame.display.flip()
    
    # Pausa
    pygame.time.delay(17)

pygame.quit()
