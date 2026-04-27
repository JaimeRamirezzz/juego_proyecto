def ganar_experiencia(personaje, cantidad):
    personaje.experiencia += cantidad

    while personaje.experiencia >= personaje.experiencia_necesaria:
        personaje.experiencia -= personaje.experiencia_necesaria
        subir_nivel(personaje)


def subir_nivel(personaje):
    personaje.nivel += 1
    personaje.experiencia_necesaria = int(personaje.experiencia_necesaria * 1.3)

    aplicar_mejora_por_clase(personaje)

    personaje.hp_actual = personaje.hp_max

    print(f"{personaje.nombre} ha subido al nivel {personaje.nivel}")


def aplicar_mejora_por_clase(personaje):
    if personaje.clase == "Caballero":
        personaje.hp_max += 3
        personaje.ataque += 1
        personaje.defensa += 1

    elif personaje.clase == "Tanque":
        personaje.hp_max += 5
        personaje.defensa += 2

    elif personaje.clase == "Arquero":
        personaje.hp_max += 2
        personaje.ataque += 1
        personaje.velocidad_base += 1