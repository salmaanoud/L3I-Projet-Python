"""
test_explorateur.py

Nom : test_explorateur.py
Role : tests automatiques de l'exploration de dossiers
       (src/library/explorateur.py) : lecture du type MIME dans le contenu
       des fichiers, filtre MP3/FLAC et parcours recursif
Auteur : LAIFAOUI Ines
Version : 1.0 - 11/11/2026
Licence : usage pedagogique (L3)
Compilation : aucune (Python interprete)
Execution : python3 -m unittest test_explorateur -v
            (depuis le dossier src/tests-auto)
"""

import os
import tempfile
import unittest

import outils_audio
from library.explorateur import (
    deviner_type_mime,
    est_fichier_musical,
    lister_fichiers_musicaux,
)


class TestExplorateur(unittest.TestCase):
    """
    Role : regroupe les tests de explorateur.py. Chaque test travaille
    dans un dossier temporaire, supprime a la fin du test.

    Attributs d'instance :
        _tmp (tempfile.TemporaryDirectory) : le dossier temporaire du test
        dossier (str) : chemin de ce dossier temporaire

    Prototypes des methodes :
        setUp(self)
        tearDown(self)
        chemin(self, *morceaux)
        ecrire(self, nom, contenu)
        test_*(self) : un test par comportement verifie
    """

    def setUp(self):
        """
        Role : cree le dossier temporaire utilise par le test.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = self._tmp.name

    def tearDown(self):
        """
        Role : supprime le dossier temporaire a la fin du test.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self._tmp.cleanup()

    def chemin(self, *morceaux):
        """
        Role : construit un chemin a l'interieur du dossier temporaire.

        Arguments :
            self (TestExplorateur) : instance de test
            *morceaux (str) : noms de dossiers / de fichier a joindre

        Valeur renvoyee :
            str : le chemin complet
        """
        return os.path.join(self.dossier, *morceaux)

    def ecrire(self, nom, contenu):
        """
        Role : cree un fichier quelconque (texte ou octets) dans le dossier
        temporaire.

        Arguments :
            self (TestExplorateur) : instance de test
            nom (str) : nom du fichier a creer
            contenu (str ou bytes) : contenu a ecrire dans le fichier

        Valeur renvoyee :
            str : le chemin complet du fichier cree
        """
        mode = "wb" if isinstance(contenu, bytes) else "w"
        with open(self.chemin(nom), mode) as fichier:
            fichier.write(contenu)
        return self.chemin(nom)

    # deviner_type_mime : le type est lu dans le contenu du fichier

    def test_type_mime_mp3_avec_tags_id3(self):
        """
        Role : un MP3 qui commence par un tag ID3 est reconnu "audio/mpeg".

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_mp3(self.chemin("a.mp3"), "Titre", "Artiste")
        self.assertEqual(deviner_type_mime(chemin), "audio/mpeg")

    def test_type_mime_mp3_sans_tag(self):
        """
        Role : un MP3 sans tag (qui commence directement par une trame
        MPEG) est reconnu "audio/mpeg".

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_mp3(self.chemin("a.mp3"))
        self.assertEqual(deviner_type_mime(chemin), "audio/mpeg")

    def test_type_mime_flac(self):
        """
        Role : un FLAC (signature "fLaC") est reconnu "audio/flac".

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_flac(self.chemin("a.flac"))
        self.assertEqual(deviner_type_mime(chemin), "audio/flac")

    def test_type_mime_ignore_l_extension(self):
        """
        Role : le type MIME vient du contenu : un vrai FLAC renomme en
        .txt reste un FLAC.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_flac(self.chemin("a.txt"))
        self.assertEqual(deviner_type_mime(chemin), "audio/flac")

    def test_type_mime_texte(self):
        """
        Role : un fichier texte n'a pas de type MIME audio (None).

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertIsNone(deviner_type_mime(self.ecrire("notes.txt", "bonjour")))

    def test_type_mime_fichier_vide(self):
        """
        Role : un fichier vide n'a pas de type MIME audio (None).

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertIsNone(deviner_type_mime(self.ecrire("vide.mp3", b"")))

    def test_type_mime_fichier_inexistant(self):
        """
        Role : un fichier qui n'existe pas donne None, sans erreur.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertIsNone(deviner_type_mime(self.chemin("absent.mp3")))

    # est_fichier_musical : extension ET type MIME doivent etre coherents

    def test_vrais_fichiers_acceptes(self):
        """
        Role : un vrai MP3 et un vrai FLAC sont acceptes.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertTrue(est_fichier_musical(outils_audio.creer_mp3(self.chemin("a.mp3"))))
        self.assertTrue(est_fichier_musical(outils_audio.creer_flac(self.chemin("a.flac"))))

    def test_extension_en_majuscules(self):
        """
        Role : l'extension est comparee sans tenir compte des majuscules
        (A.MP3 est accepte).

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertTrue(est_fichier_musical(outils_audio.creer_mp3(self.chemin("A.MP3"))))

    def test_faux_mp3_refuse(self):
        """
        Role : un fichier .mp3 qui contient du texte est refuse.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertFalse(est_fichier_musical(self.ecrire("faux.mp3", "pas de la musique")))

    def test_flac_renomme_en_mp3_refuse(self):
        """
        Role : un FLAC renomme en .mp3 est refuse (le contenu ne correspond
        pas a l'extension).

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_flac(self.chemin("a.mp3"))
        self.assertFalse(est_fichier_musical(chemin))

    def test_mp3_renomme_en_flac_refuse(self):
        """
        Role : un MP3 renomme en .flac est refuse (le contenu ne correspond
        pas a l'extension).

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_mp3(self.chemin("a.flac"))
        self.assertFalse(est_fichier_musical(chemin))

    def test_bonne_signature_mais_mauvaise_extension_refuse(self):
        """
        Role : un vrai MP3 renomme en .txt est refuse (l'extension n'est
        pas musicale).

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_mp3(self.chemin("a.txt"))
        self.assertFalse(est_fichier_musical(chemin))

    # lister_fichiers_musicaux : parcours recursif

    def test_parcours_recursif(self):
        """
        Role : les fichiers des sous-dossiers sont trouves, a tous les
        niveaux.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        os.makedirs(self.chemin("album", "cd1"))
        outils_audio.creer_mp3(self.chemin("a.mp3"))
        outils_audio.creer_flac(self.chemin("album", "b.flac"))
        outils_audio.creer_mp3(self.chemin("album", "cd1", "c.mp3"))
        trouves = lister_fichiers_musicaux(self.dossier)
        self.assertEqual(
            sorted(trouves),
            sorted([
                self.chemin("a.mp3"),
                self.chemin("album", "b.flac"),
                self.chemin("album", "cd1", "c.mp3"),
            ]),
        )

    def test_fichiers_non_musicaux_ignores(self):
        """
        Role : les fichiers texte et les faux MP3 ne sont pas retenus.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        outils_audio.creer_mp3(self.chemin("a.mp3"))
        self.ecrire("notes.txt", "bonjour")
        self.ecrire("faux.mp3", "pas de la musique")
        self.assertEqual(lister_fichiers_musicaux(self.dossier), [self.chemin("a.mp3")])

    def test_dossier_vide(self):
        """
        Role : un dossier vide donne une liste vide.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertEqual(lister_fichiers_musicaux(self.dossier), [])

    def test_dossier_inexistant(self):
        """
        Role : un dossier qui n'existe pas donne une liste vide, sans
        erreur.

        Arguments :
            self (TestExplorateur) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertEqual(lister_fichiers_musicaux(self.chemin("absent")), [])


if __name__ == "__main__":
    unittest.main()
