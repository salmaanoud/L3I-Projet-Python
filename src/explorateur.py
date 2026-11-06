#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
explorateur.py

Nom : explorateur.py
Role : exploration recursive d'un dossier pour recuperer tous les fichiers
       musicaux MP3 et FLAC (avec verification de l'extension ET du type
       MIME attendu, comme demande dans le sujet)
Auteur : LAIFAOUI Ines
Version : 1.0 - 05/11/2026
Licence : usage pedagogique (L3)
Compilation : aucune (Python interprete)
Execution : python3 explorateur.py <dossier>
"""

import os
import sys

# pour chaque extension musicale acceptee, le type MIME qui doit lui
# correspondre (c'est notre propre tableau de correspondance, pas besoin
# d'une librairie externe pour ca)
MIME_PAR_EXTENSION = {
    ".mp3": "audio/mpeg",
    ".flac": "audio/flac",
}


def deviner_type_mime(chemin):
    """
    Role : deduit le type MIME attendu d'un fichier a partir de son
    extension, en utilisant le tableau MIME_PAR_EXTENSION.

    Arguments :
        chemin (str) : chemin du fichier

    Valeur renvoyee :
        str ou None : le type MIME attendu (ex: "audio/mpeg"), ou None si
            l'extension n'est pas une extension musicale connue
    """
    _, extension = os.path.splitext(chemin)
    return MIME_PAR_EXTENSION.get(extension.lower())


def est_fichier_musical(chemin):
    """
    Role : verifie qu'un fichier est bien un MP3 ou un FLAC, en
    controlant a la fois son extension et le type MIME qui lui
    correspond (les deux sont demandes dans le sujet pour eviter de se
    fier a la seule extension).

    Arguments :
        chemin (str) : chemin du fichier a verifier

    Valeur renvoyee :
        bool : True si le fichier est un MP3 ou un FLAC valide, False sinon
    """
    _, extension = os.path.splitext(chemin)
    extension = extension.lower()

    if extension not in MIME_PAR_EXTENSION:
        return False

    type_mime_attendu = deviner_type_mime(chemin)
    return type_mime_attendu == MIME_PAR_EXTENSION[extension]


def lister_fichiers_musicaux(dossier):
    """
    Role : parcourt un dossier et tous ses sous-dossiers de maniere
    recursive, et recupere tous les fichiers MP3/FLAC trouves.

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
    for chemin in resultats:
        print(" -", chemin)
