"""
cli.py
Role : interface en ligne de commande (CLI) du projet : affichage des
       métadonnées d'un fichier MP3/FLAC, analyse récursive d'un dossier et
       génération d'une playlist XSPF. Réutilise la bibliothèque
       (metadata.py, explorateur.py, playlist_xspf.py).

Execution :
    python3 cli.py -h
    python3 cli.py -f music.mp3
    python3 cli.py -d ./music/
    python3 cli.py -d ./music/ -o playlist.xspf
"""

import argparse
import os
import sys

# Permet de lancer « python3 cli.py » depuis src/cli : on ajoute src au chemin
# de recherche pour que « import library » fonctionne.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library.metadata import extract_metadata  # noqa: E402
from library.explorateur import lister_fichiers_musicaux  # noqa: E402
from library.playlist_xspf import generer_playlist_par_defaut  # noqa: E402


def format_duree(secondes):
    """
    Role : convertit une durée en secondes en texte au format mm:ss.

    Arguments :
        secondes (float) : durée en secondes

    Valeur renvoyee :
        str : la durée arrondie à la seconde, par exemple "03:34"
    """
    total = int(round(secondes))
    return f"{total // 60:02d}:{total % 60:02d}"


def afficher_track(track):
    """
    Role : affiche dans la console les métadonnées d'un morceau (fichier,
    format, titre, artiste, album, durée). Un champ vide est affiché
    "(inconnu)".

    Arguments :
        track (Track) : le morceau à afficher

    Valeur renvoyee :
        None
    """
    print(f"Fichier : {track.path}")
    print(f"Format  : {track.format.upper()}")
    print(f"Titre   : {track.title or '(inconnu)'}")
    print(f"Artiste : {track.artist or '(inconnu)'}")
    print(f"Album   : {track.album or '(inconnu)'}")
    print(f"Durée   : {format_duree(track.duration)}")


def creer_parser():
    """
    Role : construit l'analyseur de la ligne de commande (argparse) avec
    les options -h, -f, -d et -o. Les options -f (fichier) et -d
    (dossier) sont exclusives l'une de l'autre, comme demandé dans le
    sujet.

    Arguments :
        aucun

    Valeur renvoyee :
        argparse.ArgumentParser : l'analyseur prêt à lire les arguments
    """
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Analyse de fichiers audio MP3/FLAC et génération de playlists XSPF.",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help",
        help="affiche cette aide et quitte",
    )
    # un seul des deux à la fois : argparse refuse -f et -d ensemble
    entree = parser.add_mutually_exclusive_group()
    entree.add_argument(
        "-f", "--file", metavar="FICHIER",
        help="fichier MP3 ou FLAC dont on affiche les métadonnées",
    )
    entree.add_argument(
        "-d", "--directory", metavar="DOSSIER",
        help="dossier à explorer (récursivement) pour générer une playlist",
    )
    parser.add_argument(
        "-o", "--output", metavar="PLAYLIST.xspf",
        help="fichier XSPF où sauvegarder la playlist (à utiliser avec -d)",
    )
    return parser


def traiter_fichier(chemin):
    """
    Role : option -f. Lit les métadonnées d'un fichier MP3 ou FLAC et les
    affiche. Si le fichier n'existe pas ou n'est pas lisible, affiche un
    message d'erreur sur la sortie d'erreur.

    Arguments :
        chemin (str) : chemin du fichier à analyser

    Valeur renvoyee :
        int : 0 si tout s'est bien passé, 1 en cas d'erreur
    """
    if not os.path.isfile(chemin):
        print(f"Erreur : le fichier « {chemin} » n'existe pas.", file=sys.stderr)
        return 1
    try:
        track = extract_metadata(chemin)
    except ValueError as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1
    afficher_track(track)
    return 0


def traiter_dossier(dossier, sortie):
    """
    Role : option -d. Explore un dossier et tous ses sous-dossiers,
    affiche les métadonnées de chaque MP3/FLAC trouvé, puis génère une
    playlist XSPF si un fichier de sortie est demandé (option -o). Un
    fichier illisible est signalé ("Ignoré") sans arrêter le programme.

    Arguments :
        dossier (str) : chemin du dossier à explorer
        sortie (str ou None) : chemin du fichier .xspf à créer, ou None
            pour ne pas générer de playlist

    Valeur renvoyee :
        int : 0 si tout s'est bien passé, 1 si le dossier n'existe pas
    """
    if not os.path.isdir(dossier):
        print(f"Erreur : le dossier « {dossier} » n'existe pas.", file=sys.stderr)
        return 1

    chemins = lister_fichiers_musicaux(dossier)
    tracks = []
    for chemin in chemins:
        try:
            tracks.append(extract_metadata(chemin))
        except ValueError as erreur:
            print(f"Ignoré : {erreur}", file=sys.stderr)

    for numero, track in enumerate(tracks, start=1):
        print(f"--- Morceau {numero} ---")
        afficher_track(track)

    if sortie:
        generer_playlist_par_defaut(dossier, sortie)
        print(f"Playlist enregistrée dans « {sortie} ».")
    return 0


def main(argv=None):
    """
    Role : point d'entrée du mode console. Lit la ligne de commande, vérifie
    les combinaisons d'options, puis lance le traitement d'un fichier (-f)
    ou d'un dossier (-d). Sans paramètre, affiche une erreur qui propose
    l'aide (-h).

    Arguments :
        argv (list[str] ou None) : arguments de la ligne de commande
            (par défaut ceux de sys.argv ; une liste permet de tester la
            fonction sans passer par le terminal)

    Valeur renvoyee :
        int : code de sortie du programme (0 si tout s'est bien passé)
    """
    parser = creer_parser()
    args = parser.parse_args(argv)

    if args.file is None and args.directory is None:
        parser.error("aucun paramètre : indiquez -f FICHIER ou -d DOSSIER. "
                     "Tapez -h (ou --help) pour obtenir de l'aide.")
    if args.output and args.directory is None:
        parser.error("l'option -o s'utilise avec -d (génération d'une playlist).")

    if args.file is not None:
        return traiter_fichier(args.file)
    return traiter_dossier(args.directory, args.output)


if __name__ == "__main__":
    sys.exit(main())
