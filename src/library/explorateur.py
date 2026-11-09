
"""
explorateur.py
Role : exploration recursive d'un dossier pour recuperer tous les fichiers
       musicaux MP3 et FLAC. Un fichier n'est retenu que si son extension
       est bonne ET si le type MIME lu dans le contenu du fichier (ses
       premiers octets) correspond a cette extension, comme demande dans
       le sujet.
"""

import os
import sys

# pour chaque extension musicale acceptee, le type MIME qui doit lui
# correspondre
MIME_PAR_EXTENSION = {
    ".mp3": "audio/mpeg",
    ".flac": "audio/flac",
}


def deviner_type_mime(chemin):
    """
    Role : deduit le type MIME reel d'un fichier en lisant ses premiers
    octets (sa "signature"), sans se fier a son extension. Un FLAC
    commence par "fLaC". Un MP3 commence soit par "ID3" (fichier avec tags
    ID3v2), soit directement par une trame MPEG (un octet 0xFF suivi d'un
    octet dont les 3 premiers bits valent 1).

    Arguments :
        chemin (str) : chemin du fichier a analyser

    Valeur renvoyee :
        str ou None : "audio/flac" ou "audio/mpeg" si la signature est
            reconnue, None si elle ne l'est pas ou si le fichier est
            illisible
    """
    try:
        with open(chemin, "rb") as fichier:
            debut = fichier.read(4)
    except OSError:
        return None

    if debut.startswith(b"fLaC"):
        return "audio/flac"

    if debut.startswith(b"ID3"):
        return "audio/mpeg"

    # trame MPEG sans tag ID3 : 0xFF puis un octet de la forme 111xxxxx
    if len(debut) >= 2 and debut[0] == 0xFF and (debut[1] & 0xE0) == 0xE0:
        return "audio/mpeg"

    return None


def est_fichier_musical(chemin):
    """
    Role : verifie qu'un fichier est bien un MP3 ou un FLAC, en
    controlant a la fois son extension et son type MIME reel (lu dans le
    contenu du fichier). Les deux doivent etre coherents : un fichier
    "faux.mp3" qui ne contient pas de vrai MP3 est refuse.

    Arguments :
        chemin (str) : chemin du fichier a verifier

    Valeur renvoyee :
        bool : True si le fichier est un MP3 ou un FLAC valide, False sinon
    """
    _, extension = os.path.splitext(chemin)
    extension = extension.lower()

    if extension not in MIME_PAR_EXTENSION:
        return False

    type_mime_reel = deviner_type_mime(chemin)
    return type_mime_reel == MIME_PAR_EXTENSION[extension]


def lister_fichiers_musicaux(dossier):
    """
    Role : parcourt un dossier et tous ses sous-dossiers de maniere
    recursive, et recupere tous les fichiers MP3/FLAC valides trouves.

    Arguments :
        dossier (str) : chemin du dossier a explorer

    Valeur renvoyee :
        list[str] : liste des chemins complets des fichiers MP3/FLAC trouves
    """
    fichiers_trouves = []

    for racine, _, fichiers in os.walk(dossier):
        for nom_fichier in fichiers:
            chemin_complet = os.path.join(racine, nom_fichier)
            if est_fichier_musical(chemin_complet):
                fichiers_trouves.append(chemin_complet)

    return fichiers_trouves


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python3 explorateur.py <dossier>")
        sys.exit(1)

    dossier_cible = sys.argv[1]
    resultats = lister_fichiers_musicaux(dossier_cible)
    print(f"{len(resultats)} fichier(s) musical(aux) trouve(s) :")
    for fichier_trouve in resultats:
        print(" -", fichier_trouve)