import tkinter as tk
from tkinter import messagebox
import random

class BatailleNavaleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bataille Navale")
        self.resizable(False, False)

        # ---------------------
        # 1) Variables globales
        # ---------------------

        # Qui joue ? (pour la suite, lors des tirs)
        self.current_player = tk.StringVar(value="Joueur")

        # Phase de placement en cours ?
        self.placing_phase = True

        # Orientation du navire en cours de placement
        self.orientation_var = tk.StringVar(value="Horizontal")

        # Liste des navires à placer (nom, taille).
        # 1 porte-avions (5), 1 croiseur (4), 2 destroyers (3), 2 sous-marins (2)
        self.ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]

        # Index du navire en cours de placement
        self.current_ship_index = 0

        # Représentation interne des plateaux (0 = vide, 1 = navire)
        self.player_board = [[0]*10 for _ in range(10)]
        self.computer_board = [[0]*10 for _ in range(10)]

        # -------------------
        # 2) Création des UI
        # -------------------

        # Frames
        self.player_frame = tk.LabelFrame(self, text="Plateau Joueur", padx=5, pady=5)
        self.computer_frame = tk.LabelFrame(self, text="Plateau Ordinateur", padx=5, pady=5)
        self.control_frame = tk.LabelFrame(self, text="Contrôles", padx=5, pady=5)

        self.player_frame.grid(row=0, column=0, padx=10, pady=10)
        self.computer_frame.grid(row=0, column=1, padx=10, pady=10)
        self.control_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Grilles de boutons
        self.player_buttons = self.create_grid(self.player_frame, is_player=True)
        self.computer_buttons = self.create_grid(self.computer_frame, is_player=False)

        # Panneau de contrôle
        self.create_control_panel()

        # -----------------------------
        # 3) Placement aléatoire IA/ordi
        # -----------------------------
        self.place_computer_ships_randomly()

    def create_grid(self, parent, is_player=True):
        """
        Crée une grille 10x10 de boutons.
        is_player détermine si c’est la grille du joueur ou celle de l’ordinateur.
        """
        buttons = []
        for row in range(10):
            row_buttons = []
            for col in range(10):
                btn = tk.Button(
                    parent,
                    width=3,       # Ajustez la taille du bouton
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
         - Indicateur de tour
         - Bouton 'Nouvelle partie'
         - Bouton 'Rejouer'
         - Radio-boutons pour l'orientation des navires (lors de la phase de placement)
        """

        # Indicateur de tour (nom du joueur dont c’est le tour, réutilisable plus tard)
        self.turn_label = tk.Label(self.control_frame, textvariable=self.current_player)
        self.turn_label.pack(side=tk.LEFT, padx=10)

        # Bouton Nouvelle partie
        self.new_game_button = tk.Button(
            self.control_frame, 
            text="Nouvelle partie",
            command=self.start_new_game
        )
        self.new_game_button.pack(side=tk.LEFT, padx=10)

        # Bouton Rejouer (ou Réinitialiser)
        self.reset_button = tk.Button(
            self.control_frame, 
            text="Rejouer",
            command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Radio-boutons pour l'orientation du navire (Horizontal / Vertical)
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

    def on_cell_click(self, row, col, is_player):
        """
        Gestion du clic sur une cellule.
        - Si on est en phase de placement et que c'est sur le plateau du joueur,
          on tente de placer le prochain navire.
        - Sinon, s’il s’agit d’un clic sur le plateau de l’adversaire (dans la phase de tir),
          on gérera plus tard la logique de tir.
        """
        # Si on est toujours en phase de placement et que c'est le plateau du joueur
        if self.placing_phase and is_player:
            self.place_player_ship(row, col)
        else:
            # Ici on pourrait traiter plus tard la logique de tir
            messagebox.showinfo("Info", f"Cliqué sur ({row}, {col}) | Joueur={is_player}")

    # -----------------------------------------
    # Placement manuel du joueur
    # -----------------------------------------
    def place_player_ship(self, row, col):
        """
        Place le prochain navire du joueur (self.ships_to_place[self.current_ship_index]) 
        en fonction de l’orientation choisie (self.orientation_var) si possible.
        """
        if self.current_ship_index >= len(self.ships_to_place):
            messagebox.showinfo("Info", "Tous vos navires sont déjà placés.")
            return

        ship_name, ship_size = self.ships_to_place[self.current_ship_index]
        orientation = self.orientation_var.get()  # "Horizontal" ou "Vertical"

        if self.can_place_ship(self.player_board, row, col, ship_size, orientation):
            # On place le navire
            self.set_ship(self.player_board, row, col, ship_size, orientation, is_player=True)
            
            # On passe au navire suivant
            self.current_ship_index += 1

            # Vérifier si on a placé tous les navires
            if self.current_ship_index >= len(self.ships_to_place):
                self.placing_phase = False  # Fin de la phase de placement
                messagebox.showinfo("Info", "Tous vos navires sont placés. La partie peut commencer.")
        else:
            messagebox.showwarning("Impossible", 
                                   f"Impossible de placer le {ship_name} ({ship_size} cases) ici.")

    def can_place_ship(self, board, row, col, size, orientation):
        """
        Vérifie si on peut placer un navire de taille 'size' à partir de (row, col)
        sur le board (10x10), selon 'orientation' (Horizontal ou Vertical).
        Retourne True si possible, False sinon.
        """
        if orientation == "Horizontal":
            if col + size > 10:  # Dépasse la grille
                return False
            # Vérifier que toutes les cases [row][col..col+size-1] sont libres (==0)
            for c in range(col, col + size):
                if board[row][c] != 0:
                    return False
        else:  # Vertical
            if row + size > 10:
                return False
            # Vérifier que toutes les cases [row..row+size-1][col] sont libres
            for r in range(row, row + size):
                if board[r][col] != 0:
                    return False

        return True

    def set_ship(self, board, row, col, size, orientation, is_player=False):
        """
        Marque les cases d’un navire sur 'board' comme étant occupées (1).
        Colorie également les boutons correspondant pour le joueur.
        """
        if orientation == "Horizontal":
            for c in range(col, col + size):
                board[row][c] = 1  # Navire
                if is_player:
                    self.player_buttons[row][c].configure(bg="blue")
        else:
            for r in range(row, row + size):
                board[r][col] = 1
                if is_player:
                    self.player_buttons[r][col].configure(bg="blue")

    # -----------------------------------------
    # Placement aléatoire (ordinateur)
    # -----------------------------------------
    def place_computer_ships_randomly(self):
        """
        Place les mêmes navires que le joueur sur le plateau de l’ordinateur (computer_board),
        de manière aléatoire et sans chevauchement.
        """
        ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]

        for ship_name, ship_size in ships_to_place:
            placed = False
            while not placed:
                orientation = random.choice(["Horizontal", "Vertical"])
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                if self.can_place_ship(self.computer_board, row, col, ship_size, orientation):
                    self.set_ship(self.computer_board, row, col, ship_size, orientation, is_player=False)
                    placed = True

    # -----------------------------------------
    # Logique pour démarrer une nouvelle partie
    # -----------------------------------------
    def start_new_game(self):
        """
        Logique pour démarrer une nouvelle partie.
        - Réinitialiser les variables
        - Remettre les grilles à zéro
        - Autoriser à nouveau la phase de placement
        - Re-placer l’ordinateur
        """
        self.reset_game()  # On remet tout à zéro

        self.placing_phase = True
        self.current_ship_index = 0

        # On replace aléatoirement les navires de l’ordi
        self.place_computer_ships_randomly()

        messagebox.showinfo("Nouvelle partie", "Nouvelle partie démarrée. Placez vos navires !")

    def reset_game(self):
        """
        Logique pour réinitialiser la partie (ou rejouer).
        On remet les couleurs d’origine, les tableaux internes, etc.
        """
        # Réinitialiser les tableaux internes
        self.player_board = [[0]*10 for _ in range(10)]
        self.computer_board = [[0]*10 for _ in range(10)]

        # Réinitialiser les boutons
        for row in range(10):
            for col in range(10):
                self.player_buttons[row][col].configure(bg="lightblue")
                self.computer_buttons[row][col].configure(bg="lightgray")

        # Réinitialiser l’état
        self.current_player.set("Joueur")
        self.placing_phase = True
        self.current_ship_index = 0
        self.ships_to_place = [
            ("Porte-avions", 5),
            ("Croiseur", 4),
            ("Destroyer", 3),
            ("Destroyer", 3),
            ("Sous-marin", 2),
            ("Sous-marin", 2)
        ]

        messagebox.showinfo("Rejouer", "La grille a été réinitialisée. Placez vos navires.")

if __name__ == "__main__":
    app = BatailleNavaleApp()
    app.mainloop()
