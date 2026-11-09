import os

import mutagen

from .track import Track

EXTENSIONS_SUPPORTEES = (".mp3", ".flac")


def extract_metadata(path):
    """Lit les métadonnées d'un fichier MP3 (ID3) ou FLAC (Vorbis) et renvoie un Track."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in EXTENSIONS_SUPPORTEES:
        raise ValueError(f"Format non supporté : {ext}")

    try:
        audio = mutagen.File(path, easy=True)
    except mutagen.MutagenError as erreur:
        raise ValueError(f"Fichier audio illisible ou corrompu : {path}") from erreur
    if audio is None:
        raise ValueError(f"Fichier audio illisible : {path}")

    def premier(cle):
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