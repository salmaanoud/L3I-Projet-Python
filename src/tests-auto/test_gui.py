"""
Module : Tests automatiques de l'interface graphique

Rôle :
    Vérifier le bon fonctionnement de l'interface graphique
    du gestionnaire de fichiers musicaux MP3 et FLAC.

    Les tests permettent de contrôler la sélection des fichiers
    et des dossiers, l'affichage des métadonnées, leur
    réinitialisation et la génération des playlists XSPF.

    Les interactions avec les fichiers et les fenêtres de dialogue
    sont simulées à l'aide de unittest.mock.
"""

import unittest
import os
import sys
import tkinter as tk

# Ajout du dossier src au chemin de recherche
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from gui.gui import MusicGUI


class TestMusicGUI(unittest.TestCase):
    """
    Rôle :
        Regrouper les tests automatiques de l'interface MusicGUI.

        Vérifier le comportement des principales fonctionnalités
        de l'interface graphique à l'aide de la bibliothèque unittest.
    """

    def setUp(self):
        """
        Rôle :
            Préparer l'environnement nécessaire à chaque test.

            Créer une fenêtre Tkinter masquée et initialiser
            une instance de l'interface graphique MusicGUI.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Création d'une fenêtre pour chaque test
        self.fenetre = tk.Tk()
        self.fenetre.withdraw()
        self.application = MusicGUI(self.fenetre)

    def tearDown(self):
        """
        Rôle :
            Nettoyer l'environnement après chaque test.

            Détruire la fenêtre Tkinter afin de libérer
            les ressources utilisées pendant le test.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Fermeture de la fenêtre après chaque test
        self.fenetre.destroy()

    def test_effacer_metadonnees(self):
        """
        Rôle :
            Vérifier la réinitialisation des métadonnées affichées.

            Contrôler que les champs titre, artiste, album et durée
            retrouvent leurs valeurs initiales après l'appel
            de la méthode effacer_metadonnees.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Simulation de métadonnées affichées
        self.application.label_titre.config(text="Titre : Test")
        self.application.label_artiste.config(text="Artiste : Test")
        self.application.label_album.config(text="Album : Test")
        self.application.label_duree.config(text="Duree : 3:00")

        # Appel de la méthode à tester
        self.application.effacer_metadonnees()

        # Vérification des résultats
        self.assertEqual(
            self.application.label_titre.cget("text"),
            "Titre :"
        )
        self.assertEqual(
            self.application.label_artiste.cget("text"),
            "Artiste :"
        )
        self.assertEqual(
            self.application.label_album.cget("text"),
            "Album :"
        )
        self.assertEqual(
            self.application.label_duree.cget("text"),
            "Duree :"
        )

    def test_choisir_dossier_annule(self):
        """
        Rôle :
            Vérifier le comportement lors de l'annulation
            de la sélection d'un dossier.

            Simuler une annulation de la fenêtre de dialogue
            et vérifier que le tableau reste vide.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Simulation de l'annulation de la sélection du dossier
        from unittest.mock import patch

        with patch("gui.gui.filedialog.askdirectory", return_value=""):
            self.application.choisir_dossier()

        # Vérification que le tableau reste vide
        self.assertEqual(
            len(self.application.tableau.get_children()),
            0
        )

    def test_afficher_metadonnees(self):
        """
        Rôle :
            Vérifier l'affichage des métadonnées d'un morceau.

            Simuler la sélection d'un fichier musical et
            l'extraction de ses informations.

            Contrôler que le titre, l'artiste, l'album et la durée
            sont correctement affichés dans l'interface.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Simulation de la sélection d'un fichier musical
        from unittest.mock import patch, Mock

        morceau = Mock()
        morceau.title = "Musique test"
        morceau.artist = "Artiste test"
        morceau.album = "Album test"
        morceau.duration = 125

        chemin = os.path.abspath("musique_test.mp3")

        with patch("gui.gui.os.path.isfile", return_value=True), \
             patch("gui.gui.extract_metadata", return_value=morceau):

            self.application.tableau.insert(
                "",
                "end",
                iid=chemin,
                text="musique_test.mp3"
            )

            self.application.tableau.selection_set(chemin)
            self.application.afficher_metadonnees(None)

        # Vérification des métadonnées affichées
        self.assertEqual(
            self.application.label_titre.cget("text"),
            "Titre : Musique test"
        )
        self.assertEqual(
            self.application.label_artiste.cget("text"),
            "Artiste : Artiste test"
        )
        self.assertEqual(
            self.application.label_album.cget("text"),
            "Album : Album test"
        )
        self.assertEqual(
            self.application.label_duree.cget("text"),
            "Duree : 2:05"
        )

    def test_generer_playlist(self):
        """
        Rôle :
            Vérifier la génération d'une playlist XSPF.

            Simuler la sélection d'un dossier musical et
            le choix du fichier de sortie.

            Contrôler que la fonction de génération reçoit
            les bons chemins et qu'un message de confirmation
            est affiché.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Simulation du choix du dossier et du fichier de sortie
        from unittest.mock import patch

        dossier = os.path.abspath("test_music")
        sortie = os.path.abspath("playlist_test.xspf")

        with patch(
            "gui.gui.filedialog.askdirectory",
            return_value=dossier
        ), patch(
            "gui.gui.filedialog.asksaveasfilename",
            return_value=sortie
        ), patch(
            "gui.gui.generer_playlist_par_defaut",
            return_value=sortie
        ) as mock_generation, patch(
            "gui.gui.messagebox.showinfo"
        ) as mock_message:

            # Appel de la méthode à tester
            self.application.generer_playlist()

            # Vérification des chemins transmis
            mock_generation.assert_called_once_with(
                dossier,
                sortie
            )

            # Vérification du message de confirmation
            mock_message.assert_called_once()

    def test_choisir_morceau_annule(self):
        """
        Rôle :
            Vérifier le comportement lors de l'annulation
            de la sélection d'un morceau.

            Simuler une annulation de la fenêtre de dialogue
            et contrôler que le tableau reste vide.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Simulation de l'annulation du choix d'un morceau
        from unittest.mock import patch

        with patch("gui.gui.filedialog.askopenfilename", return_value=""):
            self.application.choisir_morceau()

        # Vérification que le tableau reste vide
        self.assertEqual(
            len(self.application.tableau.get_children()),
            0
        )

    def test_choisir_morceau_valide(self):
        """
        Rôle :
            Vérifier la sélection d'un fichier musical valide.

            Simuler le choix d'un fichier MP3 et l'extraction
            de ses métadonnées.

            Contrôler que le morceau est correctement ajouté
            au tableau avec son nom de fichier.

        Arguments :
            Aucun.

        Valeur renvoyée :
            Aucune.
        """
        # Simulation de la sélection d'un fichier MP3
        from unittest.mock import patch, Mock

        chemin = os.path.abspath("musique_test.mp3")

        morceau = Mock()
        morceau.title = "Musique test"
        morceau.artist = "Artiste test"
        morceau.album = "Album test"
        morceau.duration = 125

        with patch(
            "gui.gui.filedialog.askopenfilename",
            return_value=chemin
        ), patch(
            "gui.gui.extract_metadata",
            return_value=morceau
        ):
            self.application.choisir_morceau()

        # Vérification de la présence du morceau
        lignes = self.application.tableau.get_children()

        self.assertEqual(len(lignes), 1)

        self.assertEqual(
            self.application.tableau.item(lignes[0], "text"),
            "musique_test.mp3"
        )


if __name__ == "__main__":
    unittest.main()