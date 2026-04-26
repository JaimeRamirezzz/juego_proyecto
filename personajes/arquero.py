from personajes.personaje import Personaje


class Arquero(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Arquero",
            vida=25,
            ataque=8,
            defensa=3,
            velocidad=9,
            equipo=equipo
        )