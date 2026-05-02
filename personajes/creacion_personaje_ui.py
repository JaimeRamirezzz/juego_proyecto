import pygame as pg
from personajes.caballero import Caballero
from personajes.tanque import Tanque
from personajes.arquero import Arquero


class PantallaCreacionPersonajes:
    def __init__(self, font, colores):
        self.font = font
        self.colores = colores

        self.ultimo_movimiento = 0
        self.espera_movimiento = 200

        self.personajes = [
            Caballero("Caballero"),
            Tanque("Tanque"),
            Arquero("Arquero")
        ]

        self.ataques_disponibles = {
            "Caballero": [
                {"nombre": "Tajo firme", "desc": "Ataque equilibrado con espada"},
                {"nombre": "Golpe con escudo", "desc": "Daño bajo pero seguro"},
                {"nombre": "Corte defensivo", "desc": "Ataque que protege al usuario"}
            ],
            "Tanque": [
                {"nombre": "Martillazo", "desc": "Golpe fuerte directo"},
                {"nombre": "Golpe pesado", "desc": "Más daño, pero más lento"},
                {"nombre": "Impacto sísmico", "desc": "Salta y hace retumbar el suelo"}
            ],
            "Arquero": [
                {"nombre": "Disparo rápido", "desc": "Ataque veloz con daño moderado"},
                {"nombre": "Flecha precisa", "desc": "Ataque más potente y preciso"},
                {"nombre": "Disparo doble", "desc": "Dos disparos rápidos seguidos"}
            ]
        }

        self.ataque_actual = {
            "Caballero": 0,
            "Tanque": 0,
            "Arquero": 0
        }

        for personaje in self.personajes:
            personaje.ataques = [
                self.ataques_disponibles[personaje.clase][0]["nombre"]
            ]

        self.clase_actual = 0
        self.stat_actual = 0

        self.stats = ["vida", "ataque", "defensa", "velocidad"]

        self.puntos_maximos = 5

        self.puntos_usados = {
            "Caballero": {"vida": 0, "ataque": 0, "defensa": 0, "velocidad": 0},
            "Tanque": {"vida": 0, "ataque": 0, "defensa": 0, "velocidad": 0},
            "Arquero": {"vida": 0, "ataque": 0, "defensa": 0, "velocidad": 0}
        }

    def personaje_actual(self):
        return self.personajes[self.clase_actual]

    def puntos_restantes(self):
        personaje = self.personaje_actual()
        usados = sum(self.puntos_usados[personaje.clase].values())
        return self.puntos_maximos - usados

    def manejar_evento(self, event):
        if event.type == pg.KEYDOWN:

            if event.key == pg.K_RETURN:
                return True

            tiempo_actual = pg.time.get_ticks()

            if event.key in [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT, pg.K_TAB, pg.K_e]:
                if tiempo_actual - self.ultimo_movimiento < self.espera_movimiento:
                    return False

                self.ultimo_movimiento = tiempo_actual

            if event.key == pg.K_TAB:
                self.clase_actual = (self.clase_actual + 1) % len(self.personajes)

            elif event.key == pg.K_UP:
                self.stat_actual = (self.stat_actual - 1) % len(self.stats)

            elif event.key == pg.K_DOWN:
                self.stat_actual = (self.stat_actual + 1) % len(self.stats)

            elif event.key == pg.K_RIGHT:
                self.subir_stat()

            elif event.key == pg.K_LEFT:
                self.bajar_stat()

            elif event.key == pg.K_e:
                self.cambiar_ataque()

        return False
    
    def cambiar_ataque(self):
        personaje = self.personaje_actual()
        clase = personaje.clase

        self.ataque_actual[clase] = (self.ataque_actual[clase] + 1) % len(self.ataques_disponibles[clase])

        ataque_elegido = self.ataques_disponibles[clase][self.ataque_actual[clase]]

        personaje.ataques = [ataque_elegido["nombre"]]

    def subir_stat(self):
        if self.puntos_restantes() <= 0:
            return

        personaje = self.personaje_actual()
        stat = self.stats[self.stat_actual]

        self.puntos_usados[personaje.clase][stat] += 1

        if stat == "vida":
            personaje.hp_max += 2
            personaje.hp_actual = personaje.hp_max
        elif stat == "ataque":
            personaje.ataque += 1
        elif stat == "defensa":
            personaje.defensa += 1
        elif stat == "velocidad":
            personaje.velocidad_base += 1

    def bajar_stat(self):
        personaje = self.personaje_actual()
        stat = self.stats[self.stat_actual]

        if self.puntos_usados[personaje.clase][stat] <= 0:
            return

        self.puntos_usados[personaje.clase][stat] -= 1

        if stat == "vida":
            personaje.hp_max -= 2
            personaje.hp_actual = personaje.hp_max
        elif stat == "ataque":
            personaje.ataque -= 1
        elif stat == "defensa":
            personaje.defensa -= 1
        elif stat == "velocidad":
            personaje.velocidad_base -= 1

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

    def dibujar(self, pantalla):
        personaje = self.personaje_actual()

        titulo = self.font.render("CREACIÓN DE PERSONAJE", True, self.colores["white"])
        pantalla.blit(titulo, (340, 60))

        instrucciones1 = self.font.render("TAB: cambiar clase", True, self.colores["light_gray"])
        instrucciones2 = self.font.render("Flechas ARRIBA/ABAJO: elegir stat", True, self.colores["light_gray"])
        instrucciones3 = self.font.render("Flechas DERECHA/IZQUIERDA: subir o bajar", True, self.colores["light_gray"])
        instrucciones4 = self.font.render("ENTER: confirmar personajes", True, self.colores["light_gray"])

        pantalla.blit(instrucciones1, (80, 610))
        pantalla.blit(instrucciones2, (80, 635))
        pantalla.blit(instrucciones3, (80, 660))
        pantalla.blit(instrucciones4, (600, 635))

        clase_texto = self.font.render(f"Clase actual: {personaje.clase}", True, self.colores["yellow_bright"])
        pantalla.blit(clase_texto, (80, 130))

        puntos_texto = self.font.render(f"Puntos restantes: {self.puntos_restantes()}", True, self.colores["white"])
        pantalla.blit(puntos_texto, (80, 170))

        valores = {
            "vida": personaje.hp_max,
            "ataque": personaje.ataque,
            "defensa": personaje.defensa,
            "velocidad": personaje.velocidad_base
        }

        y = 240
        for i, stat in enumerate(self.stats):
            seleccionada = i == self.stat_actual
            self.dibujar_barra(pantalla, stat, valores[stat], y, seleccionada)
            y += 60

        titulo_ataques = self.font.render(
            "Ataque inicial:",
            True,
            self.colores["white"]
        )
        pantalla.blit(titulo_ataques, (650, 220))

        clase = personaje.clase
        ataques = self.ataques_disponibles[clase]

        for i, ataque in enumerate(ataques):
            seleccionado = i == self.ataque_actual[clase]

            color = self.colores["yellow_bright"] if seleccionado else self.colores["light_gray"]

            texto = self.font.render(
                f"{'>' if seleccionado else ' '} {ataque['nombre']}",
                True,
                color
            )

            pantalla.blit(texto, (650, 260 + i * 35))

        # Texto de descripción
        ataque_seleccionado = ataques[self.ataque_actual[clase]]
        texto_desc = ataque_seleccionado["desc"]

        # Crear superficie de texto
        texto_render = self.font.render(texto_desc, True, self.colores["white"])

        # Tamaño de la caja (un poco más grande que el texto)
        padding = 10
        caja_x = 640
        caja_y = 370

        caja_ancho = texto_render.get_width() + padding * 2
        caja_alto = texto_render.get_height() + padding * 2

        # Dibujar fondo de la caja
        pg.draw.rect(pantalla, self.colores["dark_gray"], (caja_x, caja_y, caja_ancho, caja_alto))

        # Borde de la caja
        pg.draw.rect(pantalla, self.colores["white"], (caja_x, caja_y, caja_ancho, caja_alto), 2)

        # Dibujar texto encima
        pantalla.blit(texto_render, (caja_x + padding, caja_y + padding))

        ayuda_ataque = self.font.render(
            "E: cambiar atque",
            True,
            self.colores["light_gray"]
        )
        pantalla.blit(ayuda_ataque, (650, 420))

    def obtener_personajes(self):
        return self.personajes