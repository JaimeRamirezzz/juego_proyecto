import pygame
from config import ANCHO_PANTALLA, ALTO_PANTALLA, ALTO_PANEL, ALTO_MAPA
from personajes.personaje import Personaje
from ataques import Ataque
GB_COLORS = {
    'white': (224, 248, 208),
    'light_gray': (136, 192, 112),
    'dark_gray': (52, 104, 86),
    'black': (8, 24, 32),
    "green_bright": (120, 200, 80),    # Zona movimiento
    "red_bright": (200, 80, 80),       # Zona ataque  
    "yellow_bright": (255, 220, 80),   # Seleccionada
    "blue_bright": (100, 150, 255),    # Hover
}

class PanelAtaques:
    def __init__(self, aliados, x= 0, y=ALTO_MAPA, ancho=ANCHO_PANTALLA, alto =ALTO_PANEL):
        self.rect = pygame.Rect(x, y, ancho, alto)
        
        # Inizializzazione dei font
        self.fuente_titulo = pygame.font.SysFont("Arial", 22, bold=True)
        self.fuente_habs = pygame.font.SysFont("Arial", 16, bold=True)
        self.fuente_stats = pygame.font.SysFont("Arial", 14)
        
        self.ataques_actuales = []
        self.rects_botones = []
        self.indice_seleccionado = -1

        # Colori del pannello
        self.color_fondo = (30, 30, 30)
        self.color_borde = (180, 180, 180)
        self.color_texto = (255, 255, 255)
        self.color_boton = (70, 70, 90)
        self.color_seleccionado = (200, 150, 0)

        # Lista de aliados para mostrar sus vidas
        self.aliados = aliados

    def actualizar_jugador(self, jugador_actual):
        """Riceve il personaggio attuale e filtra i suoi attacchi in base all'energia."""
        self.ataques_actuales = []
        self.indice_seleccionado = -1 
        
        if jugador_actual.equipo == "jugador":
            for ataque in jugador_actual.ataques:
                if jugador_actual.capacidad_aguante >= ataque.coste():
                    self.ataques_actuales.append(ataque)

    def dibujar(self, pantalla, ronda, personaje_actual):
        """Disegna lo sfondo, le barre e i bottoni."""
        if personaje_actual is None:
            return 
        pygame.draw.rect(pantalla, self.color_fondo, self.rect)
        pygame.draw.rect(pantalla, self.color_borde, self.rect, 3)

        txt_turno = self.fuente_titulo.render(f"Ronda {ronda} - Turno: {personaje_actual.nombre}", True, self.color_texto)
        pantalla.blit(txt_turno, (self.rect.x + 15, self.rect.y + 10))

        if personaje_actual.equipo != "jugador":
            txt_espera = self.fuente_titulo.render("Esperando al enemigo...", True, (150, 150, 150))
            pantalla.blit(txt_espera, (self.rect.x + 15, self.rect.y + 60))
        else:
            # Barra della Vita
            ancho_barra = 200
            porcentaje_vida = max(0, personaje_actual.hp_actual / personaje_actual.hp_max)
            pygame.draw.rect(pantalla, (100, 0, 0), (self.rect.x + 15, self.rect.y + 45, ancho_barra, 15))
            pygame.draw.rect(pantalla, (255, 50, 50), (self.rect.x + 15, self.rect.y + 45, ancho_barra * porcentaje_vida, 15))
            
            # Barra dell'Aguante (Energia)
            porcentaje_aguante = max(0, personaje_actual.capacidad_aguante / (personaje_actual.aguante*2))
            pygame.draw.rect(pantalla, (0, 100, 0), (self.rect.x + 15, self.rect.y + 65, ancho_barra, 15))
            pygame.draw.rect(pantalla, (50, 255, 50), (self.rect.x + 15, self.rect.y + 65, ancho_barra * porcentaje_aguante, 15))

            # Disposizione dei bottoni su due colonne
            self.rects_botones.clear()
            margen_x = 15
            margen_y = 100
            ancho_boton = (self.rect.width - 50) // 2
            alto_boton = 55

            font = pygame.font.SysFont("consolas", 20)

            for aliado in self.aliados:
                pantalla.blit(font.render(f"{aliado.nombre} HP:{int(aliado.hp_actual)}/{aliado.hp_max}", True, GB_COLORS["white"]), (670, 470+(self.aliados.index(aliado)+1)*50))


            pantalla.blit(font.render(f"Espacio: Mover", True, GB_COLORS["white"]), (420, 520))
            pantalla.blit(font.render(f"Enter: Pasa Turno", True, GB_COLORS["white"]), (420, 570))
            contador = 0
            for j in range(4):
                for i in personaje_actual.ataques:
                    contador += 1

                    pantalla.blit(font.render(f"{contador}:{i.nombre()} C->{i.coste()}  D->{i.potencia()}", True, GB_COLORS["white"]), (20, 560+((contador/2)*50)))
                '''
                columna = i % 2
                fila = i // 2
                x_boton = self.rect.x + margen_x + columna * (ancho_boton + 20)
                y_boton = self.rect.y + margen_y + fila * (alto_boton + 10)
                
                rect_boton = pygame.Rect(x_boton, y_boton, ancho_boton, alto_boton)
                self.rects_botones.append(rect_boton)
                
                color = self.color_seleccionado if i == self.indice_seleccionado else self.color_boton
                pygame.draw.rect(pantalla, color, rect_boton)
                pygame.draw.rect(pantalla, self.color_borde, rect_boton, 1)
                
                # Testo dell'attacco con i veri dati (Nome e Potenza)
                txt_hab = self.fuente_habs.render(f"[{i+1}] {ataque.nombre()} (Poder: {ataque.potencia()})", True, self.color_texto)
                pantalla.blit(txt_hab, (x_boton + 10, y_boton + 8))
                
                # Testo delle statistiche (Costo e Descrizione)
                txt_stats = self.fuente_stats.render(f"Coste Aguante: {ataque.coste()} | {ataque.descripcion()}", True, (200, 200, 200))
                pantalla.blit(txt_stats, (x_boton + 10, y_boton + 30))
                '''

    def detectar_clic(self, pos_raton):
        """Restituisce True se clicchi su un attacco valido."""
        for i, rect in enumerate(self.rects_botones):
            if rect.collidepoint(pos_raton):
                self.indice_seleccionado = i
                return True
        return False

    def detectar_tecla(self, tecla):
        """Restituisce True se premi un numero corrispondente all'attacco."""
        if pygame.K_1 <= tecla <= pygame.K_9:
            indice = tecla - pygame.K_1
            if indice < len(self.ataques_actuales):
                self.indice_seleccionado = indice
                return True
        return False

    def obtener_ataque_seleccionado(self):
        """Restituisce l'oggetto attacco che hai appena selezionato."""
        if 0 <= self.indice_seleccionado < len(self.ataques_actuales):
            return self.ataques_actuales[self.indice_seleccionado]
        return None