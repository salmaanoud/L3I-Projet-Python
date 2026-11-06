import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys

# Ajout du dossier src au chemin de recherche
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des fonctions du projet
from explorateur import lister_fichiers_musicaux
from library.metadata import extract_metadata


# Creation de la fenetre principale
fenetre = tk.Tk()

# Titre de la fenetre
fenetre.title("Gestionnaire de musique MP3/FLAC")

# Dimensions de la fenetre
fenetre.geometry("900x600")


# Fonction pour choisir un dossier
def choisir_dossier():
    dossier = filedialog.askdirectory()

    if dossier:
        # Recherche des fichiers MP3 et FLAC
        fichiers = lister_fichiers_musicaux(dossier)

        # Suppression des anciennes lignes
        for ligne in tableau.get_children():
            tableau.delete(ligne)

        # Creation du dossier principal
        racine = tableau.insert(
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
                    dossiers[chemin_dossier] = tableau.insert(
                        parent,
                        "end",
                        text=nom_dossier,
                        open=True
                    )

                parent = dossiers[chemin_dossier]

            # Ajout du fichier musical
            nom = os.path.basename(fichier)
            format_fichier = os.path.splitext(fichier)[1].lower()

            tableau.insert(
                parent,
                "end",
                iid=fichier,
                text=nom,
                values=(format_fichier,)
            )


# Fonction pour afficher les metadonnees
def afficher_metadonnees(event):
    selection = tableau.selection()

    if selection:
        chemin = selection[0]

        
        # Verification que la selection est un fichier musical
        if not os.path.isfile(chemin):
            label_titre.config(text="Titre :")
            label_artiste.config(text="Artiste :")
            label_album.config(text="Album :")
            label_duree.config(text="Duree :")
            return


        try:
            morceau = extract_metadata(chemin)

            # Affichage des informations dans la fenetre
            label_titre.config(text="Titre : " + str(morceau.title))
            label_artiste.config(text="Artiste : " + str(morceau.artist))
            label_album.config(text="Album : " + str(morceau.album))

            minutes = int(morceau.duration // 60)
            secondes = int(morceau.duration % 60)

            label_duree.config(
                text=f"Duree : {minutes}:{secondes:02d}"
            )

        # Affichage d'un message en cas d'erreur
        except (ValueError, OSError) as erreur:
            messagebox.showerror("Erreur", str(erreur))


# Creation du bouton
bouton_dossier = tk.Button(
    fenetre,
    text="Choisir un dossier",
    command=choisir_dossier
)

# Affichage du bouton
bouton_dossier.pack(pady=20)


# Creation de l'arborescence des fichiers musicaux
tableau = ttk.Treeview(
    fenetre,
    columns=("format",),
    show="tree headings"
)

# Definition des colonnes
tableau.heading("#0", text="Nom du fichier / Dossier")
tableau.heading("format", text="Format")

# Dimensions des colonnes
tableau.column("#0", width=500)
tableau.column("format", width=100)

# Affichage du tableau
tableau.pack(fill="both", expand=True, padx=20, pady=10)

# Detection de la selection d'un morceau
tableau.bind("<<TreeviewSelect>>", afficher_metadonnees)


# Creation de la zone des metadonnees
zone_infos = ttk.LabelFrame(fenetre, text="Informations du morceau")

zone_infos.pack(fill="x", padx=20, pady=10)

# Creation des champs d'informations
label_titre = ttk.Label(zone_infos, text="Titre :")
label_titre.pack(anchor="w", padx=10, pady=3)

label_artiste = ttk.Label(zone_infos, text="Artiste :")
label_artiste.pack(anchor="w", padx=10, pady=3)

label_album = ttk.Label(zone_infos, text="Album :")
label_album.pack(anchor="w", padx=10, pady=3)

label_duree = ttk.Label(zone_infos, text="Duree :")
label_duree.pack(anchor="w", padx=10, pady=3)


# Affichage de la fenetre
fenetre.mainloop()
