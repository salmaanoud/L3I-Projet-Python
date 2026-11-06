"""Structure de données commune représentant un morceau de musique (MP3 ou FLAC).

Règle du groupe : on peut AJOUTER des champs (avec une valeur par défaut),
mais on ne renomme ni ne supprime jamais un champ sans prévenir tout le monde.
"""

from dataclasses import dataclass


@dataclass
class Track:
    """Un morceau de musique et ses principales métadonnées.

    Attributes:
        path: chemin du fichier audio.
        format: "mp3" ou "flac" (en minuscules, sans le point).
        title: titre du morceau ("" si absent).
        artist: nom de l'artiste ("" si absent).
        album: nom de l'album ("" si absent).
        duration: durée en secondes (float). L'affichage en mm:ss est
            à la charge de la GUI / du CLI.
    """

    path: str
    format: str
    title: str = ""
    artist: str = ""
    album: str = ""
    duration: float = 0.0