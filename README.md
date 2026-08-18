# Mastermind

[![Tests](https://github.com/guillaumeboileaupro/Mastermind/actions/workflows/tests.yml/badge.svg)](https://github.com/guillaumeboileaupro/Mastermind/actions/workflows/tests.yml)
[![Paquet Ubuntu](https://github.com/guillaumeboileaupro/Mastermind/actions/workflows/build-ubuntu.yml/badge.svg)](https://github.com/guillaumeboileaupro/Mastermind/actions/workflows/build-ubuntu.yml)

Jeu Mastermind avec **interface desktop PyQt6 entièrement en Python**, API
FastAPI optionnelle et persistance SQLite. Le projet ne contient aucun code
JavaScript.

## Modes de jeu

Deux modes utilisent la même logique Mastermind :

- **Couleurs** : rouge, bleu, vert, jaune, violet, orange.
- **Chiffres** : 1, 2, 3, 4, 5, 6.

Les couleurs sont transmises et persistées directement sous forme de codes
hexadécimaux CSS, sans identifiant textuel intermédiaire.

Dans les deux modes :

- le code secret contient **4 positions** ;
- les valeurs peuvent être **réutilisées** ;
- le score d'une tentative est affiché sur deux chiffres :
  - premier chiffre = nombre de valeurs bien placées ;
  - second chiffre = nombre de valeurs correctes mais mal placées.

Exemple : `21` signifie 2 valeurs bien placées et 1 valeur correcte mal placée.

## Fonctions

- application graphique installable sur Ubuntu ;
- logo Mastermind comme icône de l'application ;
- sélection du mode de jeu ;
- génération d'un code secret ;
- affichage graphique des 6 couleurs ;
- interface native sans navigateur ni serveur web local ;
- difficulté normale ou facile enfant avec un indice par position ;
- validation des tentatives avec gestion correcte des doublons ;
- reprise d'une partie active après redémarrage ;
- chronomètre de la partie en cours ;
- score courant et score final ;
- score total cumulé ;
- historique persistant des parties ;
- nombre de victoires ;
- abandon d'une partie ;
- changement de mode en démarrant une nouvelle partie.

## Installer sur Ubuntu

Le workflow **Build Ubuntu package** construit et publie comme artefact le
paquet `mastermind_0.1.0_amd64.deb` à chaque modification de `main`.

Après une construction locale depuis la racine du projet :

```bash
sudo apt install ./dist/mastermind_0.1.0_amd64.deb
```

Pour un artefact téléchargé depuis GitHub Actions, utiliser son chemin réel, par
exemple depuis le dossier de téléchargement :

```bash
cd ~/Téléchargements
sudo apt install ./mastermind_0.1.0_amd64.deb
```

Mastermind apparaît ensuite dans le menu des applications Ubuntu, catégorie **Jeux**.

Pour le désinstaller :

```bash
sudo apt remove mastermind
```

Les parties et statistiques sont conservées dans :

```text
~/.local/share/mastermind/mastermind.db
```

Désinstaller le paquet ne supprime donc pas automatiquement l'historique personnel.

## Lancer la version de développement

Le projet nécessite **Python 3.10 ou une version plus récente**. Vérifier la
version utilisée avant de créer l'environnement :

```bash
python3.10 --version
```

### Version desktop

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-desktop.txt
python desktop.py
```

L'interface graphique appelle directement la logique Python et SQLite. Elle ne
lance ni navigateur, ni pywebview, ni moteur JavaScript.

### API Python optionnelle

L'API JSON peut être lancée séparément pour le développement ou une intégration
externe :

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Elle n'est pas nécessaire au fonctionnement de l'application desktop.

## Construire le paquet `.deb`

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-desktop.txt
bash packaging/build-deb.sh
```

Le paquet est écrit dans `dist/`.

La CI construit avec Python 3.10 dans un conteneur Debian 11 (glibc 2.31).
Cette base vise Ubuntu 20.04 et les versions plus récentes sur architecture
x86-64. Le workflow exécute les tests avant de produire et téléverser le paquet.

## Score

Une victoire démarre sur une base de 1000 points.

- chaque tentative ratée avant la victoire retire 100 points ;
- chaque seconde retire 1 point ;
- une victoire rapporte au minimum 100 points ;
- une partie abandonnée rapporte 0 point.

## Architecture

```text
Mastermind/
├── app/
│   ├── game.py             # règles Mastermind et calcul du score
│   ├── main.py             # logique applicative + API FastAPI optionnelle
│   ├── storage.py          # persistance SQLite utilisateur
│   └── types.py            # structures de données strictement typées
├── static/
│   └── mastermind.svg      # logo / icône fourni
├── packaging/
│   ├── build-deb.sh        # construction du paquet Ubuntu
│   └── mastermind.desktop  # entrée du menu Applications
├── desktop.py              # interface graphique PyQt6 native en Python
├── mastermind.spec         # configuration PyInstaller
├── pyproject.toml          # configuration mypy stricte
├── requirements-dev.txt    # dépendances des tests et du typage
├── requirements-desktop.txt
└── tests/
```

## API principale

| Méthode | Route                       | Fonction                               |
| ------- | --------------------------- | -------------------------------------- |
| `GET`   | `/api/modes`              | règles, modes et choix disponibles    |
| `GET`   | `/api/games/current`      | partie active à reprendre             |
| `POST`  | `/api/games`              | démarrer une partie / changer de mode |
| `POST`  | `/api/games/{id}/guesses` | proposer une combinaison              |
| `POST`  | `/api/games/{id}/give-up` | abandonner la partie                  |
| `GET`   | `/api/history`            | historique des parties                |
| `GET`   | `/api/stats`              | statistiques et score total           |

Le code secret n'est jamais renvoyé par l'API pendant une partie active. Il devient visible uniquement quand la partie est terminée.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m mypy
python -m pytest -q
```

Toutes les fonctions Python possèdent une docstring et des annotations de type.
La CI exécute le contrôle statique strict avec `mypy` avant les **42 tests
automatisés**, dont les tests de l'interface PyQt6 en mode hors écran.

## Langages

Le code applicatif est entièrement en Python. Le seul autre langage détecté par
GitHub est Shell, utilisé exclusivement par `packaging/build-deb.sh` pour créer
le paquet Debian.
