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

        self.ataques = ataques if ataques is not None else []
        self.vivo = True

    def velocidad(self):
        return self.velocidad_base

    def esta_vivo(self):
        return self.vivo and self.hp_actual > 0

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
    
    def mostrar_en_turno(self):
        window.blit(font.render(f"{self.nombre}", True, GB_COLORS["white"]), (380, 200))#Nombre del personaje
        window.blit(font.render(f"1:{self.ataques[0].nombre()}", True, GB_COLORS["white"]), (200, 500))#nombre de los ataques disponibles
        window.blit(font.render(f"2:{self.ataques[1].nombre()}", True, GB_COLORS["white"]), (300, 650))
        window.blit(font.render(f"3:{self.ataques[2].nombre()}", True, GB_COLORS["white"]), (300, 500))
        window.blit(font.render(f"4:{self.ataques[3].nombre()}", True, GB_COLORS["white"]), (200, 650))