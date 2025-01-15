import tkinter as tk
from tkinter import messagebox

class BatailleNavaleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bataille Navale")
        self.resizable(False, False)

        # Variables pour suivre le tour (Joueur / Ordinateur)
        self.current_player = tk.StringVar(value="Joueur")

        # Création des frames principaux
        self.player_frame = tk.LabelFrame(self, text="Plateau Joueur", padx=5, pady=5)
        self.computer_frame = tk.LabelFrame(self, text="Plateau Ordinateur", padx=5, pady=5)
        self.control_frame = tk.LabelFrame(self, text="Contrôles", padx=5, pady=5)

        self.player_frame.grid(row=0, column=0, padx=10, pady=10)
        self.computer_frame.grid(row=0, column=1, padx=10, pady=10)
        self.control_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Création des grilles pour le joueur et pour l'ordinateur
        self.player_buttons = self.create_grid(self.player_frame, is_player=True)
        self.computer_buttons = self.create_grid(self.computer_frame, is_player=False)

        # Création du panneau de contrôle
        self.create_control_panel()

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
                    width=3,       # Ajustez pour changer la taille du bouton
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
        """
        # Indicateur de tour
        self.turn_label = tk.Label(self.control_frame, textvariable=self.current_player)
        self.turn_label.pack(side=tk.LEFT, padx=10)

        # Bouton Nouvelle partie
        self.new_game_button = tk.Button(
            self.control_frame, text="Nouvelle partie",
            command=self.start_new_game
        )
        self.new_game_button.pack(side=tk.LEFT, padx=10)

        # Bouton Rejouer (ou Réinitialiser)
        self.reset_button = tk.Button(
            self.control_frame, text="Rejouer",
            command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)

    def on_cell_click(self, row, col, is_player):
        """
        Gestion du clic sur une cellule.
        Pour l’instant, on se contente d’afficher une boîte de dialogue
        ou de changer la couleur du bouton pour illustrer le concept.
        """
        if is_player:
            messagebox.showinfo("Info", f"Vous avez cliqué sur ({row}, {col}) du plateau Joueur.")
        else:
            messagebox.showinfo("Info", f"Vous avez cliqué sur ({row}, {col}) du plateau Ordinateur.")

        # Exemple de changement de couleur (placeholder)
        # Ici, on peut plus tard mettre la logique d'un tir, etc.
        # Pour la démonstration, on change juste le bouton en rouge.
        if is_player:
            self.player_buttons[row][col].configure(bg="red")
        else:
            self.computer_buttons[row][col].configure(bg="red")

    def start_new_game(self):
        """
        Logique pour démarrer une nouvelle partie.
        Ici, on peut prévoir le placement des navires, réinitialiser la grille, etc.
        """
        messagebox.showinfo("Nouvelle partie", "Ici, on démarre une nouvelle partie.")
        # Placeholder : Réinitialiser ou logiques futures

    def reset_game(self):
        """
        Logique pour réinitialiser la partie (ou rejouer).
        On remet les couleurs d’origine, etc.
        """
        for row in range(10):
            for col in range(10):
                self.player_buttons[row][col].configure(bg="lightblue")
                self.computer_buttons[row][col].configure(bg="lightgray")
        self.current_player.set("Joueur")
        messagebox.showinfo("Rejouer", "La grille a été réinitialisée.")

if __name__ == "__main__":
    app = BatailleNavaleApp()
    app.mainloop()
