"""
test_playlist_xspf.py

Nom : test_playlist_xspf.py
Role : tests automatiques des playlists XSPF (src/library/playlist_xspf.py) :
       echappement XML, construction des URI, creation / lecture /
       validation d'une playlist et generation de la playlist par defaut
Auteur : LAIFAOUI Ines
Version : 1.0 - 11/11/2026
Licence : usage pedagogique (L3)
Compilation : aucune (Python interprete)
Execution : python3 -m unittest test_playlist_xspf -v
            (depuis le dossier src/tests-auto)
"""

import os
import tempfile
import unittest

import outils_audio
from library.playlist_xspf import (
    chemin_vers_uri,
    creer_playlist,
    deechapper_xml,
    echapper_xml,
    generer_playlist_par_defaut,
    lire_playlist,
    piste_depuis_fichier,
    valider_playlist,
)


class TestEchappementXml(unittest.TestCase):
    """
    Role : regroupe les tests de echapper_xml et deechapper_xml.

    Attributs d'instance :
        aucun

    Prototypes des methodes :
        test_*(self) : un test par comportement verifie
    """

    def test_caracteres_speciaux_echappes(self):
        """
        Role : &, <, > et " sont remplaces par leur forme echappee.

        Arguments :
            self (TestEchappementXml) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertEqual(echapper_xml('a & b < c > d "e"'),
                         "a &amp; b &lt; c &gt; d &quot;e&quot;")

    def test_texte_normal_inchange(self):
        """
        Role : un texte sans caractere special n'est pas modifie.

        Arguments :
            self (TestEchappementXml) : instance de test

        Valeur renvoyee :
            None
        """
        self.assertEqual(echapper_xml("Bonjour"), "Bonjour")

    def test_aller_retour(self):
        """
        Role : echapper puis deechapper redonne le texte de depart, meme
        s'il contient deja "&amp;".

        Arguments :
            self (TestEchappementXml) : instance de test

        Valeur renvoyee :
            None
        """
        texte = 'Rock & Roll <live> "1999" &amp; co'
        self.assertEqual(deechapper_xml(echapper_xml(texte)), texte)


class TestCheminVersUri(unittest.TestCase):
    """
    Role : regroupe les tests de chemin_vers_uri.

    Attributs d'instance :
        aucun

    Prototypes des methodes :
        test_*(self) : un test par comportement verifie
    """

    def test_forme_de_l_uri(self):
        """
        Role : l'URI commence par "file:///" (et pas par quatre slashs),
        ne contient aucun antislash et garde le nom du fichier.

        Arguments :
            self (TestCheminVersUri) : instance de test

        Valeur renvoyee :
            None
        """
        uri = chemin_vers_uri(os.path.join(tempfile.gettempdir(), "a.mp3"))
        self.assertTrue(uri.startswith("file:///"))
        # ancien bug : quatre slashs au lieu de trois
        self.assertFalse(uri.startswith("file:////"))
        self.assertNotIn("\\", uri)
        self.assertTrue(uri.endswith("/a.mp3"))

    def test_chemin_relatif_devient_absolu(self):
        """
        Role : un chemin relatif est transforme en URI absolue.

        Arguments :
            self (TestCheminVersUri) : instance de test

        Valeur renvoyee :
            None
        """
        uri = chemin_vers_uri("dossier_relatif/a.mp3")
        self.assertTrue(uri.startswith("file:///"))
        self.assertTrue(uri.endswith("/dossier_relatif/a.mp3"))


class TestPlaylist(unittest.TestCase):
    """
    Role : regroupe les tests de creer_playlist, lire_playlist,
    valider_playlist, piste_depuis_fichier et generer_playlist_par_defaut.
    Chaque test travaille dans un dossier temporaire, supprime a la fin.

    Attributs d'instance :
        _tmp (tempfile.TemporaryDirectory) : le dossier temporaire du test
        dossier (str) : chemin de ce dossier temporaire
        sortie (str) : chemin du fichier playlist.xspf utilise par les tests

    Prototypes des methodes :
        setUp(self)
        tearDown(self)
        chemin(self, *morceaux)
        lire_texte(self, chemin)
        test_*(self) : un test par comportement verifie
    """

    def setUp(self):
        """
        Role : cree le dossier temporaire et le chemin du fichier .xspf.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = self._tmp.name
        self.sortie = os.path.join(self.dossier, "playlist.xspf")

    def tearDown(self):
        """
        Role : supprime le dossier temporaire a la fin du test.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        self._tmp.cleanup()

    def chemin(self, *morceaux):
        """
        Role : construit un chemin a l'interieur du dossier temporaire.

        Arguments :
            self (TestPlaylist) : instance de test
            *morceaux (str) : noms de dossiers / de fichier a joindre

        Valeur renvoyee :
            str : le chemin complet
        """
        return os.path.join(self.dossier, *morceaux)

    def lire_texte(self, chemin):
        """
        Role : lit un fichier texte en UTF-8.

        Arguments :
            self (TestPlaylist) : instance de test
            chemin (str) : chemin du fichier a lire

        Valeur renvoyee :
            str : le contenu du fichier
        """
        with open(chemin, encoding="UTF-8") as fichier:
            return fichier.read()

    # creer_playlist et lire_playlist

    def test_creation_puis_relecture(self):
        """
        Role : une playlist ecrite puis relue redonne les memes pistes
        (la location est relue sous forme d'URI).

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        pistes = [
            {"location": self.chemin("a.mp3"), "title": "Titre A",
             "creator": "Artiste A", "album": "Album A"},
            {"location": self.chemin("b.flac"), "title": "Titre B"},
        ]
        creer_playlist(pistes, self.sortie)
        relues = lire_playlist(self.sortie)
        self.assertEqual(len(relues), 2)
        self.assertEqual(relues[0], {
            "location": chemin_vers_uri(self.chemin("a.mp3")),
            "title": "Titre A", "creator": "Artiste A", "album": "Album A"})
        self.assertEqual(relues[1], {
            "location": chemin_vers_uri(self.chemin("b.flac")),
            "title": "Titre B"})

    def test_piste_avec_seulement_une_location(self):
        """
        Role : une piste qui n'a que sa location (seul champ obligatoire)
        est bien ecrite et relue.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        creer_playlist([{"location": self.chemin("a.mp3")}], self.sortie)
        self.assertEqual(lire_playlist(self.sortie),
                         [{"location": chemin_vers_uri(self.chemin("a.mp3"))}])

    def test_caracteres_speciaux_conserves(self):
        """
        Role : les caracteres speciaux d'un titre ou d'un artiste sont
        echappes dans le fichier, puis retrouves intacts a la relecture.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        pistes = [{"location": self.chemin("a.mp3"),
                   "title": 'Rock & Roll <live>', "creator": 'Les "Gars"'}]
        creer_playlist(pistes, self.sortie)
        relue = lire_playlist(self.sortie)[0]
        self.assertEqual(relue["title"], "Rock & Roll <live>")
        self.assertEqual(relue["creator"], 'Les "Gars"')
        # dans le fichier lui-meme, les caracteres sont bien echappes
        self.assertIn("Rock &amp; Roll &lt;live&gt;", self.lire_texte(self.sortie))

    def test_playlist_vide(self):
        """
        Role : une playlist sans piste est ecrite et relue comme une liste
        vide.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        creer_playlist([], self.sortie)
        self.assertEqual(lire_playlist(self.sortie), [])

    def test_fichier_en_xml_avec_espace_de_noms(self):
        """
        Role : le fichier genere commence par l'en-tete XML et declare
        l'espace de noms XSPF et la balise trackList.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        creer_playlist([{"location": self.chemin("a.mp3")}], self.sortie)
        texte = self.lire_texte(self.sortie)
        self.assertTrue(texte.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertIn('xmlns="http://xspf.org/ns/0/"', texte)
        self.assertIn("<trackList>", texte)

    # valider_playlist

    def test_playlist_generee_valide(self):
        """
        Role : une playlist produite par creer_playlist est valide.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        creer_playlist([{"location": self.chemin("a.mp3")}], self.sortie)
        self.assertEqual(valider_playlist(self.sortie), (True, []))

    def test_validation_sans_espace_de_noms(self):
        """
        Role : une playlist sans xmlns est declaree invalide, avec une
        seule erreur qui le mentionne.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        creer_playlist([{"location": self.chemin("a.mp3")}], self.sortie)
        texte = self.lire_texte(self.sortie).replace(' xmlns="http://xspf.org/ns/0/"', "")
        with open(self.sortie, "w", encoding="UTF-8") as fichier:
            fichier.write(texte)
        valide, erreurs = valider_playlist(self.sortie)
        self.assertFalse(valide)
        self.assertEqual(len(erreurs), 1)
        self.assertIn("xmlns", erreurs[0])

    def test_validation_sans_tracklist(self):
        """
        Role : une playlist sans balise trackList est declaree invalide.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        with open(self.sortie, "w", encoding="UTF-8") as fichier:
            fichier.write('<playlist version="1" xmlns="http://xspf.org/ns/0/"></playlist>')
        valide, erreurs = valider_playlist(self.sortie)
        self.assertFalse(valide)
        self.assertIn("trackList", erreurs[0])

    def test_validation_piste_sans_location(self):
        """
        Role : une piste sans balise location est declaree invalide.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        creer_playlist([{"location": self.chemin("a.mp3")}], self.sortie)
        texte = self.lire_texte(self.sortie)
        texte = texte.replace("<location>", "<x>").replace("</location>", "</x>")
        with open(self.sortie, "w", encoding="UTF-8") as fichier:
            fichier.write(texte)
        valide, erreurs = valider_playlist(self.sortie)
        self.assertFalse(valide)
        self.assertIn("location", erreurs[0])

    def test_validation_fichier_inexistant(self):
        """
        Role : valider un fichier qui n'existe pas renvoie (False, [une
        erreur]) au lieu de planter.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        valide, erreurs = valider_playlist(self.chemin("absent.xspf"))
        self.assertFalse(valide)
        self.assertEqual(len(erreurs), 1)

    # piste_depuis_fichier et playlist par defaut

    def test_piste_avec_metadonnees(self):
        """
        Role : une piste construite depuis un MP3 tagge reprend titre,
        artiste et album.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_mp3(self.chemin("a.mp3"), "Mon titre", "Mon artiste", "Mon album")
        self.assertEqual(piste_depuis_fichier(chemin), {
            "location": chemin, "title": "Mon titre",
            "creator": "Mon artiste", "album": "Mon album"})

    def test_piste_sans_tags_utilise_le_nom_du_fichier(self):
        """
        Role : sans tag, le titre de la piste est le nom du fichier.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = outils_audio.creer_mp3(self.chemin("sans_tags.mp3"))
        self.assertEqual(piste_depuis_fichier(chemin),
                         {"location": chemin, "title": "sans_tags.mp3"})

    def test_piste_fichier_illisible_ne_plante_pas(self):
        """
        Role : un fichier illisible ne provoque pas d'erreur : on garde son
        nom comme titre.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        chemin = self.chemin("abime.mp3")
        with open(chemin, "w") as fichier:
            fichier.write("pas de la musique")
        self.assertEqual(piste_depuis_fichier(chemin),
                         {"location": chemin, "title": "abime.mp3"})

    def test_playlist_par_defaut(self):
        """
        Role : la playlist par defaut contient tous les MP3/FLAC du dossier
        et de ses sous-dossiers (pas les autres fichiers), est valide et
        reprend les titres.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        os.makedirs(self.chemin("musique", "sous_dossier"))
        outils_audio.creer_mp3(self.chemin("musique", "a.mp3"), "Titre A", "Artiste A")
        outils_audio.creer_flac(self.chemin("musique", "sous_dossier", "b.flac"), "Titre B")
        with open(self.chemin("musique", "notes.txt"), "w") as fichier:
            fichier.write("ignore")

        resultat = generer_playlist_par_defaut(self.chemin("musique"), self.sortie)

        self.assertEqual(resultat, self.sortie)
        self.assertEqual(valider_playlist(self.sortie), (True, []))
        titres = sorted(piste["title"] for piste in lire_playlist(self.sortie))
        self.assertEqual(titres, ["Titre A", "Titre B"])

    def test_playlist_par_defaut_dossier_sans_musique(self):
        """
        Role : un dossier sans musique donne une playlist vide mais valide.

        Arguments :
            self (TestPlaylist) : instance de test

        Valeur renvoyee :
            None
        """
        os.makedirs(self.chemin("vide"))
        generer_playlist_par_defaut(self.chemin("vide"), self.sortie)
        self.assertEqual(lire_playlist(self.sortie), [])
        self.assertEqual(valider_playlist(self.sortie), (True, []))


if __name__ == "__main__":
    unittest.main()
