# Mastermind

Application web Mastermind avec backend FastAPI et persistance SQLite.

## Modes de jeu

Deux modes utilisent exactement la même logique Mastermind :

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

- sélection du mode de jeu ;
- génération d'un code secret ;
- affichage graphique des 6 couleurs ;
- validation des tentatives avec gestion correcte des doublons ;
- reprise d'une partie active après redémarrage du serveur ;
- chronomètre de la partie en cours ;
- score courant ;
- score final ;
- score total cumulé ;
- historique persistant des parties ;
- nombre de victoires ;
- abandon d'une partie ;
- changement de mode en démarrant une nouvelle partie.

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
│   ├── __init__.py
│   ├── game.py        # règles Mastermind et calcul du score
│   ├── main.py        # API FastAPI + serveur de la vue web
│   └── storage.py     # persistance SQLite
├── static/
│   ├── app.js         # interaction avec l'API
│   ├── index.html     # interface du jeu
│   └── style.css
├── tests/
│   └── test_game.py
├── .gitignore
├── requirements.txt
└── README.md
```

La base SQLite est créée automatiquement dans `data/mastermind.db` au premier démarrage. Elle n'est pas versionnée.

## Lancer le projet

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Puis ouvrir `http://127.0.0.1:8000`.

La documentation interactive FastAPI est disponible sur `http://127.0.0.1:8000/docs`.

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
