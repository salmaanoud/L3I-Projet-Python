import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys

# Ajout du dossier src au chemin de recherche
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des fonctions du projet
from library.explorateur import lister_fichiers_musicaux
from library.metadata import extract_metadata
from library.playlist_xspf import generer_playlist_par_defaut

# Classe de l'interface graphique
class MusicGUI:
    def __init__(self, fenetre):
        self.fenetre = fenetre

        # Configuration de la fenetre
        self.fenetre.title("Gestionnaire de musique MP3/FLAC")
        self.fenetre.geometry("900x600")

        # Creation du bouton
        self.bouton_dossier = tk.Button(
            self.fenetre,
            text="Choisir un dossier",
            command=self.choisir_dossier
        )
        self.bouton_dossier.pack(pady=20)

        # Bouton pour generer la playlist par defaut
        self.bouton_playlist = tk.Button(
            self.fenetre,
            text="Generer la playlist par defaut",
            command=self.generer_playlist
        )
        self.bouton_playlist.pack(pady=5)

        # Creation de l'arborescence des fichiers musicaux
        self.tableau = ttk.Treeview(
            self.fenetre,
            columns=("format",),
            show="tree headings"
        )

        # Definition des colonnes
        self.tableau.heading("#0", text="Nom du fichier / Dossier")
        self.tableau.heading("format", text="Format")

        # Dimensions des colonnes
        self.tableau.column("#0", width=500)
        self.tableau.column("format", width=100)

        # Affichage du tableau
        self.tableau.pack(fill="both", expand=True, padx=20, pady=10)

        # Detection de la selection d'un morceau
        self.tableau.bind("<<TreeviewSelect>>", self.afficher_metadonnees)

        # Creation de la zone des metadonnees
        self.zone_infos = ttk.LabelFrame(
            self.fenetre,
            text="Informations du morceau"
        )
        self.zone_infos.pack(fill="x", padx=20, pady=10)

        # Creation des champs d'informations
        self.label_titre = ttk.Label(self.zone_infos, text="Titre :")
        self.label_titre.pack(anchor="w", padx=10, pady=3)

        self.label_artiste = ttk.Label(self.zone_infos, text="Artiste :")
        self.label_artiste.pack(anchor="w", padx=10, pady=3)

        self.label_album = ttk.Label(self.zone_infos, text="Album :")
        self.label_album.pack(anchor="w", padx=10, pady=3)

        self.label_duree = ttk.Label(self.zone_infos, text="Duree :")
        self.label_duree.pack(anchor="w", padx=10, pady=3)

    # Methode pour choisir un dossier
    def choisir_dossier(self):
        dossier = filedialog.askdirectory()

        if dossier:
            # Recherche des fichiers MP3 et FLAC
            fichiers = lister_fichiers_musicaux(dossier)

            # Suppression des anciennes lignes
            for ligne in self.tableau.get_children():
                self.tableau.delete(ligne)

            # Creation du dossier principal
            racine = self.tableau.insert(
                "",
                "end",
                text=os.path.basename(os.path.normpath(dossier)),
                open=True
            )

            # Dictionnaire des dossiers deja crees
            dossiers = {".": racine}

            # Ajout des fichiers dans l'arborescence
            for fichier in fichiers:
                chemin_relatif = os.path.relpath(fichier, dossier)
                parties = chemin_relatif.split(os.sep)

                parent = racine
                chemin_dossier = "."

                # Creation des sous-dossiers
                for nom_dossier in parties[:-1]:
                    chemin_dossier = os.path.join(chemin_dossier, nom_dossier)

                    if chemin_dossier not in dossiers:
                        dossiers[chemin_dossier] = self.tableau.insert(
                            parent,
                            "end",
                            text=nom_dossier,
                            open=True
                        )

                    parent = dossiers[chemin_dossier]

                # Ajout du fichier musical
                nom = os.path.basename(fichier)
                format_fichier = os.path.splitext(fichier)[1].lower()

                self.tableau.insert(
                    parent,
                    "end",
                    iid=fichier,
                    text=nom,
                    values=(format_fichier,)
                )

            # Reinitialisation des informations
            self.effacer_metadonnees()

    # Generation de la playlist par defaut
    def generer_playlist(self):
        dossier = filedialog.askdirectory(
            title="Choisir un dossier pour la playlist"
        )

        if not dossier:
            return

        try:
            chemin_playlist = generer_playlist_par_defaut(dossier)

            messagebox.showinfo(
                "Playlist generee",
                f"La playlist a ete creee :\n{os.path.abspath(chemin_playlist)}"
            )

        except Exception as erreur:
            messagebox.showerror(
                "Erreur",
                f"Impossible de generer la playlist :\n{erreur}"
            )

    # Methode pour effacer les metadonnees
    def effacer_metadonnees(self):
        self.label_titre.config(text="Titre :")
        self.label_artiste.config(text="Artiste :")
        self.label_album.config(text="Album :")
        self.label_duree.config(text="Duree :")

    # Methode pour afficher les metadonnees
    def afficher_metadonnees(self, event):
        selection = self.tableau.selection()

        if selection:
            chemin = selection[0]

            # Verification que la selection est un fichier musical
            if not os.path.isfile(chemin):
                self.effacer_metadonnees()
                return

            try:
                morceau = extract_metadata(chemin)

                # Affichage des informations dans la fenetre
                self.label_titre.config(
                    text="Titre : " + str(morceau.title)
                )
                self.label_artiste.config(
                    text="Artiste : " + str(morceau.artist)
                )
                self.label_album.config(
                    text="Album : " + str(morceau.album)
                )

                minutes = int(morceau.duration // 60)
                secondes = int(morceau.duration % 60)

                self.label_duree.config(
                    text=f"Duree : {minutes}:{secondes:02d}"
                )

            # Affichage d'un message en cas d'erreur
            except (ValueError, OSError) as erreur:
                self.effacer_metadonnees()
                messagebox.showerror("Erreur", str(erreur))


# Creation de la fenetre principale
fenetre = tk.Tk()

# Creation de l'objet interface graphique
application = MusicGUI(fenetre)

# Affichage de la fenetre
fenetre.mainloop()
