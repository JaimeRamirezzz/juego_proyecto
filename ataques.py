class Ataque:
    def __init__(self, potencia, nombre, grupo_ataque, descripcion, desgaste):
        self._potencia = potencia
        self._nombre = nombre
        self._grupo_ataque = grupo_ataque
        self._descripcion = descripcion
        self.desgaste = desgaste

    def nombre(self):
        return self._nombre

    def potencia(self):
        return self._potencia

    def grupo_ataque(self):
        return self._grupo_ataque

    def descripcion(self):
        return self._descripcion
    
    def coste(self):
        return self.desgaste

    def atacar(self, atacante, objetivo):
        daño = self._potencia + atacante.ataque
        objetivo.recibir_daño(daño)
        return daño


# Ataques de arquero
Disparo_rapido = Ataque(8, "Disparo rápido", "arquero", "Ataque veloz con daño moderado", 4)
Flecha_precisa = Ataque(12, "Flecha precisa", "arquero", "Ataque más potente y preciso", 6)
Disparo_doble = Ataque(7, "Disparo doble", "arquero", "Dos disparos rápidos seguidos", 3)

# Ataques de caballero
Tajo_firme = Ataque(10, "Tajo firme", "caballero", "Ataque equilibrado con espada", 6)
Golpe_con_escudo = Ataque(8, "Golpe con escudo", "caballero", "Daño bajo, pero seguro", 4)
Corte_defensivo = Ataque(7, "Corte defensivo", "caballero", "Ataque que protege al usuario", 3)

# Ataques de tanque
Martillazo = Ataque(9, "Martillazo", "tanque", "Golpe fuerte directo", 5)
Golpe_pesado = Ataque(11, "Golpe pesado", "tanque", "Más daño, pero más lento", 7)
Impacto_sismico = Ataque(8, "Impacto sísmico", "tanque", "Salta y hace retumbar el suelo", 4)