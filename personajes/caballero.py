from personajes.personaje import Personaje


class Caballero(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Caballero",
            vida=30,
            ataque=7,
            defensa=6,
            velocidad=5,
            equipo=equipo
        )