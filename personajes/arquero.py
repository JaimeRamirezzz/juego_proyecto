from personajes.personaje import Personaje


class Arquero(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Arquero",
            vida=14,
            ataque=5,
            defensa=2,
            velocidad=6,
            equipo=equipo
        )