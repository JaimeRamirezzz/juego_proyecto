class Combat_Manager:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        # Decidimos quién empieza (por ejemplo, el jugador)
        self.player.turn = True
        self.enemy.turn = False

    def next_turn(self):
        # El switch: lo que sea True pasa a False y viceversa
        self.player.turn = not self.player.turn
        self.enemy.turn = not self.enemy.turn
        
        print(f" Turn({self.player.turn}) / Enemigo({self.enemy.turn}) ---")
