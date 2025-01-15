import tkinter as tk
import time
import random

class BatailleNavaleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ----- Taille fixe de la fenêtre -----
        self.geometry("800x600")
        self.resizable(False, False)
        # -------------------------------------

        self.title("Bataille Navale")

        # Variable qui stocke la difficulté ("facile" ou "difficile")
        self.difficulty = None

        # Indique si on est en phase de placement ou de jeu
        self.placing_phase = True

        # Indique si la partie est terminée
        self.game_over = False

        # Le joueur peut-il cliquer ? (pour bloquer les clics quand l'IA joue)
        self.player_can_play = True

        # Variables pour le chrono
        self.start_time = 0.0
        self.end_time = 0.0

        # Orientation du navire en cours de placement
        self.orientation_var = tk.StringVar(value="Horizontal")

        # Liste des navires à placer pour le joueur
        self.ships_to_place = []

        # Index du navire à placer
        self.current_ship_index = 0

        # Tableaux internes : 0=vide, 1=navire, 2=raté, 3=touché
        self.player_board = []
        self.computer_board = []

        # Détails des navires
        self.player_ships_details = []
        self.computer_ships_details = []

        # Ensemble des tirs déjà effectués par l’ordinateur
        self.computer_shots_done = set()

        # Stats de tirs
        self.player_hits = 0
        self.player_misses = 0
        self.computer_hits = 0
        self.computer_misses = 0

        # Dernier tir réussi de l'ordi (pour la difficulté "difficile")
        self.last_computer_hit = None

        # Label indiquant le tour
        self.turn_label_var = tk.StringVar(value="")

        # On crée 3 frames principaux : Accueil, Jeu, Fin
        self.frameAccueil = tk.Frame(self, bg="#66B2FF")
        self.frameJeu = tk.Frame(self, bg="#88CCFF")
        self.frameFin = tk.Frame(self, bg="#66B2FF")

        self.create_frame_accueil()
        self.create_frame_jeu()
        self.create_frame_fin()

        # Au démarrage, on affiche l'écran d'accueil
        self.show_frame(self.frameAccueil)

    # ---------------------------------------------------------------------
    # Gestion de l'affichage des frames (Accueil, Jeu, Fin)
    # ---------------------------------------------------------------------
    def show_frame(self, frame_to_show):
        """
        Masque tous les frames et n'affiche que frame_to_show.
        """
        for fr in [self.frameAccueil, self.frameJeu, self.frameFin]:
            fr.pack_forget()
        frame_to_show.pack(fill="both", expand=True)

    # ---------------------------------------------------------------------
    # ÉCRAN D'ACCUEIL : sélection de difficulté, bouton Lancer
    # ---------------------------------------------------------------------
    def create_frame_accueil(self):
        self.frameAccueil.config(width=600, height=400)

        title_label = tk.Label(
            self.frameAccueil, 
            text="Bataille Navale", 
            bg="#66B2FF",
            fg="white",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=30)

        difficulty_label = tk.Label(
            self.frameAccueil,
            text="Choisissez la difficulté :",
            bg="#66B2FF",
            fg="white",
            font=("Arial", 14)
        )
        difficulty_label.pack(pady=10)

        # Frame boutons de difficulté
        diff_buttons_frame = tk.Frame(self.frameAccueil, bg="#66B2FF")
        diff_buttons_frame.pack(pady=5)

        # Boutons radio pour la difficulté
        self.difficulty_var = tk.StringVar(value="facile")
        radio_facile = tk.Radiobutton(
            diff_buttons_frame, text="Facile", 
            variable=self.difficulty_var, value="facile",
            bg="#66B2FF",
            fg="black",
            selectcolor="#BBDDEE",
            font=("Arial", 12)
        )
        radio_difficile = tk.Radiobutton(
            diff_buttons_frame, text="Difficile",
            variable=self.difficulty_var, value="difficile",
            bg="#66B2FF",
            fg="black",
            selectcolor="#BBDDEE",
            font=("Arial", 12)
        )
        radio_facile.pack(side="left", padx=10)
        radio_difficile.pack(side="left", padx=10)

        # Bouton "Lancer la partie"
        start_button = tk.Button(
            self.frameAccueil,
            text="Lancer la partie",
            bg="#0055AA",
            fg="white",
            font=("Arial", 14, "bold"),
            command=self.on_start_game_clicked
        )
        start_button.pack(pady=20)

    def on_start_game_clicked(self):
        """
        Appelé quand on clique sur "Lancer la partie" depuis l'écran d'accueil.
        Initialise la difficulté (facile/difficile), puis passe à l'écran de jeu.
        """
        self.difficulty = self.difficulty_var.get()  # "facile" ou "difficile"
        self.reset_game_variables()  # Initialise tous les tableaux, navires, etc.
        self.show_frame(self.frameJeu)

    def reset_game_variables(self):
        """
        Initialise / réinitialise toutes les variables nécessaires à la partie.
        """
        self.placing_phase = True
        self.game_over = False
        self.player_can_play = True  # Le joueur peut cliquer tant qu'on n'a pas passé la main à l'IA

        # Chrono
        self.start_time = 0.0
        self.end_time = 0.0

        # Orientation par défaut
        self.orientation_var.set("Horizontal")

        # Liste des navires à placer
        self.ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]
        self.current_ship_index = 0

        # Boards
        self.player_board = [[0]*10 for _ in range(10)]
        self.computer_board = [[0]*10 for _ in range(10)]

        # Navires détaillés
        self.player_ships_details = []
        self.computer_ships_details = []

        self.computer_shots_done = set()

        # Stats de tirs
        self.player_hits = 0
        self.player_misses = 0
        self.computer_hits = 0
        self.computer_misses = 0

        # Dernier tir réussi de l'ordi
        self.last_computer_hit = None

        # On nettoie tous les widgets de la frameJeu (grilles, labels, etc.)
        for child in self.frameJeu.winfo_children():
            child.destroy()

        # On recrée la structure de la frameJeu
        self.create_frame_jeu_content()

    # ---------------------------------------------------------------------
    # ÉCRAN DE JEU : on sépare la création en deux parties :
    #   1) create_frame_jeu() initial (appelé dans __init__)
    #   2) create_frame_jeu_content() qu'on appelle aussi en reset
    # ---------------------------------------------------------------------
    def create_frame_jeu(self):
        """
        Crée la frameJeu une seule fois (structure de base).
        Mais le contenu principal (grilles, labels, etc.) est géré
        par create_frame_jeu_content(), afin qu'on puisse le recréer au reset.
        """
        self.frameJeu.config(width=800, height=600)

    def create_frame_jeu_content(self):
        """
        Construit le contenu à l'intérieur de la frameJeu.
        On l'appelle au lancement ET au reset.
        """
        # Label principal d'info (en haut)
        self.info_label = tk.Label(
            self.frameJeu, 
            text="", 
            bg="#88CCFF", 
            fg="black",
            font=("Arial", 12, "italic")
        )
        self.info_label.pack(pady=5)

        # Label tour
        self.turn_label = tk.Label(
            self.frameJeu,
            textvariable=self.turn_label_var,
            bg="#88CCFF",
            fg="black",
            font=("Arial", 14, "bold")
        )
        self.turn_label.pack(pady=5)

        # Frame global pour tout le plateau
        boards_frame = tk.Frame(self.frameJeu, bg="#88CCFF")
        boards_frame.pack()

        # Frame Joueur
        player_frame = tk.Frame(boards_frame, bg="#88CCFF")
        player_frame.grid(row=0, column=0, padx=20, pady=10)

        # Création de la grille Joueur
        self.player_buttons_frame = tk.Frame(player_frame, bg="#88CCFF")
        self.player_buttons_frame.pack()

        self.player_buttons = self.create_grid(self.player_buttons_frame, is_player=True)

        # Label "Bateaux coulés (Joueur)" en dessous
        self.sunk_ships_label_player = tk.Label(
            player_frame,
            text="Bateaux coulés (Joueur) : (aucun)",
            bg="#88CCFF",
            fg="blue",
            font=("Arial", 10),
            wraplength=150,   # On force un retour à la ligne
            justify="left"
        )
        self.sunk_ships_label_player.pack(pady=5)

        # Frame Ordinateur
        computer_frame = tk.Frame(boards_frame, bg="#88CCFF")
        computer_frame.grid(row=0, column=1, padx=20, pady=10)

        # Création de la grille Ordinateur
        self.computer_buttons_frame = tk.Frame(computer_frame, bg="#88CCFF")
        self.computer_buttons_frame.pack()

        self.computer_buttons = self.create_grid(self.computer_buttons_frame, is_player=False)

        # Label "Bateaux coulés (Ordinateur)" en dessous
        self.sunk_ships_label_computer = tk.Label(
            computer_frame,
            text="Bateaux coulés (Ordinateur) : (aucun)",
            bg="#88CCFF",
            fg="red",
            font=("Arial", 10),
            wraplength=150,   # Retour à la ligne
            justify="left"
        )
        self.sunk_ships_label_computer.pack(pady=5)

        # Frame bas pour l'orientation
        self.orientation_frame = tk.Frame(self.frameJeu, bg="#88CCFF")
        self.orientation_frame.pack(pady=5)

        orientation_label = tk.Label(
            self.orientation_frame, text="Orientation :", 
            bg="#88CCFF", fg="black", font=("Arial", 12)
        )
        orientation_label.pack(side="left", padx=5)

        radio_h = tk.Radiobutton(
            self.orientation_frame, text="Horizontal", 
            variable=self.orientation_var, value="Horizontal",
            bg="#88CCFF", selectcolor="#BBDDEE"
        )
        radio_v = tk.Radiobutton(
            self.orientation_frame, text="Vertical", 
            variable=self.orientation_var, value="Vertical",
            bg="#88CCFF", selectcolor="#BBDDEE"
        )
        radio_h.pack(side="left", padx=5)
        radio_v.pack(side="left", padx=5)

    def create_grid(self, parent, is_player=True):
        """
        Crée une grille 10x10 de boutons (dans 'parent').
        """
        buttons = []
        for row in range(10):
            row_buttons = []
            for col in range(10):
                color = "#7EC8E3" if is_player else "#72B2D6"
                btn = tk.Button(
                    parent,
                    width=3,
                    height=1,
                    bg=color,
                    text="",
                    font=("Arial", 10),
                    command=lambda r=row, c=col: self.on_cell_click(r, c, is_player)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
                row_buttons.append(btn)
            buttons.append(row_buttons)
        return buttons

    def on_cell_click(self, row, col, is_player):
        # Si la partie est finie ou si le joueur ne peut pas jouer (tour de l'ordi), on ignore
        if self.game_over or not self.player_can_play:
            return

        if self.placing_phase:
            # Phase de placement
            if is_player:
                self.place_player_ship(row, col)
            else:
                self.set_info("Vous ne pouvez pas encore tirer, placez vos navires.")
        else:
            # Phase de tir
            if not is_player:
                # Tir du joueur sur la grille de l'ordinateur
                self.player_shoot_computer(row, col)
            else:
                self.set_info("Ceci est votre propre grille.")

    def place_player_ship(self, row, col):
        # Vérif si on a encore des navires à placer
        if self.current_ship_index >= len(self.ships_to_place):
            self.set_info("Tous vos navires sont déjà placés.")
            return

        ship_name, ship_size = self.ships_to_place[self.current_ship_index]
        orientation = self.orientation_var.get()  # Horizontal ou Vertical

        if self.can_place_ship(self.player_board, row, col, ship_size, orientation):
            coords = self.set_ship(self.player_board, row, col, ship_size, orientation, is_player=True)
            # On enregistre le navire
            self.player_ships_details.append({
                'name': ship_name,
                'size': ship_size,
                'coordinates': coords,
                'hits': 0,
                'sunk': False
            })
            self.current_ship_index += 1

            if self.current_ship_index >= len(self.ships_to_place):
                # Fin de placement
                self.placing_phase = False
                self.set_info("Vos navires sont placés. Commencez à tirer sur la grille ennemie !")

                # On supprime les widgets d'orientation
                for widget in self.orientation_frame.winfo_children():
                    widget.destroy()

                # Placement aléatoire ordi
                self.place_computer_ships_randomly()

                # La phase de tir va commencer => on lance le chrono
                self.start_time = time.time()

                # Indique le tour
                self.turn_label_var.set("Au tour du Joueur")
        else:
            self.set_info(f"Impossible de placer le {ship_name} ({ship_size} cases) ici.")

    def can_place_ship(self, board, row, col, size, orientation):
        if orientation == "Horizontal":
            if col + size > 10:
                return False
            for c in range(col, col + size):
                if board[row][c] != 0:
                    return False
        else:  # Vertical
            if row + size > 10:
                return False
            for r in range(row, row + size):
                if board[r][col] != 0:
                    return False
        return True

    def set_ship(self, board, row, col, size, orientation, is_player=False):
        coords = []
        if orientation == "Horizontal":
            for c in range(col, col + size):
                board[row][c] = 1
                coords.append((row, c))
                if is_player:
                    self.player_buttons[row][c].configure(bg="#0033CC")  # Couleur plus sombre
        else:
            for r in range(row, row + size):
                board[r][col] = 1
                coords.append((r, col))
                if is_player:
                    self.player_buttons[r][col].configure(bg="#0033CC")
        return coords

    def place_computer_ships_randomly(self):
        ships = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]
        self.computer_ships_details = []
        for name, size in ships:
            placed = False
            while not placed:
                orientation = random.choice(["Horizontal", "Vertical"])
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                if self.can_place_ship(self.computer_board, row, col, size, orientation):
                    coords = self.set_ship(self.computer_board, row, col, size, orientation, is_player=False)
                    self.computer_ships_details.append({
                        'name': name,
                        'size': size,
                        'coordinates': coords,
                        'hits': 0,
                        'sunk': False
                    })
                    placed = True

    # ---------------------------------------------------------------------
    # Tirs / phase de jeu
    # ---------------------------------------------------------------------
    def player_shoot_computer(self, row, col):
        if self.computer_board[row][col] in [2, 3]:
            self.set_info("Vous avez déjà tiré ici.")
            return

        # Quand le joueur tire, on empêche de cliquer jusqu'à ce que l'ordi ait joué
        self.player_can_play = False

        if self.computer_board[row][col] == 1:
            # Touché
            self.computer_board[row][col] = 3
            self.computer_buttons[row][col].configure(text="X", fg="red")
            self.player_hits += 1
            self.update_ship_hit(self.computer_ships_details, row, col, is_computer=True)
            self.set_info("Touché !")
        else:
            # Raté
            self.computer_board[row][col] = 2
            self.computer_buttons[row][col].configure(text="O", fg="blue")
            self.player_misses += 1
            self.set_info("Raté...")

        # Vérifier si la partie est terminée
        if self.all_ships_sunk(self.computer_ships_details):
            self.end_game(winner="Joueur")
            return

        # Sinon, c'est au tour de l'Ordinateur (on attend 0.5s)
        self.turn_label_var.set("Au tour de l'Ordinateur")
        self.after(500, self.computer_shoot_player)

    def computer_shoot_player(self):
        if self.game_over:
            return

        # Ordinateur joue
        if self.difficulty == "difficile" and self.last_computer_hit is not None:
            row, col = self.find_adjacent_shot(*self.last_computer_hit)
            if row is None:
                row, col = self.random_shot()
        else:
            row, col = self.random_shot()

        self.computer_shots_done.add((row, col))
        cell_value = self.player_board[row][col]

        if cell_value == 1:
            # Touché
            self.player_board[row][col] = 3
            self.player_buttons[row][col].configure(text="X", fg="red")
            self.computer_hits += 1
            self.update_ship_hit(self.player_ships_details, row, col, is_computer=False)
            self.set_info("L'Ordinateur a tiré et vous a touché !")

            if self.difficulty == "difficile":
                self.last_computer_hit = (row, col)
        else:
            # Raté
            if cell_value not in [2, 3]:
                self.player_board[row][col] = 2
                self.player_buttons[row][col].configure(text="O", fg="blue")
            self.computer_misses += 1
            self.set_info("L'Ordinateur a tiré et a raté.")
            if self.difficulty == "difficile":
                self.last_computer_hit = None

        # Vérifier si la partie est terminée
        if self.all_ships_sunk(self.player_ships_details):
            self.end_game(winner="Ordinateur")
            return

        # Retour au joueur
        self.turn_label_var.set("Au tour du Joueur")
        self.player_can_play = True  # On ré-autorise le joueur à cliquer

    def random_shot(self):
        valid = False
        row = col = 0
        while not valid:
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            if (row, col) not in self.computer_shots_done:
                valid = True
        return (row, col)

    def find_adjacent_shot(self, row, col):
        candidates = []
        # up
        if row > 0 and (row-1, col) not in self.computer_shots_done:
            candidates.append((row-1, col))
        # down
        if row < 9 and (row+1, col) not in self.computer_shots_done:
            candidates.append((row+1, col))
        # left
        if col > 0 and (row, col-1) not in self.computer_shots_done:
            candidates.append((row, col-1))
        # right
        if col < 9 and (row, col+1) not in self.computer_shots_done:
            candidates.append((row, col+1))

        if not candidates:
            return (None, None)
        return random.choice(candidates)

    def update_ship_hit(self, ships_details, row, col, is_computer):
        for ship in ships_details:
            if (row, col) in ship['coordinates']:
                ship['hits'] += 1
                if ship['hits'] == ship['size']:
                    ship['sunk'] = True
                    self.reveal_sunk_ship(ship, is_computer)
                break

        self.update_sunk_labels()

    def reveal_sunk_ship(self, ship, is_computer):
        for (r, c) in ship['coordinates']:
            if is_computer:
                self.computer_buttons[r][c].configure(bg="dim gray", fg="white", text="X")
            else:
                self.player_buttons[r][c].configure(bg="dim gray", fg="white", text="X")

    def update_sunk_labels(self):
        sunk_player = [ship['name'] for ship in self.player_ships_details if ship['sunk']]
        sunk_computer = [ship['name'] for ship in self.computer_ships_details if ship['sunk']]

        if sunk_player:
            txt_pl = "Bateaux coulés (Joueur) : " + ", ".join(sunk_player)
        else:
            txt_pl = "Bateaux coulés (Joueur) : (aucun)"

        if sunk_computer:
            txt_co = "Bateaux coulés (Ordinateur) : " + ", ".join(sunk_computer)
        else:
            txt_co = "Bateaux coulés (Ordinateur) : (aucun)"

        self.sunk_ships_label_player.config(text=txt_pl)
        self.sunk_ships_label_computer.config(text=txt_co)

    def all_ships_sunk(self, ships_details):
        return all(ship['sunk'] for ship in ships_details)

    def set_info(self, message):
        self.info_label.config(text=message)

    # ---------------------------------------------------------------------
    # ÉCRAN DE FIN
    # ---------------------------------------------------------------------
    def create_frame_fin(self):
        self.frameFin.config(width=600, height=400)

        self.end_title_label = tk.Label(
            self.frameFin,
            text="Fin de la partie",
            bg="#66B2FF",
            fg="white",
            font=("Arial", 24, "bold")
        )
        self.end_title_label.pack(pady=30)

        self.end_info_label = tk.Label(
            self.frameFin,
            text="",
            bg="#66B2FF",
            fg="white",
            font=("Arial", 12),
            justify="center"   # On centre le texte
        )
        self.end_info_label.pack(pady=10)

        # Boutons Rejouer / Quitter
        buttons_frame = tk.Frame(self.frameFin, bg="#66B2FF")
        buttons_frame.pack(pady=20)

        self.end_replay_button = tk.Button(
            buttons_frame,
            text="Rejouer",
            bg="#0055AA",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.on_end_replay_clicked
        )
        self.end_replay_button.pack(side="left", padx=10)

        self.end_quit_button = tk.Button(
            buttons_frame,
            text="Quitter",
            bg="#AA0000",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.quit
        )
        self.end_quit_button.pack(side="left", padx=10)

    def end_game(self, winner):
        self.game_over = True
        self.end_time = time.time()

        # On calcule la durée
        duration = self.end_time - self.start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        info_text = []
        info_text.append(f"Vainqueur : {winner}")
        info_text.append(f"Temps de la partie : {minutes} min {seconds} s")

        info_text.append("")
        info_text.append("Statistiques de tir :")
        info_text.append(f"  Joueur : {self.player_hits} touches / {self.player_misses} ratés")
        info_text.append(f"  Ordinateur : {self.computer_hits} touches / {self.computer_misses} ratés")

        # Navires coulés
        sunk_player = [ship['name'] for ship in self.player_ships_details if ship['sunk']]
        sunk_computer = [ship['name'] for ship in self.computer_ships_details if ship['sunk']]

        info_text.append("")
        info_text.append("Navires coulés par le Joueur : " + ", ".join(sunk_computer) if sunk_computer else "Navires coulés par le Joueur : (aucun)")
        info_text.append("Navires coulés par l'Ordinateur : " + ", ".join(sunk_player) if sunk_player else "Navires coulés par l'Ordinateur : (aucun)")

        final_text = "\n".join(info_text)
        self.end_info_label.config(text=final_text)

        # On affiche l'écran de fin
        self.show_frame(self.frameFin)

    def on_end_replay_clicked(self):
        """
        Bouton "Rejouer" sur l'écran de fin : on revient à l'écran d'accueil,
        et on réinitialise tout pour une nouvelle partie.
        """
        self.show_frame(self.frameAccueil)

    # ---------------------------------------------------------------------
    # Méthodes système
    # ---------------------------------------------------------------------
    def quit(self):
        self.destroy()

# -------------------------------------------------------------------------
# Lancement de l'application
# -------------------------------------------------------------------------
if __name__ == "__main__":
    app = BatailleNavaleApp()
    app.mainloop()
