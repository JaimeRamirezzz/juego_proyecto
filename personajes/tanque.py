from personajes.personaje import Personaje


class Tanque(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Tanque",
            vida=28,
            ataque=3,
            defensa=6,
            velocidad=2,
            ataques=[],
            equipo=equipo
        )