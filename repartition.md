# Répartition du travail — Groupe projet 03

## 1. Membres du groupe

- Salma ANOUD
- Ines LAIFAOUI
- Meriem SIMYA

## 2. Travail réalisé au 13 novembre 2026

### Meriem SIMYA
- Création de la classe `Track` (`track.py`).
- Extraction des métadonnées MP3 et FLAC (`metadata.py`).
- Développement de l'interface en ligne de commande (`cli.py`) avec les options `-f`, `-d`, `-o` et `-h`.
- Gestion des erreurs dans l'interface en ligne de commande.
-  Création de trente-six tests automatiques : classe `Track`, extraction des métadonnées et interface en ligne de commande (`test_track.py`, `test_metadata.py`, `test_cli.py`).

### Ines LAIFAOUI
- Développement de l'exploration récursive des dossiers (`explorateur.py`).
- Vérification des extensions et des types MIME des fichiers MP3 et FLAC.
- Développement de la génération, de la lecture et de la validation des playlists XSPF (`playlist_xspf.py`).
- Création de trente-sept tests automatiques : exploration des dossiers et playlists XSPF (`test_explorateur.py`, `test_playlist_xspf.py`).

### Salma ANOUD
- Développement de l'interface graphique avec Tkinter (`gui.py`).
- Mise en place de la sélection des dossiers et des fichiers musicaux.
- Affichage de l'arborescence et des métadonnées des morceaux.
- Intégration de la génération des playlists XSPF dans l'interface.
- Création de six tests automatiques de l'interface graphique (`test_gui.py`).

## 3. Organisation du groupe

Le projet est réalisé en mode hybride, avec une organisation combinant le travail en présentiel et à distance.

Chaque membre est responsable des fonctionnalités qui lui ont été attribuées, conformément au diagramme de Gantt.

Le dépôt GitHub commun permet de partager le code source, de suivre les modifications et d'intégrer progressivement les différents modules du projet.

Les membres du groupe collaborent pour assurer la cohérence entre les différentes fonctionnalités de l'application.

## 4. Travaux prévus après le point d'avancement

- **Meriem :** modification et sauvegarde des tags musicaux.
- **Ines :** intégration d'une API web pour les informations des albums et les paroles.
- **Salma :** ajout de la lecture audio dans l'application.
