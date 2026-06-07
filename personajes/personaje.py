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
class Personaje:
    _id_counter = 0
 
    def __init__(self, nombre, clase, vida, ataque, defensa, velocidad, ataques=None, equipo="jugador"):
        Personaje._id_counter += 1
        self.id = Personaje._id_counter
        self.nombre = nombre
        self.clase = clase
        self.equipo = equipo

        self.nivel = 1
        self.experiencia = 0
        self.experiencia_necesaria = 50

        self.hp_max = vida
        self.hp_actual = vida
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad_base = velocidad
        
        self.aguante = 10
        self.capacidad_aguante = self.aguante
         # posición para el mapa
        self.current_node = (0, 0)
        self.color = (100, 200, 255)  # AZUL CLARO
        self.ataques = ataques if ataques is not None else []
        self.vivo = True

    def recuperacion_por_turno(self): #Para la implementacion de los ataques con consumo de energia
        #He la capacidad de aguante maximo es aguante * 2, pero ahora no hay una variable que sea el maximo
        if self.aguante < self.capacidad_aguante:
            self.capacidad_aguante = self.aguante * 2
        else:
            self.capacidad_aguante += self.aguante

    def atacar(self, indice):
        if len(self.ataques) > indice:
            if self.ataques[indice].coste() > self.capacidad_aguante:
                return False
            else:
                self.capacidad_aguante = self.ataques[indice].coste() > self.capacidad_aguante
                return True
        else:
            return False

    def velocidad(self):
        return self.velocidad_base

    def recibir_daño(self, cantidad):
        self.hp_actual -= cantidad/self.defensa
        if self.hp_actual <= 0:
            self.vivo = False

    def esta_vivo(self):
        return self.vivo or self.hp_actual > 0

    def añadir_ataque(self, ataque):
        self.ataques.append(ataque)

    def mostrar_stats(self):
        print("---------------")
        print(f"Nombre: {self.nombre}")
        print(f"Clase: {self.clase}")
        print(f"Nivel: {self.nivel}")
        print(f"Vida: {self.hp_actual}/{self.hp_max}")
        print(f"Ataque: {self.ataque}")
        print(f"Defensa: {self.defensa}")
        print(f"Velocidad: {self.velocidad_base}")
        print(f"XP: {self.experiencia}/{self.experiencia_necesaria}")
        print(f"Ataques: {self.ataques}")
        print("---------------")
    
    def mostrar_en_turno(self, window, font):
        window.blit(font.render(f"{self.nombre}", True, GB_COLORS["white"]), (380, 200))#Nombre del personaje
        window.blit(font.render(f"1:{self.ataques[0].nombre()}", True, GB_COLORS["white"]), (200, 500))#nombre de los ataques disponibles
        window.blit(font.render(f"2:{self.ataques[1].nombre()}", True, GB_COLORS["white"]), (300, 650))
        window.blit(font.render(f"3:{self.ataques[2].nombre()}", True, GB_COLORS["white"]), (300, 500))
        window.blit(font.render(f"4:{self.ataques[3].nombre()}", True, GB_COLORS["white"]), (200, 650))