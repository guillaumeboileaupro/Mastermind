# Mastermind

Jeu Mastermind avec **application desktop Ubuntu**, backend FastAPI et persistance SQLite.

## Modes de jeu

Deux modes utilisent la même logique Mastermind :

- **Couleurs** : rouge, bleu, vert, jaune, violet, orange.
- **Chiffres** : 1, 2, 3, 4, 5, 6.

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

Le workflow **Build Ubuntu package** construit un paquet `mastermind_0.1.0_amd64.deb`.

Après téléchargement du `.deb` :

```bash
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

### Version web

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Puis ouvrir `http://127.0.0.1:8000`.

### Version desktop

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-desktop.txt
python desktop.py
```

## Construire le paquet `.deb`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-desktop.txt
bash packaging/build-deb.sh
```

Le paquet est écrit dans `dist/`.

La CI construit avec Python 3.10 dans un conteneur Debian 11 (glibc 2.31). Cette base permet de viser Ubuntu 20.04 et les versions plus récentes sur architecture x86-64 tout en satisfaisant les versions Python requises par Uvicorn et pytest.

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
│   ├── main.py             # API FastAPI + vue locale
│   └── storage.py          # persistance SQLite utilisateur
├── static/
│   ├── mastermind.svg      # logo / icône fourni
│   ├── app.js
│   ├── index.html
│   └── style.css
├── packaging/
│   ├── build-deb.sh        # construction du paquet Ubuntu
│   └── mastermind.desktop  # entrée du menu Applications
├── desktop.py              # fenêtre desktop pywebview + serveur local
├── mastermind.spec         # configuration PyInstaller
├── requirements-desktop.txt
└── tests/
```

## API principale

| Méthode | Route | Fonction |
|---|---|---|
| `GET` | `/api/modes` | règles, modes et choix disponibles |
| `GET` | `/api/games/current` | partie active à reprendre |
| `POST` | `/api/games` | démarrer une partie / changer de mode |
| `POST` | `/api/games/{id}/guesses` | proposer une combinaison |
| `POST` | `/api/games/{id}/give-up` | abandonner la partie |
| `GET` | `/api/history` | historique des parties |
| `GET` | `/api/stats` | statistiques et score total |

Le code secret n'est jamais renvoyé par l'API pendant une partie active. Il devient visible uniquement quand la partie est terminée.

## Tests

```bash
pytest -q
```
