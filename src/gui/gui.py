"""
Module : Interface graphique

Rôle :
    Fournir une interface graphique Tkinter pour le gestionnaire
    de fichiers musicaux MP3 et FLAC.

    L'interface permet de choisir un dossier ou un morceau,
    de parcourir une arborescence musicale, d'afficher les
    métadonnées et de générer une playlist au format XSPF.
"""

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


class MusicGUI:
    """
    Rôle :
        Représenter l'interface graphique du gestionnaire musical.

        Cette classe permet de parcourir les fichiers MP3 et FLAC,
        d'afficher leurs métadonnées et de générer des playlists XSPF.

    Attributs :
        fenetre : Fenêtre principale Tkinter.
        tableau : Arborescence des fichiers musicaux.
        cadre_tableau : Conteneur du tableau.
        barre_horizontale : Barre de défilement horizontale.
        zone_infos : Zone d'affichage des métadonnées.
    """

    def __init__(self, fenetre):
        """
        Rôle :
            Initialiser la fenêtre principale et les composants graphiques.

        Arguments :
            fenetre (tk.Tk) : Fenêtre principale de l'application.

        Valeur renvoyée :
            Aucune.
        """
        self.fenetre = fenetre

        # Configuration de la fenêtre
        self.fenetre.title("Gestionnaire de musique MP3/FLAC")
        self.fenetre.geometry("900x600")

        # Création du bouton pour choisir un dossier
        self.bouton_dossier = tk.Button(
            self.fenetre,
            text="Choisir un dossier",
            command=self.choisir_dossier
        )
        self.bouton_dossier.pack(pady=10)

        # Bouton pour choisir directement un morceau
        self.bouton_morceau = tk.Button(
            self.fenetre,
            text="Choisir un morceau",
            command=self.choisir_morceau
        )
        self.bouton_morceau.pack(pady=5)

        # Bouton pour générer la playlist par défaut
        self.bouton_playlist = tk.Button(
            self.fenetre,
            text="Generer la playlist par defaut",
            command=self.generer_playlist
        )
        self.bouton_playlist.pack(pady=5)

        # Création du conteneur pour le tableau
        self.cadre_tableau = ttk.Frame(self.fenetre)
        self.cadre_tableau.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Création de l'arborescence des fichiers musicaux
        self.tableau = ttk.Treeview(
            self.cadre_tableau,
            columns=("format", "titre", "artiste", "album", "duree"),
            show="tree headings"
        )

        # Définition des colonnes
        self.tableau.heading("#0", text="Nom du fichier / Dossier")
        self.tableau.heading("format", text="Format")
        self.tableau.heading("titre", text="Titre")
        self.tableau.heading("artiste", text="Artiste")
        self.tableau.heading("album", text="Album")
        self.tableau.heading("duree", text="Duree")

        # Dimensions des colonnes
        self.tableau.column("#0", width=220, minwidth=150)
        self.tableau.column("format", width=70, minwidth=60)
        self.tableau.column("titre", width=200, minwidth=100)
        self.tableau.column("artiste", width=150, minwidth=100)
        self.tableau.column("album", width=150, minwidth=100)
        self.tableau.column("duree", width=70, minwidth=60)

        # Barre de défilement horizontale
        self.barre_horizontale = ttk.Scrollbar(
            self.cadre_tableau,
            orient="horizontal",
            command=self.tableau.xview
        )
        self.barre_horizontale.pack(side="bottom", fill="x")

        # Liaison de la barre au tableau
        self.tableau.configure(
            xscrollcommand=self.barre_horizontale.set
        )

        # Affichage du tableau
        self.tableau.pack(fill="both", expand=True)

        # Détection de la sélection d'un morceau
        self.tableau.bind(
            "<<TreeviewSelect>>",
            self.afficher_metadonnees
        )

        # Création de la zone des métadonnées
        self.zone_infos = ttk.LabelFrame(
            self.fenetre,
            text="Informations du morceau"
        )
        self.zone_infos.pack(fill="x", padx=20, pady=10)

        # Création des champs d'informations
        self.label_titre = ttk.Label(
            self.zone_infos,
            text="Titre :"
        )
        self.label_titre.pack(anchor="w", padx=10, pady=3)

        self.label_artiste = ttk.Label(
            self.zone_infos,
            text="Artiste :"
        )
        self.label_artiste.pack(anchor="w", padx=10, pady=3)

        self.label_album = ttk.Label(
            self.zone_infos,
            text="Album :"
        )
        self.label_album.pack(anchor="w", padx=10, pady=3)

        self.label_duree = ttk.Label(
            self.zone_infos,
            text="Duree :"
        )
        self.label_duree.pack(anchor="w", padx=10, pady=3)

    def choisir_morceau(self):
        """
        Rôle :
            Permettre à l'utilisateur de choisir un fichier MP3 ou FLAC.

            Le fichier sélectionné est affiché dans le tableau
            avec ses métadonnées.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        fichier = filedialog.askopenfilename(
            title="Choisir un morceau",
            filetypes=[
                ("Fichiers musicaux", "*.mp3 *.flac"),
                ("Fichiers MP3", "*.mp3"),
                ("Fichiers FLAC", "*.flac")
            ]
        )

        if not fichier:
            return

        # Récupération des métadonnées du morceau
        try:
            morceau = extract_metadata(fichier)
            titre = morceau.title or ""
            artiste = morceau.artist or ""
            album = morceau.album or ""
            minutes = int(morceau.duration // 60)
            secondes = int(morceau.duration % 60)
            duree = f"{minutes}:{secondes:02d}"
        except (ValueError, OSError):
            titre = ""
            artiste = ""
            album = ""
            duree = ""

        # Remplacement du contenu du tableau par le morceau choisi
        for ligne in self.tableau.get_children():
            self.tableau.delete(ligne)

        self.effacer_metadonnees()
        self.tableau.insert(
            "",
            "end",
            iid=fichier,
            text=os.path.basename(fichier),
            values=(
                os.path.splitext(fichier)[1].lower(),
                titre,
                artiste,
                album,
                duree
            )
        )
        self.tableau.selection_set(fichier)
        self.afficher_metadonnees(None)

    def choisir_dossier(self):
        """
        Rôle :
            Permettre à l'utilisateur de sélectionner un dossier musical.

            Rechercher les fichiers MP3 et FLAC dans le dossier
            et ses sous-dossiers, puis afficher leur arborescence
            et leurs métadonnées dans le tableau.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        dossier = filedialog.askdirectory()

        if dossier:
            # Recherche des fichiers MP3 et FLAC
            fichiers = lister_fichiers_musicaux(dossier)

            # Suppression des anciennes lignes
            for ligne in self.tableau.get_children():
                self.tableau.delete(ligne)

            # Création du dossier principal
            racine = self.tableau.insert(
                "",
                "end",
                text=os.path.basename(os.path.normpath(dossier)),
                open=True
            )

            # Dictionnaire des dossiers déjà créés
            dossiers = {".": racine}

            # Ajout des fichiers dans l'arborescence
            for fichier in fichiers:
                chemin_relatif = os.path.relpath(fichier, dossier)
                parties = chemin_relatif.split(os.sep)

                parent = racine
                chemin_dossier = "."

                # Création des sous-dossiers
                for nom_dossier in parties[:-1]:
                    chemin_dossier = os.path.join(
                        chemin_dossier,
                        nom_dossier
                    )

                    if chemin_dossier not in dossiers:
                        dossiers[chemin_dossier] = self.tableau.insert(
                            parent,
                            "end",
                            text=nom_dossier,
                            open=True
                        )

                    parent = dossiers[chemin_dossier]

                # Récupération du nom et du format
                nom = os.path.basename(fichier)
                format_fichier = os.path.splitext(fichier)[1].lower()

                # Récupération des métadonnées du fichier
                try:
                    morceau = extract_metadata(fichier)

                    titre = morceau.title or ""
                    artiste = morceau.artist or ""
                    album = morceau.album or ""

                    minutes = int(morceau.duration // 60)
                    secondes = int(morceau.duration % 60)
                    duree = f"{minutes}:{secondes:02d}"

                except (ValueError, OSError):
                    # Si le fichier est illisible, les champs restent vides
                    titre = ""
                    artiste = ""
                    album = ""
                    duree = ""

                # Ajout du fichier musical avec ses métadonnées
                self.tableau.insert(
                    parent,
                    "end",
                    iid=fichier,
                    text=nom,
                    values=(
                        format_fichier,
                        titre,
                        artiste,
                        album,
                        duree
                    )
                )

            # Réinitialisation des informations
            self.effacer_metadonnees()

    def generer_playlist(self):
        """
        Rôle :
            Générer une playlist au format XSPF à partir d'un dossier.

            Permettre à l'utilisateur de choisir le dossier musical
            et l'emplacement d'enregistrement de la playlist.

            Afficher un message de confirmation ou d'erreur.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        dossier = filedialog.askdirectory(
            title="Choisir un dossier pour la playlist"
        )

        if not dossier:
            return

        try:
            # Choix du nom et de l'emplacement de la playlist
            chemin_sortie = filedialog.asksaveasfilename(
                title="Enregistrer la playlist XSPF",
                defaultextension=".xspf",
                filetypes=[("Playlists XSPF", "*.xspf")],
                initialfile="default_playlist.xspf"
            )

            if not chemin_sortie:
                return

            # Génération de la playlist à l'emplacement choisi
            chemin_playlist = generer_playlist_par_defaut(
                dossier,
                chemin_sortie
            )

            messagebox.showinfo(
                "Playlist generee",
                f"La playlist a ete creee :\n{os.path.abspath(chemin_playlist)}"
            )

        except Exception as erreur:
            messagebox.showerror(
                "Erreur",
                f"Impossible de generer la playlist :\n{erreur}"
            )

    def effacer_metadonnees(self):
        """
        Rôle :
            Réinitialiser les informations du morceau sélectionné.

            Remettre les champs titre, artiste, album et durée
            à leurs valeurs initiales.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        self.label_titre.config(text="Titre :")
        self.label_artiste.config(text="Artiste :")
        self.label_album.config(text="Album :")
        self.label_duree.config(text="Duree :")

    def afficher_metadonnees(self, event):
        """
        Rôle :
            Afficher les métadonnées du fichier musical sélectionné.

            Vérifier que l'élément sélectionné est un fichier,
            puis afficher son titre, son artiste, son album
            et sa durée dans la zone d'informations.

            Effacer les informations si un dossier est sélectionné.

        Arguments :
            event (tkinter.Event) :
                Événement déclenché lors de la sélection
                d'un élément du tableau.

        Valeur renvoyée :
            Aucune.
        """
        selection = self.tableau.selection()

        if selection:
            chemin = selection[0]

            # Vérification que la sélection est un fichier musical
            if not os.path.isfile(chemin):
                self.effacer_metadonnees()
                return

            try:
                morceau = extract_metadata(chemin)

                # Affichage des informations dans la fenêtre
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


# Lancement de l'application uniquement en exécution directe
if __name__ == "__main__":

    # Création de la fenêtre principale
    fenetre = tk.Tk()

    # Création de l'objet interface graphique
    application = MusicGUI(fenetre)

    # Affichage de la fenêtre
    fenetre.mainloop()