from personajes.personaje import Personaje


class Caballero(Personaje):
    def __init__(self, nombre, equipo="jugador"):
        super().__init__(
            nombre=nombre,
            clase="Caballero",
            vida=18,
            ataque=4,
            defensa=4,
            velocidad=3,
            ataques=["Espadazo", "Corte rápido", "Golpe con escudo"],
            equipo=equipo
        )