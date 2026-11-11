# Gestion de fichiers audio et de playlists en Python

Projet de la mineure Python, L3 Informatique, CY Cergy Paris Université (semestre 5, 2026-2027).

Application qui analyse des fichiers audio **MP3** et **FLAC** (extraction des métadonnées) et génère des playlists au format **XSPF**, en mode console (CLI) et en mode graphique (GUI).

## Équipe

Groupe : Groupe projet 03

| Nom | Prénom |
|---|---|
| ANOUD | Salma |
| LAIFAOUI | Ines |
| SIMYA | Meriem |

## Répartition du travail

| Membre | Travail réalisé |
|---|---|
| **Meriem SIMYA** | Classe `Track` (`track.py`), extraction des métadonnées MP3 (ID3) et FLAC (Vorbis) (`metadata.py`), mode console (`cli.py`) |
| **Ines LAIFAOUI** | Exploration récursive d'un dossier avec vérification de l'extension et du type MIME (`explorateur.py`), génération, lecture et validation de playlists XSPF (`playlist_xspf.py`) |
| **Salma ANOUD** | Interface graphique Tkinter : fenêtre, arborescence et affichage des métadonnées (`gui.py`) |

## Fonctionnalités

- Extraction des métadonnées d'un fichier MP3 ou FLAC : titre, artiste, album, durée
- Exploration récursive d'un dossier (seuls les MP3 et FLAC sont retenus)
- Génération, lecture et validation de playlists XSPF
- Mode console avec les options `-f`, `-d`, `-o` et `-h`, et des messages d'erreur clairs
- Interface graphique avec arborescence et affichage des métadonnées

## Installation

Le projet est écrit en Python 3 et utilise une seule bibliothèque externe, `mutagen`.

1. Récupérer le projet :

```
git clone https://github.com/salmaanoud/L3I-Projet-Python.git
cd L3I-Projet-Python
```

2. Créer un environnement virtuel et l'activer (sous Linux ou macOS, remplacer la dernière ligne par `source venv/bin/activate`) :

```
python -m venv venv
venv\Scripts\activate
```

3. Installer la bibliothèque :

```
pip install mutagen
```

## Utilisation

### Mode console

Depuis le dossier `src/cli` :

```
python cli.py -h
python cli.py -f morceau.mp3
python cli.py -d ./musique
python cli.py -d ./musique -o playlist.xspf
```

- `-h` : affiche l'aide
- `-f` : affiche les métadonnées d'un fichier
- `-d` : analyse un dossier, sous-dossiers compris
- `-o` : avec `-d`, génère aussi une playlist XSPF

Sans paramètre, le programme affiche un message d'erreur qui propose `-h`. Les options `-f` et `-d` sont exclusives.

### Mode graphique

Depuis le dossier `src/gui` :

```
python gui.py
```

## Organisation du dépôt

```
doc/          documentation, rapport, diaporama, démonstration
src/
  library/    Track, extraction des métadonnées, exploration, playlists XSPF
  cli/        mode console
  gui/        interface graphique (Tkinter)
  tests-auto/ tests automatiques
README.md
```