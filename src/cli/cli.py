"""Interface en ligne de commande (CLI) : extraction de métadonnées et playlists.

Exemples :
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


def format_duree(secondes):
    """Convertit une durée en secondes en texte mm:ss."""
    total = int(round(secondes))
    return f"{total // 60:02d}:{total % 60:02d}"


def afficher_track(track):
    """Affiche les métadonnées d'un Track dans la console."""
    print(f"Fichier : {track.path}")
    print(f"Format  : {track.format.upper()}")
    print(f"Titre   : {track.title or '(inconnu)'}")
    print(f"Artiste : {track.artist or '(inconnu)'}")
    print(f"Album   : {track.album or '(inconnu)'}")
    print(f"Durée   : {format_duree(track.duration)}")


def creer_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Analyse de fichiers audio MP3/FLAC et génération de playlists XSPF.",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help",
        help="affiche cette aide et quitte",
    )
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
    if not os.path.isdir(dossier):
        print(f"Erreur : le dossier « {dossier} » n'existe pas.", file=sys.stderr)
        return 1

    # Ces fonctions sont écrites par Ines (exploration + playlists XSPF).
    try:
        from library.explorer import scan_directory
    except ImportError:
        print("Le parcours de dossier (-d) n'est pas encore disponible.", file=sys.stderr)
        return 1

    chemins = scan_directory(dossier)
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
        try:
            from library.playlist import save_playlist
        except ImportError:
            print("La sauvegarde XSPF (-o) n'est pas encore disponible.", file=sys.stderr)
            return 1
        save_playlist(tracks, sortie)
        print(f"Playlist enregistrée dans « {sortie} ».")
    return 0


def main(argv=None):
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