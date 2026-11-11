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

    def setUp(self):
        # Creation d'une fenetre pour chaque test
        self.fenetre = tk.Tk()
        self.fenetre.withdraw()
        self.application = MusicGUI(self.fenetre)

    def tearDown(self):
        # Fermeture de la fenetre apres chaque test
        self.fenetre.destroy()

    def test_effacer_metadonnees(self):
        # Simulation de metadonnees affichees
        self.application.label_titre.config(text="Titre : Test")
        self.application.label_artiste.config(text="Artiste : Test")
        self.application.label_album.config(text="Album : Test")
        self.application.label_duree.config(text="Duree : 3:00")

        # Appel de la methode a tester
        self.application.effacer_metadonnees()

        # Verification des resultats
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
        # Simulation de l'annulation de la selection du dossier
        from unittest.mock import patch

        with patch("gui.gui.filedialog.askdirectory", return_value=""):
            self.application.choisir_dossier()

        # Verification que le tableau reste vide
        self.assertEqual(
            len(self.application.tableau.get_children()),
            0
        )

    def test_afficher_metadonnees(self):
        # Simulation de la selection d'un fichier musical
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

        # Verification des metadonnees affichees
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

            # Appel de la methode a tester
            self.application.generer_playlist()

            # Verification des chemins transmis
            mock_generation.assert_called_once_with(
                dossier,
                sortie
            )

            # Verification du message de confirmation
            mock_message.assert_called_once()


if __name__ == "__main__":
    unittest.main()