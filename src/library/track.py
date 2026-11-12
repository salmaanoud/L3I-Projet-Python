"""
track.py
Role : structure de données commune représentant un morceau de musique
       (MP3 ou FLAC) et ses principales métadonnées. Elle est partagée par
       la bibliothèque (metadata.py, playlist_xspf.py), le mode console
       (cli.py) et l'interface graphique (gui.py).

       Règle du groupe : on peut AJOUTER des champs (avec une valeur par
       défaut), mais on ne renomme ni ne supprime jamais un champ sans
       prévenir tout le monde.
"""

from dataclasses import dataclass


@dataclass
class Track:
    """
    Role : représente un morceau de musique et ses principales
    métadonnées (celles lues dans les tags ID3 d'un MP3 ou Vorbis d'un
    FLAC).

    Attributs :
        path (str) : chemin du fichier audio
        format (str) : "mp3" ou "flac" (en minuscules, sans le point)
        title (str) : titre du morceau ("" si absent)
        artist (str) : nom de l'artiste ("" si absent)
        album (str) : nom de l'album ("" si absent)
        duration (float) : durée en secondes (l'affichage en mm:ss est à
            la charge de la GUI et du CLI)
    """

    path: str
    format: str
    title: str = ""
    artist: str = ""
    album: str = ""
    duration: float = 0.0
