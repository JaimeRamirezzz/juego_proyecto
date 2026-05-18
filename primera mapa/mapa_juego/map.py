import pygame # Importa la librería Pygame para manejar gráficos

# Clase para definir las propiedades de cada tipo de suelo/terreno
class TipoTerreno:
    def __init__(self, nombre, imagen, es_solido):
        self.nombre = nombre # Guarda el nombre (ej. "Lava")
        self.imagen = pygame.image.load(imagen) # Carga el archivo de imagen en memoria
        self.es_solido = es_solido # Define si el personaje puede atravesarlo o no

# Clase para gestionar la construcción y el dibujo del nivel
class Mapa:
    def __init__(self, archivo_mapa, tipos_terreno, tamano_terreno):
        # Almacena la lista de tipos de terrenos disponibles
        self.tipos_terreno = tipos_terreno

        # Abre el archivo de texto que contiene la estructura del nivel
        archivo = open(archivo_mapa, "r")
        datos = archivo.read() # Lee todo el contenido del archivo
        archivo.close() # Cierra el archivo para liberar recursos

        # Crea la matriz del mapa a partir de los datos leídos
        self.terrenos = [] # Lista principal que contendrá las filas
        for linea in datos.split('\n'): # Divide el texto por cada salto de línea
            fila = [] # Crea una lista vacía para la fila actual
            for numero_terreno in linea: # Recorre cada carácter (número) de la línea
                fila.append(int(numero_terreno)) # Convierte el carácter a entero y lo añade
            self.terrenos.append(fila) # Añade la fila completa a la lista de terrenos

        # Guarda el tamaño en píxeles de cada cuadro de terreno (ej. 32x32)
        self.tamano_terreno = tamano_terreno

    # Método para renderizar el mapa en la ventana del juego
    def dibujar(self, pantalla):
        # 1. Calculamos el tamaño total del mapa en píxeles
        # Ancho: cantidad de columnas por el tamaño de cada cuadro
        ancho_mapa = len(self.terrenos[0]) * self.tamano_terreno
        # Alto: cantidad de filas por el tamaño de cada cuadro
        alto_mapa = len(self.terrenos) * self.tamano_terreno

        # 2. Calculamos el margen (offset) para centrar el mapa
        # Restamos el tamaño del mapa al tamaño de la ventana y dividimos entre 2
        offset_x = (pantalla.get_width() - ancho_mapa) // 2
        offset_y = (pantalla.get_height() - alto_mapa) // 2

        # 3. Dibujamos el mapa usando los desplazamientos (offsets)
        for y, fila in enumerate(self.terrenos):
            for x, terreno in enumerate(fila):
                # Calculamos la posición sumando el offset para que no empiece en (0,0)
                pos_x = x * self.tamano_terreno + offset_x
                pos_y = y * self.tamano_terreno + offset_y
                
                ubicacion = (pos_x, pos_y)
                
                # Seleccionamos la imagen según el número del terreno
                imagen = self.tipos_terreno[terreno].imagen
                # Dibujamos la imagen en la posición centrada
                pantalla.blit(imagen, ubicacion)