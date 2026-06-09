from personajes.personaje import Personaje


class Arquero(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Arquero",
            vida=20,
            ataque=5,
            defensa=6,
            velocidad=6,
            ataques=[],
            equipo=equipo
        )