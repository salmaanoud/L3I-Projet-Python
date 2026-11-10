"""Tests de la classe Track (src/library/track.py)."""

import unittest

import outils_audio  # noqa: F401  (prépare le chemin de recherche)
from library.track import Track


class TestTrack(unittest.TestCase):

    def test_valeurs_par_defaut(self):
        track = Track(path="a.mp3", format="mp3")
        self.assertEqual(track.title, "")
        self.assertEqual(track.artist, "")
        self.assertEqual(track.album, "")
        self.assertEqual(track.duration, 0.0)

    def test_champs_renseignes(self):
        track = Track("a.flac", "flac", "Titre", "Artiste", "Album", 12.5)
        self.assertEqual(track.path, "a.flac")
        self.assertEqual(track.format, "flac")
        self.assertEqual(track.title, "Titre")
        self.assertEqual(track.artist, "Artiste")
        self.assertEqual(track.album, "Album")
        self.assertEqual(track.duration, 12.5)

    def test_egalite(self):
        self.assertEqual(Track("a.mp3", "mp3", "T"), Track("a.mp3", "mp3", "T"))
        self.assertNotEqual(Track("a.mp3", "mp3", "T"), Track("a.mp3", "mp3", "U"))


if __name__ == "__main__":
    unittest.main()
