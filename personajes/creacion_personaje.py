def repartir_puntos_creacion(personaje, vida=0, ataque=0, defensa=0, velocidad=0):
    puntos_disponibles = 5
    puntos_usados = vida + ataque + defensa + velocidad

    if puntos_usados > puntos_disponibles:
        print("Has usado demasiados puntos de creación")
        return False

    personaje.hp_max += vida * 2
    personaje.hp_actual = personaje.hp_max
    personaje.ataque += ataque
    personaje.defensa += defensa
    personaje.velocidad_base += velocidad

    return True