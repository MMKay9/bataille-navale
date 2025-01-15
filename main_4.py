import tkinter as tk
from tkinter import messagebox
import random

class BatailleNavaleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bataille Navale")
        self.resizable(False, False)

        # ------------------------------------------------
        # 1) Variables globales : phase, orientation, etc.
        # ------------------------------------------------

        # Indique le joueur courant (si jamais on gère des tours plus tard)
        self.current_player = tk.StringVar(value="Joueur")

        # Indique si on est en phase de placement (True) ou en phase de tir (False)
        self.placing_phase = True

        # Variable pour gérer si la partie est terminée
        self.game_over = False

        # Orientation du navire en cours de placement
        self.orientation_var = tk.StringVar(value="Horizontal")

        # Liste des navires à placer pour le joueur
        # (1 porte-avions (5), 1 croiseur (4), 2 destroyers (3), 2 sous-marins (2))
        self.ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]
        self.current_ship_index = 0

        # Représentations internes des plateaux (0 = vide, 1 = navire, 2 = tir raté, 3 = tir touché)
        self.player_board = [[0]*10 for _ in range(10)]
        self.computer_board = [[0]*10 for _ in range(10)]

        # Pour éviter que l’ordinateur retire au même endroit.
        self.computer_shots_done = set()

        # Détails de navires (player / computer) : liste de dicos {name, size, coordinates, hits, sunk}
        self.player_ships_details = []
        self.computer_ships_details = []

        # ------------------------------------
        # 2) Création des UI (frames, boutons)
        # ------------------------------------
        self.player_frame = tk.LabelFrame(self, text="Plateau Joueur", padx=5, pady=5)
        self.computer_frame = tk.LabelFrame(self, text="Plateau Ordinateur", padx=5, pady=5)
        self.control_frame = tk.LabelFrame(self, text="Contrôles", padx=5, pady=5)
        self.info_frame = tk.LabelFrame(self, text="Informations", padx=5, pady=5)

        self.player_frame.grid(row=0, column=0, padx=10, pady=10)
        self.computer_frame.grid(row=0, column=1, padx=10, pady=10)
        self.control_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.info_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Grilles de boutons (10x10) pour chaque plateau
        self.player_buttons = self.create_grid(self.player_frame, is_player=True)
        self.computer_buttons = self.create_grid(self.computer_frame, is_player=False)

        # Panneau de contrôle (orientation, boutons Nouvelle partie/Rejouer, etc.)
        self.create_control_panel()

        # Zone d'information (navires coulés, etc.)
        self.create_info_panel()

        # -----------------------------------------
        # 3) Placement aléatoire des navires de l’ordi
        # -----------------------------------------
        self.place_computer_ships_randomly()

    def create_grid(self, parent, is_player=True):
        """
        Crée une grille 10x10 de boutons. 
        is_player = True => grille du joueur
        is_player = False => grille de l’ordinateur
        """
        buttons = []
        for row in range(10):
            row_buttons = []
            for col in range(10):
                btn = tk.Button(
                    parent,
                    width=3,       # Ajustez la taille selon vos préférences
                    height=1,
                    bg="lightblue" if is_player else "lightgray",
                    command=lambda r=row, c=col: self.on_cell_click(r, c, is_player)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
                row_buttons.append(btn)
            buttons.append(row_buttons)
        return buttons

    def create_control_panel(self):
        """
        Crée le panneau de contrôle avec :
         - Label indiquant le joueur courant
         - Bouton 'Nouvelle partie'
         - Bouton 'Rejouer'
         - Radio-boutons pour orientation (phase de placement)
        """
        # Indicateur de tour
        self.turn_label = tk.Label(self.control_frame, textvariable=self.current_player)
        self.turn_label.pack(side=tk.LEFT, padx=10)

        # Bouton Nouvelle partie
        self.new_game_button = tk.Button(
            self.control_frame, 
            text="Nouvelle partie",
            command=self.start_new_game
        )
        self.new_game_button.pack(side=tk.LEFT, padx=10)

        # Bouton Rejouer (Reset)
        self.reset_button = tk.Button(
            self.control_frame, 
            text="Rejouer",
            command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Radio-boutons pour l'orientation
        orientation_frame = tk.Frame(self.control_frame)
        orientation_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(orientation_frame, text="Orientation :").pack(side=tk.TOP)
        tk.Radiobutton(
            orientation_frame, 
            text="Horizontal", 
            variable=self.orientation_var, 
            value="Horizontal"
        ).pack(side=tk.TOP, anchor=tk.W)
        tk.Radiobutton(
            orientation_frame, 
            text="Vertical", 
            variable=self.orientation_var, 
            value="Vertical"
        ).pack(side=tk.TOP, anchor=tk.W)

    def create_info_panel(self):
        """
        Crée la zone d'information pour afficher les navires coulés (côté joueur et ordinateur).
        """
        # Label d’entête
        info_label = tk.Label(self.info_frame, text="Navires coulés :", font=('Arial', 10, 'bold'))
        info_label.pack(side=tk.TOP, anchor=tk.W)

        # Frame pour lister navires coulés joueur
        self.sunk_player_label = tk.Label(self.info_frame, text="Joueur : (aucun)", fg="blue")
        self.sunk_player_label.pack(side=tk.TOP, anchor=tk.W)

        # Frame pour lister navires coulés ordi
        self.sunk_computer_label = tk.Label(self.info_frame, text="Ordinateur : (aucun)", fg="red")
        self.sunk_computer_label.pack(side=tk.TOP, anchor=tk.W)

    # ------------------------------------------------
    # Événement clic sur une case (joueur ou ordinateur)
    # ------------------------------------------------
    def on_cell_click(self, row, col, is_player):
        """
        Gestion du clic sur la grille.
          - Si on est en phase de placement et qu’on clique sur le plateau Joueur => on place un navire.
          - Sinon, si c’est la grille de l’ordinateur et qu’on n’est plus en phase de placement => tir du joueur.
        - Si la partie est déjà terminée (game_over = True), on ignore le clic.
        """
        if self.game_over:
            # Si le jeu est déjà terminé, on ne fait rien
            messagebox.showinfo("Partie terminée", "La partie est déjà terminée.")
            return

        if self.placing_phase:
            # Phase de placement => on ne place que sur la grille du joueur
            if is_player:
                self.place_player_ship(row, col)
            else:
                messagebox.showinfo("Info", "Vous ne pouvez pas encore tirer. Placez d’abord tous vos navires.")
        else:
            # Phase de tir => on ne tire que sur la grille de l’ordinateur
            if not is_player:
                self.player_shoot_computer(row, col)
            else:
                messagebox.showinfo("Info", "C’est la grille du Joueur, vous devez tirer sur la grille de l’ordinateur.")

    # ------------------------------------------------
    # 4) Placement manuel du joueur
    # ------------------------------------------------
    def place_player_ship(self, row, col):
        """
        Place le navire courant (self.ships_to_place[self.current_ship_index]) 
        en tenant compte de l’orientation choisie.
        """
        if self.current_ship_index >= len(self.ships_to_place):
            messagebox.showinfo("Info", "Tous vos navires sont déjà placés.")
            return

        ship_name, ship_size = self.ships_to_place[self.current_ship_index]
        orientation = self.orientation_var.get()  # "Horizontal" ou "Vertical"

        if self.can_place_ship(self.player_board, row, col, ship_size, orientation):
            # Placement effectif
            coords = self.set_ship(
                board=self.player_board,
                row=row, col=col,
                size=ship_size,
                orientation=orientation,
                is_player=True
            )

            # On enregistre les infos du navire dans player_ships_details
            self.player_ships_details.append({
                'name': ship_name,
                'size': ship_size,
                'coordinates': coords,
                'hits': 0,
                'sunk': False
            })

            self.current_ship_index += 1

            # Vérifier si on a placé tous les navires
            if self.current_ship_index >= len(self.ships_to_place):
                self.placing_phase = False
                messagebox.showinfo("Info", 
                                    "Tous vos navires sont placés. La phase de tir peut commencer.")
        else:
            messagebox.showwarning("Placement impossible",
                                   f"Impossible de placer le {ship_name} ({ship_size} cases) ici.")

    def can_place_ship(self, board, row, col, size, orientation):
        """
        Vérifie si on peut placer un navire de taille 'size' 
        depuis (row, col) selon 'orientation' (Horizontal ou Vertical).
        Retourne True/False.
        """
        if orientation == "Horizontal":
            if col + size > 10:  # dépasse la grille
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
        """
        Marque les cases du navire dans 'board' et colorie les boutons si is_player=True.
        Retourne la liste des coordonnées occupées par le navire.
        """
        coords = []
        if orientation == "Horizontal":
            for c in range(col, col + size):
                board[row][c] = 1  # navire
                coords.append((row, c))
                if is_player:
                    self.player_buttons[row][c].configure(bg="blue")
        else:
            for r in range(row, row + size):
                board[r][col] = 1
                coords.append((r, col))
                if is_player:
                    self.player_buttons[r][col].configure(bg="blue")
        return coords

    # ------------------------------------------------
    # 5) Placement aléatoire des navires de l’ordinateur
    # ------------------------------------------------
    def place_computer_ships_randomly(self):
        """
        Place les navires de la même liste sur le plateau computer_board.
        Mémorise leurs coordonnées dans self.computer_ships_details.
        """
        ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]
        self.computer_ships_details.clear()  # On vide la liste avant de placer

        for ship_name, ship_size in ships_to_place:
            placed = False
            while not placed:
                orientation = random.choice(["Horizontal", "Vertical"])
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                if self.can_place_ship(self.computer_board, row, col, ship_size, orientation):
                    coords = self.set_ship(
                        board=self.computer_board,
                        row=row, col=col,
                        size=ship_size,
                        orientation=orientation,
                        is_player=False
                    )
                    self.computer_ships_details.append({
                        'name': ship_name,
                        'size': ship_size,
                        'coordinates': coords,
                        'hits': 0,
                        'sunk': False
                    })
                    placed = True

    # ------------------------------------------------
    # 6) Phase de jeu : tir du joueur sur l’ordinateur
    # ------------------------------------------------
    def player_shoot_computer(self, row, col):
        """
        Le joueur tire sur (row, col) du plateau de l’ordinateur.
        - On vérifie si c’est un navire (board=1).
        - On marque la case comme touchée (3) ou ratée (2).
        - On met à jour l’affichage du bouton (X rouge pour touche, O bleu pour raté).
        - On met à jour les hits sur le navire. Si un navire est coulé, on l’affiche.
        - Puis on vérifie si la partie est terminée (tous navires ordi coulés ?).
        - Si la partie n’est pas terminée, l’ordinateur tire à son tour.
        """
        # Si la partie est terminée au moment du clic (sécurité), on ne fait rien
        if self.game_over:
            return

        cell_value = self.computer_board[row][col]

        if cell_value == 2 or cell_value == 3:
            # Déjà tiré sur cette case
            messagebox.showinfo("Info", "Vous avez déjà tiré sur cette case.")
            return

        if cell_value == 1:
            # Touché
            self.computer_board[row][col] = 3
            self.computer_buttons[row][col].configure(text="X", fg="red")
            self.update_ship_hit(self.computer_ships_details, row, col, is_computer=True)
        else:
            # Raté
            self.computer_board[row][col] = 2
            self.computer_buttons[row][col].configure(text="O", fg="blue")

        # Vérifier si la partie est terminée (tous les navires de l’ordi coulés ?)
        if self.all_ships_sunk(self.computer_ships_details):
            self.game_over = True
            messagebox.showinfo("Fin de partie", "Bravo, vous avez gagné !")
            return

        # Sinon, l’ordinateur tire à son tour (si la partie n’est pas finie)
        self.computer_shoot_player()

    def all_ships_sunk(self, ships_details):
        """
        Retourne True si tous les navires dans ships_details sont 'sunk'.
        """
        return all(ship['sunk'] for ship in ships_details)

    def update_ship_hit(self, ships_details, row, col, is_computer=False):
        """
        Incrémente le nombre de hits du navire concerné, 
        et vérifie s’il est coulé (hits == size).
        Met à jour l’affichage des navires coulés.
        """
        for ship in ships_details:
            if (row, col) in ship['coordinates']:
                ship['hits'] += 1
                if ship['hits'] == ship['size']:
                    ship['sunk'] = True
                    msg = f"{'Ordinateur' if is_computer else 'Joueur'} : " \
                          f"le navire {ship['name']} est coulé !"
                    messagebox.showinfo("Navire coulé", msg)
                break

        # Mettre à jour la liste des navires coulés dans l’interface
        self.update_sunk_labels()

    def update_sunk_labels(self):
        """
        Met à jour l’affichage des navires coulés pour le joueur et l’ordinateur.
        """
        # Joueur
        sunk_player = [ship['name'] for ship in self.player_ships_details if ship['sunk']]
        if sunk_player:
            text_joueur = "Joueur : " + ", ".join(sunk_player)
        else:
            text_joueur = "Joueur : (aucun)"

        # Ordi
        sunk_computer = [ship['name'] for ship in self.computer_ships_details if ship['sunk']]
        if sunk_computer:
            text_ordi = "Ordinateur : " + ", ".join(sunk_computer)
        else:
            text_ordi = "Ordinateur : (aucun)"

        self.sunk_player_label.config(text=text_joueur)
        self.sunk_computer_label.config(text=text_ordi)

    # ------------------------------------------------
    # 7) Tir de l’ordinateur sur le joueur
    # ------------------------------------------------
    def computer_shoot_player(self):
        """
        L’ordinateur tire aléatoirement sur une case du joueur 
        (qui n’a pas déjà été visée).
        - On récupère row,col aléatoirement jusqu’à trouver une case non visitée.
        - On marque la case touchée ou ratée.
        - On met à jour les hits sur le navire.
        - Puis on vérifie si la partie est terminée.
        """
        if self.game_over:
            return

        valid = False
        while not valid:
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            if (row, col) not in self.computer_shots_done:
                valid = True

        # On enregistre ce tir
        self.computer_shots_done.add((row, col))

        cell_value = self.player_board[row][col]
        if cell_value == 1:
            # Touché
            self.player_board[row][col] = 3
            self.player_buttons[row][col].configure(text="X", fg="red")
            self.update_ship_hit(self.player_ships_details, row, col, is_computer=False)
        else:
            # Raté
            if cell_value in [2, 3]:
                pass
            else:
                self.player_board[row][col] = 2
                self.player_buttons[row][col].configure(text="O", fg="blue")

        # Vérifier si la partie est terminée (tous les navires du joueur coulés ?)
        if self.all_ships_sunk(self.player_ships_details):
            self.game_over = True
            messagebox.showinfo("Fin de partie", "L’ordinateur a gagné...")
            return

    # ------------------------------------------------
    # 8) Nouvelle partie & Réinitialisation
    # ------------------------------------------------
    def start_new_game(self):
        """
        Logique pour démarrer une nouvelle partie :
         - On fait un reset
         - On replace l’IA
         - On repasse en phase de placement
        """
        self.reset_game()
        self.placing_phase = True
        self.current_ship_index = 0
        self.place_computer_ships_randomly()
        messagebox.showinfo("Nouvelle partie", 
                            "Nouvelle partie démarrée. Placez vos navires !")

    def reset_game(self):
        """
        Réinitialise tous les tableaux, variables, boutons, etc.
        """
        # Vider les boards
        self.player_board = [[0]*10 for _ in range(10)]
        self.computer_board = [[0]*10 for _ in range(10)]

        # Vider les details navires
        self.player_ships_details = []
        self.computer_ships_details = []

        # Vider les tirs déjà effectués par l’ordinateur
        self.computer_shots_done = set()

        # Réinitialiser la liste des navires à placer et l’index
        self.ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]
        self.current_ship_index = 0

        # Remettre les boutons visuellement à zéro
        for row in range(10):
            for col in range(10):
                self.player_buttons[row][col].configure(bg="lightblue", text="")
                self.computer_buttons[row][col].configure(bg="lightgray", text="")

        # Réinitialiser les labels
        self.current_player.set("Joueur")
        self.sunk_player_label.config(text="Joueur : (aucun)")
        self.sunk_computer_label.config(text="Ordinateur : (aucun)")

        # Remettre en phase de placement
        self.placing_phase = True

        # Remettre l’état de fin de partie à False
        self.game_over = False

        messagebox.showinfo("Réinitialisation", "La grille a été réinitialisée.")

if __name__ == "__main__":
    app = BatailleNavaleApp()
    app.mainloop()
