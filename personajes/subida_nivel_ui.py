import pygame as pg
from ataques import (
    Tajo_firme, Golpe_con_escudo, Corte_defensivo,
    Martillazo, Golpe_pesado, Impacto_sismico,
    Disparo_rapido, Flecha_precisa, Disparo_doble
)

ATAQUES_POR_CLASE = {
    "Caballero": [Tajo_firme, Golpe_con_escudo, Corte_defensivo],
    "Tanque": [Martillazo, Golpe_pesado, Impacto_sismico],
    "Arquero": [Disparo_rapido, Flecha_precisa, Disparo_doble]
}


class PantallaRecompensa:
    def __init__(self, font, colores, personajes):
        self.font = font
        self.colores = colores
        self.personajes = personajes
        self.terminada = False
        self.personaje_actual = 0
        self.opcion_actual = 0
        self.stat_actual = 0
        self.ataque_actual = 0

        self.stats = ["vida", "ataque", "defensa", "velocidad"]
        self.modo = "menu"  # menu, ataques, stats
        self.puntos_stats = 0

    def personaje(self):
        if not self.personajes:
            return None

        if self.personaje_actual >= len(self.personajes):
            return None

        return self.personajes[self.personaje_actual]

    def ataques_no_aprendidos(self):
        personaje = self.personaje()
        return [
            ataque for ataque in ATAQUES_POR_CLASE[personaje.clase]
            if ataque not in personaje.ataques
        ]

    def manejar_evento(self, event):
        if event.type != pg.KEYDOWN:
            return False

        personaje = self.personaje()

        if personaje is None:
            return True

        if self.modo == "menu":
            if event.key == pg.K_TAB:
                self.opcion_actual = (self.opcion_actual + 1) % 2

            elif event.key == pg.K_RETURN:
                if self.opcion_actual == 0:
                    self.modo = "ataques"
                    self.ataque_actual = 0
                else:
                    self.modo = "stats"
                    self.stat_actual = 0
                    self.puntos_stats = 2

        elif self.modo == "ataques":
            ataques = self.ataques_no_aprendidos()

            if not ataques:
                return True

            if event.key == pg.K_LEFT:
                self.ataque_actual = (self.ataque_actual - 1) % len(ataques)

            elif event.key == pg.K_RIGHT:
                self.ataque_actual = (self.ataque_actual + 1) % len(ataques)

            elif event.key == pg.K_RETURN:
                personaje.ataques.append(ataques[self.ataque_actual])
                self.terminada = True
                return True

        elif self.modo == "stats":
            if event.key == pg.K_LEFT:
                self.stat_actual = (self.stat_actual - 1) % len(self.stats)

            elif event.key == pg.K_RIGHT:
                self.stat_actual = (self.stat_actual + 1) % len(self.stats)

            elif event.key == pg.K_RETURN:
                self.subir_stat()

                if self.puntos_stats <= 0:
                    self.terminada = True
                    return True

        return self.terminada
    
    def pasar_siguiente_personaje(self):
        self.personaje_actual += 1
        self.opcion_actual = 0
        self.stat_actual = 0
        self.ataque_actual = 0
        self.modo = "menu"
        self.puntos_stats = 0

        if self.personaje_actual >= len(self.personajes):
            return True

        return False

    def subir_stat(self):
        if self.puntos_stats <= 0:
            return

        personaje = self.personaje()
        stat = self.stats[self.stat_actual]

        if stat == "vida":
            personaje.hp_max += 2
            personaje.hp_actual = personaje.hp_max

        elif stat == "ataque":
            personaje.ataque += 1

        elif stat == "defensa":
            personaje.defensa += 1

        elif stat == "velocidad":
            personaje.velocidad_base += 1

        self.puntos_stats -= 1

    def dibujar(self, pantalla):
        personaje = self.personaje()

        if personaje is None:
            texto = self.font.render("ERROR: no hay personajes para mejorar", True, self.colores["red_bright"])
            pantalla.blit(texto, (200, 300))
            return

        titulo = self.font.render("SUBIDA DE NIVEL", True, self.colores["yellow_bright"])
        pantalla.blit(titulo, (380, 60))

        texto_personaje = self.font.render(
            f"Personaje: {personaje.nombre} ({personaje.clase})",
            True,
            self.colores["white"]
        )
        pantalla.blit(texto_personaje, (80, 120))

        if self.modo == "menu":
            texto = self.font.render("Elige una recompensa:", True, self.colores["white"])
            pantalla.blit(texto, (80, 180))

            opciones = [
                "Desbloquear nuevo ataque",
                "Recibir 2 puntos de estadistica"
            ]

            for i, opcion in enumerate(opciones):
                color = self.colores["yellow_bright"] if i == self.opcion_actual else self.colores["light_gray"]
                texto_opcion = self.font.render(
                    f"{'> ' if i == self.opcion_actual else '  '}{opcion}",
                    True,
                    color
                )
                pantalla.blit(texto_opcion, (120, 250 + i * 60))

        elif self.modo == "ataques":
            ataques = self.ataques_no_aprendidos()

            titulo_ataque = self.font.render("Escoge un ataque nuevo:", True, self.colores["white"])
            pantalla.blit(titulo_ataque, (80, 180))

            if ataques:
                ataque = ataques[self.ataque_actual]

                texto_ataque = self.font.render(
                    f"<  {ataque.nombre()}  >",
                    True,
                    self.colores["yellow_bright"]
                )
                pantalla.blit(texto_ataque, (120, 270))

                descripcion = self.font.render(
                    ataque.descripcion(),
                    True,
                    self.colores["light_gray"]
                )
                pantalla.blit(descripcion, (120, 330))

        elif self.modo == "stats":
            titulo_stats = self.font.render(
                "Escoge donde poner los puntos:",
                True,
                self.colores["white"]
            )
            pantalla.blit(titulo_stats, (80, 180))

            puntos = self.font.render(
                f"Puntos restantes: {self.puntos_stats}",
                True,
                self.colores["yellow_bright"]
            )
            pantalla.blit(puntos, (80, 220))

            valores = {
                "vida": personaje.hp_max,
                "ataque": personaje.ataque,
                "defensa": personaje.defensa,
                "velocidad": personaje.velocidad_base
            }

            y = 280
            for i, stat in enumerate(self.stats):
                seleccionada = i == self.stat_actual
                self.dibujar_barra(pantalla, stat, valores[stat], y, seleccionada)
                y += 60

        # TEXTO FIJO ABAJO
        pg.draw.rect(pantalla, self.colores["dark_gray"], (0, 620, 1000, 80))

        if self.modo == "menu":
            ayuda_texto = "TAB: cambiar opcion   |   ENTER: confirmar"
        elif self.modo == "ataques":
            ayuda_texto = "FLECHAS IZQ/DER: cambiar ataque   |   ENTER: aprender"
        elif self.modo == "stats":
            ayuda_texto = "FLECHAS IZQ/DER: cambiar stat   |   ENTER: subir"
        else:
            ayuda_texto = "ENTER: continuar"

        ayuda = self.font.render(ayuda_texto, True, self.colores["yellow_bright"])
        pantalla.blit(ayuda, (40, 645))


    def dibujar_barra(self, pantalla, nombre_stat, valor, y, seleccionada):
        x = 250
        ancho_max = 250
        alto = 20

        texto = self.font.render(nombre_stat.upper(), True, self.colores["white"])
        pantalla.blit(texto, (80, y))

        pg.draw.rect(pantalla, self.colores["dark_gray"], (x, y, ancho_max, alto))

        ancho_barra = valor * 15
        if ancho_barra > ancho_max:
            ancho_barra = ancho_max

        color = self.colores["yellow_bright"] if seleccionada else self.colores["green_bright"]
        pg.draw.rect(pantalla, color, (x, y, ancho_barra, alto))

        valor_texto = self.font.render(str(valor), True, self.colores["white"])
        pantalla.blit(valor_texto, (530, y - 2))
            