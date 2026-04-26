class Personaje:
    _id_counter = 0

    def __init__(self, nombre, clase, vida, ataque, defensa, velocidad, equipo="jugador"):
        Personaje._id_counter += 1
        self.id = Personaje._id_counter

        self.nombre = nombre
        self.clase = clase
        self.equipo = equipo

        self.nivel = 1
        self.experiencia = 0
        self.experiencia_necesaria = 50
        self.puntos_stats = 0

        self.hp_max = vida
        self.hp_actual = vida
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad_base = velocidad

        self.vivo = True

    def velocidad(self):
        return self.velocidad_base

    def esta_vivo(self):
        return self.vivo and self.hp_actual > 0

    def recibir_daño(self, daño):
        daño_final = max(1, daño - self.defensa)
        self.hp_actual -= daño_final

        if self.hp_actual <= 0:
            self.hp_actual = 0
            self.vivo = False
            print(f"{self.nombre} ha sido derrotado")

    def curarse(self, cantidad):
        if self.esta_vivo():
            self.hp_actual += cantidad

            if self.hp_actual > self.hp_max:
                self.hp_actual = self.hp_max

    def ganar_experiencia(self, cantidad):
        self.experiencia += cantidad

        while self.experiencia >= self.experiencia_necesaria:
            self.experiencia -= self.experiencia_necesaria
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.puntos_stats += 3
        self.experiencia_necesaria = int(self.experiencia_necesaria * 1.3)

        self.hp_actual = self.hp_max

        print(f"{self.nombre} ha subido al nivel {self.nivel}")
        print(f"Ha ganado 3 puntos para mejorar estadísticas")

    def mejorar_stat(self, stat):
        if self.puntos_stats <= 0:
            print("No tienes puntos disponibles")
            return

        if stat == "vida":
            self.hp_max += 3
            self.hp_actual += 3

        elif stat == "ataque":
            self.ataque += 1

        elif stat == "defensa":
            self.defensa += 1

        elif stat == "velocidad":
            self.velocidad_base += 1

        else:
            print("Stat no válida")
            return

        self.puntos_stats -= 1
        print(f"{self.nombre} mejoró {stat}")

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
        print(f"Puntos disponibles: {self.puntos_stats}")
        print("---------------")