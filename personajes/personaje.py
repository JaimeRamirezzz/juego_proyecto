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
        self.experiencia_necesaria = 100
        self.puntos_stats = 0

        self.hp_max = vida
        self.hp_actual = vida
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad_base = velocidad

        self.vivo = True
        self.estados = []
        self.modificadores_vel = 0

    def velocidad(self):
        return max(0, self.velocidad_base + self.modificadores_vel)

    def esta_vivo(self):
        return self.vivo and self.hp_actual > 0

    def recibir_daño(self, daño):
        daño_final = max(1, daño - self.defensa)
        self.hp_actual -= daño_final

        if self.hp_actual <= 0:
            self.hp_actual = 0
            self.vivo = False
            print(f"{self.nombre} ha muerto")

    def curarse(self, cantidad):
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
        self.experiencia_necesaria = int(self.experiencia_necesaria * 1.25)

        self.hp_actual = self.hp_max

        print(f"{self.nombre} subió a nivel {self.nivel}")
        print(f"Tiene {self.puntos_stats} puntos para repartir")

    def mejorar_stat(self, stat):
        if self.puntos_stats <= 0:
            print("No tienes puntos disponibles")
            return

        if stat == "vida":
            self.hp_max += 5
            self.hp_actual += 5

        elif stat == "ataque":
            self.ataque += 1

        elif stat == "defensa":
            self.defensa += 1

        elif stat == "velocidad":
            self.velocidad_base += 1

        else:
            print("Stat inválida")
            return

        self.puntos_stats -= 1
        print(f"{self.nombre} mejoró {stat}")

    def calcular_daño_base(self, objetivo):
        denominador = self.ataque + objetivo.defensa

        if denominador == 0:
            return 0

        daño_base = (self.ataque ** 2) / denominador
        return daño_base

    def realizar_ataque(self, objetivo):
        daño = self.calcular_daño_base(objetivo)
        objetivo.recibir_daño(daño)
        return daño

    def mostrar_stats(self):
        print("---------------")
        print(f"Nombre: {self.nombre}")
        print(f"Clase: {self.clase}")
        print(f"Nivel: {self.nivel}")
        print(f"Vida: {self.hp_actual}/{self.hp_max}")
        print(f"Ataque: {self.ataque}")
        print(f"Defensa: {self.defensa}")
        print(f"Velocidad: {self.velocidad()}")
        print(f"XP: {self.experiencia}/{self.experiencia_necesaria}")
        print("---------------")