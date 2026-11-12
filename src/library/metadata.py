"""
metadata.py
Role : extraction des métadonnées d'un fichier audio MP3 (tags ID3) ou
       FLAC (tags Vorbis comment), avec la bibliothèque mutagen. Le
       résultat est renvoyé sous la forme d'un objet Track (cf track.py).
"""

import os

import mutagen

from .track import Track

# extensions de fichiers audio acceptées (les seules du sujet)
EXTENSIONS_SUPPORTEES = (".mp3", ".flac")


def extract_metadata(path):
    """
    Role : lit les métadonnées (titre, artiste, album, durée) d'un
    fichier MP3 ou FLAC et les renvoie dans un Track. Un tag absent
    donne une chaîne vide, et un fichier sans aucun tag est accepté.

    Arguments :
        path (str) : chemin du fichier MP3 ou FLAC à lire

    Valeur renvoyee :
        Track : le morceau, avec son chemin, son format ("mp3" ou
            "flac"), son titre, son artiste, son album et sa durée en
            secondes

    Exceptions levees :
        ValueError : si l'extension n'est pas .mp3 ou .flac, ou si le
            fichier est illisible ou corrompu
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in EXTENSIONS_SUPPORTEES:
        raise ValueError(f"Format non supporté : {ext}")

    # mutagen lève une erreur sur un fichier corrompu : on la convertit
    # en ValueError pour que le CLI et la GUI n'aient qu'un seul type
    # d'erreur à gérer
    try:
        audio = mutagen.File(path, easy=True)
    except mutagen.MutagenError as erreur:
        raise ValueError(f"Fichier audio illisible ou corrompu : {path}") from erreur
    # mutagen renvoie None quand il ne reconnaît pas le format du fichier
    if audio is None:
        raise ValueError(f"Fichier audio illisible : {path}")

    def premier(cle):
        """
        Role : renvoie la première valeur d'un tag (mutagen stocke chaque
        tag dans une liste), ou "" si le tag n'existe pas.

        Arguments :
            cle (str) : nom du tag ("title", "artist" ou "album")

        Valeur renvoyee :
            str : la valeur du tag, ou "" s'il est absent
        """
        valeurs = audio.tags.get(cle, []) if audio.tags else []
        return valeurs[0] if valeurs else ""

    return Track(
        path=path,
        format=ext[1:],
        title=premier("title"),
        artist=premier("artist"),
        album=premier("album"),
        duration=audio.info.length,
    )
