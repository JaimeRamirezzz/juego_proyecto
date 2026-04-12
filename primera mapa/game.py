import pygame # Importa las funciones principales de Pygame
from map import TipoTerreno, Mapa # Importa las clases que creamos en mapa.py

# Configuración inicial
pygame.init() # Inicializa todos los módulos internos de Pygame

# Configura el título de la ventana
pygame.display.set_caption("Juego Proyecto")
# Crea la ventana de juego con una resolución de 800x600 píxeles
pantalla = pygame.display.set_mode((988, 677))

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

# Crea el objeto mapa cargando el archivo .map y asignando los tipos de terreno
mapa = Mapa("primera mapa/start.map", tipos_terreno, 52)

# Bucle Principal del Juego
while ejecutando:
    # Revisa todos los eventos que ocurren (teclado, ratón, etc.)
    for evento in pygame.event.get():
        # Si el usuario hace clic en la 'X' de la ventana, detiene el bucle
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Código de Dibujo
    pantalla.fill(color_fondo) # Limpia la pantalla pintándola del color de fondo
    mapa.dibujar(pantalla)    # Llama a la función para dibujar todos los terrenos

    # Actualiza la pantalla para mostrar los cambios realizados
    pygame.display.flip()

    # Pausa el código por 17 milisegundos para limitar los FPS (aprox. 60 FPS)
    pygame.time.delay(17)

# Finaliza Pygame y cierra la ventana correctamente
pygame.quit()