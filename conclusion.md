# Conclusion du point d'avancement n°1 (Groupe 03)

Groupe : LAIFAOUI Ines, SIMYA Meriem, ANOUD Salma

## Ce qui est fonctionnel

- Exploration récursive d'un dossier avec vérification de l'extension ET du
  type MIME lu dans le contenu du fichier (Ines)
- Extraction des métadonnées MP3/FLAC : titre, artiste, album, durée (Meriem)
- Génération, relecture et validation d'une playlist XSPF par défaut
  `default_playlist.xspf` (Ines)
- Interface en ligne de commande : options `-f`, `-d`, `-o` et `-h` (Meriem)
- Interface graphique : choix d'un dossier ou d'un morceau, tableau des
  morceaux, panneau d'informations, génération de la playlist (Salma)
- Tests automatiques (unittest) des modules d'exploration et de playlist :
  37 tests, qui passent sous Linux et Windows [À VÉRIFIER : ajouter les
  tests de Meriem et Salma une fois lancés ensemble]

## Difficultés surmontées

- Contrôle du type MIME : au départ on ne regardait que l'extension, ce qui
  acceptait un faux MP3. On lit maintenant les premiers octets du fichier
  (signature `fLaC`, `ID3` ou trame MPEG) et on les compare à l'extension.
- Fichiers corrompus : en testant avec un faux MP3, la génération de la
  playlist plantait car l'erreur de lecture n'était pas rattrapée. C'est
  corrigé : l'erreur est gérée et le morceau garde son nom de fichier
  comme titre.
- Imports du package `library` : erreur « attempted relative import with no
  known parent package ». On a compris qu'il faut lancer le code comme un
  module depuis `src` (`python3 -m library.playlist_xspf`) ou passer par
  `cli.py`, qui ajoute `src` au chemin de recherche.
- Installation de `mutagen` : le module restait introuvable car `pip` et
  `python3` ne désignaient pas le même interpréteur. Réglé avec
  `python3 -m pip install mutagen`.
- Chemins de test : un dossier inexistant ne produit aucune erreur avec
  `os.walk`, il renvoie simplement une liste vide. On a mis du temps à
  comprendre pourquoi la playlist sortait vide (mauvais chemin).

## Items commencés

- [À VÉRIFIER avec Meriem et Salma : lecture audio, modification des tags,
  pochettes, glisser-déposer, API web. Indiquer ceux qui sont réellement
  commencés, sinon supprimer cette section.]
- Rédaction de la documentation au format demandé (rôle, arguments, valeur
  renvoyée) : faite pour les modules d'exploration et de playlist, ainsi que
  pour leurs tests.

## Items restants

- Lecture d'un morceau ou d'une playlist, en console et en graphique
- Modification et sauvegarde des tags
- Récupération des informations complètes d'un album et des paroles via une
  API web (console et graphique)
- Extraction, téléchargement et sauvegarde des pochettes
- Glisser-déposer pour composer une playlist dans la GUI
- Corrections de l'affichage de la colonne Format dans la GUI
- Documentation générée (pdoc) pour tout le projet, rapport, README,
  vidéo de démonstration, diaporama
- Tests des autres modules (CLI, GUI, métadonnées)