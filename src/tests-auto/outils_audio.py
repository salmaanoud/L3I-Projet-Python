"""Outils pour les tests : fabrique de minuscules fichiers MP3 / FLAC valides.

Les fichiers .mp3 et .flac sont ignorés par git (voir .gitignore), donc les
tests les créent à la volée dans un dossier temporaire au lieu de les stocker
dans le dépôt.
"""

import os
import sys

import mutagen
import mutagen.flac

# Permet de lancer les tests depuis n'importe où : on ajoute src (pour
# « import library ») et src/cli (pour « import cli ») au chemin de recherche.
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for dossier in (SRC, os.path.join(SRC, "cli")):
    if dossier not in sys.path:
        sys.path.insert(0, dossier)

# Une trame MPEG-1 Layer III, 128 kbit/s, 44,1 kHz fait 417 octets et dure
# 1152 / 44100 s. 40 trames donnent donc environ 1,04 s.
_ENTETE_TRAME_MP3 = bytes([0xFF, 0xFB, 0x90, 0x00])
_TAILLE_TRAME_MP3 = 417
NB_TRAMES_MP3 = 40
DUREE_MP3 = NB_TRAMES_MP3 * 1152 / 44100

# Un FLAC minimal : la signature « fLaC » puis le bloc STREAMINFO, pour
# 1 seconde de son stéréo 16 bits à 44,1 kHz (sans aucune trame audio).
FREQUENCE_FLAC = 44100
DUREE_FLAC = 1.0


def _ajouter_tags(chemin, titre, artiste, album):
    """Écrit titre / artiste / album dans le fichier (ID3 ou Vorbis)."""
    audio = mutagen.File(chemin, easy=True)
    if audio.tags is None:
        audio.add_tags()
    if titre:
        audio["title"] = titre
    if artiste:
        audio["artist"] = artiste
    if album:
        audio["album"] = album
    audio.save()


def creer_mp3(chemin, titre="", artiste="", album=""):
    """Crée un petit MP3 valide, avec des tags ID3 si on en donne."""
    trame = _ENTETE_TRAME_MP3 + bytes(_TAILLE_TRAME_MP3 - len(_ENTETE_TRAME_MP3))
    with open(chemin, "wb") as fichier:
        fichier.write(trame * NB_TRAMES_MP3)
    if titre or artiste or album:
        _ajouter_tags(chemin, titre, artiste, album)
    return chemin


def creer_flac(chemin, titre="", artiste="", album=""):
    """Crée un petit FLAC valide, avec des tags Vorbis si on en donne."""
    total_echantillons = int(FREQUENCE_FLAC * DUREE_FLAC)
    # 20 bits de fréquence | 3 bits (canaux - 1) | 5 bits (bits - 1) | 36 bits
    champ = (FREQUENCE_FLAC << 44) | (1 << 41) | (15 << 36) | total_echantillons
    streaminfo = (
        (4096).to_bytes(2, "big")       # taille de bloc min
        + (4096).to_bytes(2, "big")     # taille de bloc max
        + bytes(3) + bytes(3)           # taille de trame min / max (inconnues)
        + champ.to_bytes(8, "big")
        + bytes(16)                     # empreinte MD5 (inconnue)
    )
    entete_bloc = bytes([0x80]) + len(streaminfo).to_bytes(3, "big")
    with open(chemin, "wb") as fichier:
        fichier.write(b"fLaC" + entete_bloc + streaminfo)
    if titre or artiste or album:
        _ajouter_tags(chemin, titre, artiste, album)
    return chemin
