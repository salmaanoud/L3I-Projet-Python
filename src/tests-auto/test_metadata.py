"""Tests de l'extraction des métadonnées (src/library/metadata.py)."""

import os
import tempfile
import unittest

import outils_audio
from library.metadata import extract_metadata
from library.track import Track


class TestExtractMetadata(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def chemin(self, nom):
        return os.path.join(self.dossier, nom)

    def test_mp3_avec_tags_id3(self):
        chemin = outils_audio.creer_mp3(
            self.chemin("a.mp3"), "Mon titre", "Mon artiste", "Mon album")
        track = extract_metadata(chemin)
        self.assertIsInstance(track, Track)
        self.assertEqual(track.path, chemin)
        self.assertEqual(track.format, "mp3")
        self.assertEqual(track.title, "Mon titre")
        self.assertEqual(track.artist, "Mon artiste")
        self.assertEqual(track.album, "Mon album")
        self.assertAlmostEqual(track.duration, outils_audio.DUREE_MP3, delta=0.1)

    def test_flac_avec_tags_vorbis(self):
        chemin = outils_audio.creer_flac(
            self.chemin("a.flac"), "Titre FLAC", "Artiste FLAC", "Album FLAC")
        track = extract_metadata(chemin)
        self.assertEqual(track.format, "flac")
        self.assertEqual(track.title, "Titre FLAC")
        self.assertEqual(track.artist, "Artiste FLAC")
        self.assertEqual(track.album, "Album FLAC")
        self.assertAlmostEqual(track.duration, outils_audio.DUREE_FLAC, places=2)

    def test_accents_conserves(self):
        chemin = outils_audio.creer_mp3(
            self.chemin("a.mp3"), "Élégie", "Zaïd", "Été 2026")
        track = extract_metadata(chemin)
        self.assertEqual(track.title, "Élégie")
        self.assertEqual(track.artist, "Zaïd")
        self.assertEqual(track.album, "Été 2026")

    def test_mp3_sans_tags_donne_chaines_vides(self):
        chemin = outils_audio.creer_mp3(self.chemin("nu.mp3"))
        track = extract_metadata(chemin)
        self.assertEqual((track.title, track.artist, track.album), ("", "", ""))
        self.assertGreater(track.duration, 0)

    def test_flac_sans_tags_donne_chaines_vides(self):
        chemin = outils_audio.creer_flac(self.chemin("nu.flac"))
        track = extract_metadata(chemin)
        self.assertEqual((track.title, track.artist, track.album), ("", "", ""))

    def test_tags_partiels(self):
        chemin = outils_audio.creer_mp3(self.chemin("p.mp3"), titre="Seulement")
        track = extract_metadata(chemin)
        self.assertEqual(track.title, "Seulement")
        self.assertEqual(track.artist, "")
        self.assertEqual(track.album, "")

    def test_extension_en_majuscules(self):
        chemin = outils_audio.creer_mp3(self.chemin("A.MP3"), "Titre")
        track = extract_metadata(chemin)
        self.assertEqual(track.format, "mp3")
        self.assertEqual(track.title, "Titre")

    def test_extension_non_supportee(self):
        chemin = self.chemin("notes.txt")
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write("pas de la musique")
        with self.assertRaises(ValueError) as contexte:
            extract_metadata(chemin)
        self.assertIn(".txt", str(contexte.exception))

    def test_fichier_corrompu_leve_valueerror(self):
        chemin = self.chemin("faux.mp3")
        with open(chemin, "wb") as fichier:
            fichier.write(b"ceci n'est pas un vrai mp3")
        with self.assertRaises(ValueError):
            extract_metadata(chemin)

    def test_fichier_vide_leve_valueerror(self):
        chemin = self.chemin("vide.flac")
        open(chemin, "wb").close()
        with self.assertRaises(ValueError):
            extract_metadata(chemin)

    def test_fichier_inexistant_leve_valueerror(self):
        # mutagen convertit l'erreur « fichier introuvable » en MutagenError,
        # que extract_metadata transforme à son tour en ValueError.
        with self.assertRaises(ValueError):
            extract_metadata(self.chemin("absent.mp3"))


if __name__ == "__main__":
    unittest.main()
