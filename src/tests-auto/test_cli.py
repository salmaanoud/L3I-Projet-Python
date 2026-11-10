"""Tests du mode console (src/cli/cli.py)."""

import contextlib
import io
import os
import tempfile
import unittest

import outils_audio
import cli


def lancer(*arguments):
    """Exécute cli.main avec ces arguments.

    Renvoie (code de sortie, texte de stdout, texte de stderr). Quand argparse
    quitte le programme (SystemExit), on récupère son code de sortie.
    """
    sortie, erreur = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
        try:
            code = cli.main(list(arguments))
        except SystemExit as quitter:
            code = quitter.code
    return code, sortie.getvalue(), erreur.getvalue()


class TestFormatDuree(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(cli.format_duree(0), "00:00")

    def test_moins_d_une_minute(self):
        self.assertEqual(cli.format_duree(5), "00:05")

    def test_minutes_et_secondes(self):
        self.assertEqual(cli.format_duree(125), "02:05")

    def test_arrondi_a_la_seconde(self):
        self.assertEqual(cli.format_duree(59.6), "01:00")
        self.assertEqual(cli.format_duree(61.2), "01:01")

    def test_plus_d_une_heure(self):
        self.assertEqual(cli.format_duree(3725), "62:05")


class TestCliOptions(unittest.TestCase):
    """Erreurs d'utilisation : argparse quitte avec le code 2."""

    def test_aucun_parametre(self):
        code, _, erreur = lancer()
        self.assertEqual(code, 2)
        self.assertIn("-h", erreur)

    def test_aide(self):
        code, sortie, _ = lancer("-h")
        self.assertEqual(code, 0)
        for option in ("-f", "-d", "-o", "-h"):
            self.assertIn(option, sortie)

    def test_f_et_d_sont_exclusifs(self):
        code, _, _ = lancer("-f", "a.mp3", "-d", ".")
        self.assertEqual(code, 2)

    def test_o_sans_d(self):
        code, _, erreur = lancer("-f", "a.mp3", "-o", "p.xspf")
        self.assertEqual(code, 2)
        self.assertIn("-o", erreur)

    def test_option_inconnue(self):
        code, _, _ = lancer("-z")
        self.assertEqual(code, 2)


class TestCliFichier(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_mp3_valide(self):
        chemin = outils_audio.creer_mp3(
            os.path.join(self.dossier, "a.mp3"), "Mon titre", "Mon artiste", "Mon album")
        code, sortie, erreur = lancer("-f", chemin)
        self.assertEqual(code, 0)
        self.assertEqual(erreur, "")
        self.assertIn("MP3", sortie)
        self.assertIn("Mon titre", sortie)
        self.assertIn("Mon artiste", sortie)
        self.assertIn("Mon album", sortie)
        self.assertIn("00:01", sortie)

    def test_flac_valide(self):
        chemin = outils_audio.creer_flac(
            os.path.join(self.dossier, "a.flac"), "Titre FLAC", "Artiste FLAC", "Album FLAC")
        code, sortie, _ = lancer("-f", chemin)
        self.assertEqual(code, 0)
        self.assertIn("FLAC", sortie)
        self.assertIn("Titre FLAC", sortie)

    def test_tags_absents_affiche_inconnu(self):
        chemin = outils_audio.creer_mp3(os.path.join(self.dossier, "nu.mp3"))
        code, sortie, _ = lancer("-f", chemin)
        self.assertEqual(code, 0)
        self.assertEqual(sortie.count("(inconnu)"), 3)

    def test_fichier_inexistant(self):
        code, sortie, erreur = lancer("-f", os.path.join(self.dossier, "absent.mp3"))
        self.assertEqual(code, 1)
        self.assertEqual(sortie, "")
        self.assertIn("n'existe pas", erreur)

    def test_format_non_supporte(self):
        chemin = os.path.join(self.dossier, "notes.txt")
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write("texte")
        code, _, erreur = lancer("-f", chemin)
        self.assertEqual(code, 1)
        self.assertIn("Erreur", erreur)

    def test_fichier_corrompu(self):
        chemin = os.path.join(self.dossier, "faux.mp3")
        with open(chemin, "wb") as fichier:
            fichier.write(b"pas un vrai mp3")
        code, _, erreur = lancer("-f", chemin)
        self.assertEqual(code, 1)
        self.assertIn("Erreur", erreur)


class TestCliDossier(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = self._tmp.name
        sous_dossier = os.path.join(self.dossier, "album")
        os.mkdir(sous_dossier)
        outils_audio.creer_mp3(
            os.path.join(self.dossier, "a.mp3"), "Titre A", "Artiste A", "Album A")
        outils_audio.creer_flac(
            os.path.join(sous_dossier, "b.flac"), "Titre B", "Artiste B", "Album B")
        # Un fichier qui n'est pas de la musique doit être ignoré.
        with open(os.path.join(self.dossier, "notes.txt"), "w", encoding="utf-8") as f:
            f.write("texte")

    def tearDown(self):
        self._tmp.cleanup()

    def test_explore_recursivement(self):
        code, sortie, erreur = lancer("-d", self.dossier)
        self.assertEqual(code, 0)
        self.assertEqual(erreur, "")
        self.assertIn("Titre A", sortie)
        self.assertIn("Titre B", sortie)
        self.assertEqual(sortie.count("--- Morceau"), 2)

    def test_dossier_inexistant(self):
        code, _, erreur = lancer("-d", os.path.join(self.dossier, "absent"))
        self.assertEqual(code, 1)
        self.assertIn("n'existe pas", erreur)

    def test_dossier_vide(self):
        with tempfile.TemporaryDirectory() as vide:
            code, sortie, _ = lancer("-d", vide)
        self.assertEqual(code, 0)
        self.assertEqual(sortie.count("--- Morceau"), 0)

    def test_sans_o_ne_cree_pas_de_playlist(self):
        lancer("-d", self.dossier)
        self.assertFalse(
            [n for n in os.listdir(self.dossier) if n.endswith(".xspf")])

    def test_o_genere_une_playlist_xspf(self):
        sortie_xspf = os.path.join(self.dossier, "playlist.xspf")
        code, sortie, _ = lancer("-d", self.dossier, "-o", sortie_xspf)
        self.assertEqual(code, 0)
        self.assertIn("playlist.xspf", sortie)
        self.assertTrue(os.path.isfile(sortie_xspf))
        with open(sortie_xspf, encoding="utf-8") as fichier:
            contenu = fichier.read()
        self.assertIn("Titre A", contenu)
        self.assertIn("Titre B", contenu)

    def test_fichier_corrompu_est_ignore_sans_planter(self):
        # Signature MP3 valide (« ID3 ») mais contenu inutilisable : il passe
        # l'exploration mais l'extraction échoue, le dossier doit quand même
        # être traité.
        faux = os.path.join(self.dossier, "casse.mp3")
        with open(faux, "wb") as fichier:
            fichier.write(b"ID3" + b"\xff" * 50)
        code, sortie, erreur = lancer("-d", self.dossier)
        self.assertEqual(code, 0)
        self.assertIn("Ignoré", erreur)
        self.assertIn("casse.mp3", erreur)
        self.assertIn("Titre A", sortie)
        self.assertIn("Titre B", sortie)


if __name__ == "__main__":
    unittest.main()
