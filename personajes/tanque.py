from personajes.personaje import Personaje


class Tanque(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Tanque",
            vida=40,
            ataque=5,
            defensa=9,
            velocidad=3,
            equipo=equipo
        )