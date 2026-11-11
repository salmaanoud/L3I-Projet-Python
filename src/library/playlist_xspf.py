
"""
playlist_xspf.py
Role : generation, lecture et validation de playlists au format XSPF
       (format texte/XML standard, cf https://xspf.org/), y compris la
       playlist par defaut regroupant tous les MP3/FLAC d'un dossier
       explore recursivement, avec leurs vraies metadonnees ID3/Vorbis
       quand elles sont disponibles (module metadata.py). Le fichier XSPF
       est construit et relu a la main, avec de simples chaines de
       caracteres, sans librairie XML.
"""

import os
import sys

# import relatif car explorateur.py et metadata.py sont dans le meme
# package (library) ; le except gere le cas ou on lance ce fichier tout
# seul (python3 playlist_xspf.py), sans passer par le package
try:
    from .explorateur import lister_fichiers_musicaux
    from .metadata import extract_metadata
except ImportError:
    from explorateur import lister_fichiers_musicaux
    from metadata import extract_metadata

ESPACE_DE_NOMS_XSPF = "http://xspf.org/ns/0/"

# les champs qu'une piste peut avoir, dans l'ordre ou on les ecrit
CHAMPS_PISTE = ("location", "title", "creator", "album")


def echapper_xml(texte):
    """
    Role : remplace les caracteres speciaux XML (&, <, >, ") par leur
    equivalent echappe, pour ne pas casser le fichier XSPF genere.

    Arguments :
        texte (str) : texte a echapper

    Valeur renvoyee :
        str : le texte avec les caracteres speciaux remplaces
    """
    texte = texte.replace("&", "&amp;")
    texte = texte.replace("<", "&lt;")
    texte = texte.replace(">", "&gt;")
    texte = texte.replace('"', "&quot;")
    return texte


def deechapper_xml(texte):
    """
    Role : fait l'operation inverse de echapper_xml, pour retrouver le
    texte original quand on relit un fichier XSPF.

    Arguments :
        texte (str) : texte echappe a convertir

    Valeur renvoyee :
        str : le texte avec les caracteres speciaux remis sous leur forme normale
    """
    texte = texte.replace("&lt;", "<")
    texte = texte.replace("&gt;", ">")
    texte = texte.replace("&quot;", '"')
    texte = texte.replace("&amp;", "&")
    return texte


def chemin_vers_uri(chemin):
    """
    Role : transforme un chemin de fichier (relatif ou absolu, Windows ou
    Linux) en une URI de la forme file:///..., comme l'exige le format
    XSPF pour la balise <location>.

    Arguments :
        chemin (str) : chemin du fichier

    Valeur renvoyee :
        str : l'URI correspondante (ex: "file:///home/ines/musique/a.mp3")
    """
    chemin_absolu = os.path.abspath(chemin).replace("\\", "/")
    if not chemin_absolu.startswith("/"):
        # cas Windows, ou le chemin absolu commence par "C:/..."
        chemin_absolu = "/" + chemin_absolu
    return "file://" + chemin_absolu


def creer_playlist(pistes, chemin_sortie):
    """
    Role : cree un fichier XSPF (playlist au format texte/XML) a partir
    d'une liste de pistes.

    Arguments :
        pistes (list[dict]) : liste de pistes, chaque piste etant un
            dictionnaire avec les cles possibles "location" (str,
            obligatoire, chemin du fichier), "title" (str), "creator"
            (str, artiste) et "album" (str). Seule "location" est
            obligatoire, les autres cles sont facultatives.
        chemin_sortie (str) : chemin du fichier .xspf a creer

    Valeur renvoyee :
        None : le fichier est ecrit directement sur le disque
    """
    lignes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<playlist version="1" xmlns="{ESPACE_DE_NOMS_XSPF}">',
        "  <trackList>",
    ]

    for piste in pistes:
        lignes.append("    <track>")

        uri = chemin_vers_uri(piste["location"])
        lignes.append(f"      <location>{echapper_xml(uri)}</location>")

        for champ in ("title", "creator", "album"):
            if piste.get(champ):
                valeur = echapper_xml(piste[champ])
                lignes.append(f"      <{champ}>{valeur}</{champ}>")

        lignes.append("    </track>")

    lignes.append("  </trackList>")
    lignes.append("</playlist>")

    with open(chemin_sortie, "w", encoding="UTF-8") as fichier:
        fichier.write("\n".join(lignes) + "\n")


def piste_depuis_fichier(chemin):
    """
    Role : construit le dictionnaire d'une piste pour un fichier audio, en
    utilisant ses vraies metadonnees (titre, artiste, album) quand elles
    sont lisibles, et en se rabattant sur le nom du fichier comme titre si
    le fichier est illisible ou sans metadonnees.

    Arguments :
        chemin (str) : chemin du fichier audio

    Valeur renvoyee :
        dict : une piste au format attendu par creer_playlist (cles
            "location", "title", et "creator"/"album" si disponibles)
    """
    try:
        morceau = extract_metadata(chemin)
    except ValueError:
        # un fichier abime ou illisible ne doit pas bloquer la generation
        # de toute la playlist, on garde juste le nom du fichier comme titre
        return {"location": chemin, "title": os.path.basename(chemin)}

    piste = {"location": chemin, "title": morceau.title or os.path.basename(chemin)}
    if morceau.artist:
        piste["creator"] = morceau.artist
    if morceau.album:
        piste["album"] = morceau.album
    return piste


def generer_playlist_par_defaut(dossier, chemin_sortie="default_playlist.xspf"):
    """
    Role : genere la playlist par defaut demandee dans le sujet : tous
    les MP3/FLAC trouves recursivement dans "dossier", avec leurs vraies
    metadonnees ID3/Vorbis (titre, artiste, album) quand elles sont
    disponibles, recuperees via extract_metadata (module metadata.py).

    Arguments :
        dossier (str) : dossier a explorer recursivement
        chemin_sortie (str) : chemin du fichier .xspf a creer (par defaut
            "default_playlist.xspf")

    Valeur renvoyee :
        str : le chemin du fichier .xspf genere (= chemin_sortie)
    """
    fichiers = lister_fichiers_musicaux(dossier)
    pistes = [piste_depuis_fichier(chemin) for chemin in fichiers]
    creer_playlist(pistes, chemin_sortie)
    return chemin_sortie


def extraire_contenu_balise(ligne, balise):
    """
    Role : si une ligne contient une balise complete du type
    <balise>contenu</balise>, renvoie son contenu (sans les balises).

    Arguments :
        ligne (str) : une ligne de texte issue du fichier XSPF
        balise (str) : le nom de la balise recherchee (ex: "title")

    Valeur renvoyee :
        str ou None : le contenu de la balise (deja deechappe), ou None
            si la ligne ne contient pas cette balise
    """
    ouverture = f"<{balise}>"
    fermeture = f"</{balise}>"

    if ouverture in ligne and fermeture in ligne:
        debut = ligne.index(ouverture) + len(ouverture)
        fin = ligne.index(fermeture)
        return deechapper_xml(ligne[debut:fin])

    return None


def lire_playlist(chemin):
    """
    Role : lit un fichier XSPF existant et renvoie la liste des pistes
    qu'il contient.

    Arguments :
        chemin (str) : chemin du fichier .xspf a lire

    Valeur renvoyee :
        list[dict] : liste de pistes, sous la meme forme de dictionnaires
            que celle attendue par creer_playlist (cles possibles :
            "location", "title", "creator", "album")
    """
    pistes = []
    piste_courante = None

    with open(chemin, encoding="UTF-8") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()

            if ligne == "<track>":
                piste_courante = {}
            elif ligne == "</track>" and piste_courante is not None:
                pistes.append(piste_courante)
                piste_courante = None
            elif piste_courante is not None:
                for champ in CHAMPS_PISTE:
                    contenu = extraire_contenu_balise(ligne, champ)
                    if contenu is not None:
                        piste_courante[champ] = contenu

    return pistes


def valider_playlist(chemin):
    """
    Role : verifie qu'un fichier XSPF a la structure minimale attendue :
    presence de la balise racine <playlist> avec le bon espace de noms,
    presence d'une balise <trackList>, et une <location> pour chaque
    piste.

    Arguments :
        chemin (str) : chemin du fichier .xspf a valider

    Valeur renvoyee :
        tuple[bool, list[str]] : (True, []) si le fichier est valide,
            sinon (False, liste_des_erreurs) ou chaque erreur est decrite
            en une phrase
    """
    erreurs = []

    try:
        with open(chemin, encoding ="UTF-8") as fichier:
            contenu = fichier.read()
    except OSError as erreur:
        return False, [f"impossible de lire le fichier : {erreur}"]

    if "<playlist" not in contenu or ESPACE_DE_NOMS_XSPF not in contenu:
        erreurs.append("il manque la balise racine <playlist> avec le bon espace de noms (xmlns)")

    if "<trackList>" not in contenu:
        erreurs.append("il manque la balise <trackList>")

    nb_pistes = contenu.count("<track>")
    nb_locations = contenu.count("<location>")
    if nb_pistes != nb_locations:
        erreurs.append(
            f"{nb_pistes} piste(s) trouvee(s) mais seulement {nb_locations} "
            "balise(s) <location> : chaque piste doit avoir une location"
        )

    return len(erreurs) == 0, erreurs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python3 playlist_xspf.py <dossier>")
        sys.exit(1)

    dossier_cible = sys.argv[1]
    fichier_genere = generer_playlist_par_defaut(dossier_cible)
    print(f"Playlist par defaut generee : {fichier_genere}")

    est_valide, liste_erreurs = valider_playlist(fichier_genere)
    if est_valide:
        print("La playlist generee est valide.")
    else:
        print("Erreurs trouvees dans la playlist :", liste_erreurs)

    print("\nContenu relu depuis le fichier :")
    for piste_lue in lire_playlist(fichier_genere):
        print(" -", piste_lue)