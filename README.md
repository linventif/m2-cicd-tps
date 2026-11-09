# M2 CI/CD : TPs

Rendus des TPs du cours CI/CD (Université Toulouse Capitole).

| TP | Sujet | Branche | Rendu |
| --- | --- | --- | --- |
| TP1 | Docker : conteneurs, Dockerfile, docker compose | `feat/tp1-docker` | [tp1/README.md](tp1/README.md) |
| TP2 | Optimisation d'une image Docker (appli Node.js) | `feat/tp2-docker-optimisation` | [tp2/README.md](tp2/README.md) |

## Structure du dépôt

```text
.
├── README.md                # organisation et conventions du dépôt
├── .gitignore
├── LICENSE
└── tpN/                     # un dossier par TP
    ├── README.md            # tâches réalisées, commandes, résultats
    ├── <sujet>.pdf          # sujet du TP
    ├── pyproject.toml       # environnement Python du TP (uv)
    ├── uv.lock
    └── exN/                 # un dossier par exercice
```

## Prérequis

- [Docker Engine](https://docs.docker.com/engine/install/) avec le plugin Docker Compose v2 (`docker compose`)
- [uv](https://docs.astral.sh/uv/) pour Python (installe Python 3.14 si besoin)

## Environnement Python

Chaque TP a son propre environnement Python, géré avec uv : un `pyproject.toml` pour les dépendances, un `uv.lock` pour les versions exactes, et un `.venv/` local qui n'est pas versionné.

```bash
cd tpN
uv sync                      # crée le .venv à partir du uv.lock
uv run python <script>.py    # lance un script dans le venv
# ou : source .venv/bin/activate

uv add <paquet>              # ajoute une dépendance (met à jour pyproject.toml et uv.lock)
```

Pour un nouveau TP :

```bash
cd tpN
uv init --bare --name tpN --python 3.14
uv add <paquets>
```

## Conventions

### Organisation

- Un dossier par TP (`tpN/`), qui contient le sujet (PDF), un `README.md` et un sous-dossier par exercice (`exN/`).
- Le `README.md` d'un TP liste les tâches réalisées dans l'ordre du sujet, avec les commandes lancées et leurs résultats réels.
- Chaque exercice dockerisé est autonome : `Dockerfile`, `requirements.txt` et `compose.yaml` sont dans le dossier de l'exercice, qui sert de contexte de build.

### Branches

Les noms de branches suivent [Conventional Branch](https://conventional-branch.github.io/) :

```text
<type>/<description>
```

- **`main`** : ne reçoit que des PR fusionnées. On ne commite pas directement dessus, sauf pour l'initialisation du dépôt (README, `.gitignore`).
- **Une branche par TP**, créée depuis `main` à jour : `feat/tp1-docker`, `feat/tp2-docker-optimisation`.
- **type** : le même vocabulaire que les commits (`feat/`, `fix/`, `docs/`, `chore/`…).
- **description** : en minuscules, mots séparés par des tirets, commence par le TP concerné (`tp1-…`).

### Commits

Les messages suivent [Conventional Commits](https://www.conventionalcommits.org/fr/v1.0.0/) :

```text
<type>(<scope>): <description>
```

- **Un commit par étape** : chaque commit fait une seule chose (le code d'une étape, puis sa documentation).
- **scope** : le TP concerné (`tp1`, `tp2`). On l'omet quand le commit touche tout le dépôt.
- **description** : en anglais, à l'impératif, en minuscules, sans point final.
- **corps** (optionnel) : explique le *pourquoi* quand ce n'est pas évident.

| Type | Usage | Exemple |
| --- | --- | --- |
| `feat` | nouvelle fonctionnalité | `feat(tp1): add flask app with mongodb connection` |
| `fix` | correction de bug | `fix(tp1): bind flask to 0.0.0.0` |
| `docs` | documentation, README, sujets | `docs(tp1): document docker compose deployment` |
| `build` | Dockerfile, compose, dépendances, environnement | `build(tp1): containerize flask app with dockerfile` |
| `perf` | optimisation (taille d'image, temps de build…) | `perf(tp2): use multi-stage build` |
| `refactor` | restructuration sans changement de comportement | `refactor(tp2): split server routes` |
| `ci` | pipelines CI/CD | `ci: add github actions workflow` |
| `test` | tests | `test(tp1): add health route test` |
| `chore` | maintenance (gitignore, outillage…) | `chore: add gitignore` |

### Pull requests

- **Une PR par TP**, de la branche du TP vers `main`.
- **Titre** au format Conventional Commits, par exemple `feat(tp1): docker basics, flask and docker compose`.
- **Description** :
  - l'objectif du TP ;
  - la liste des tâches réalisées ;
  - comment tester (commandes) ;
  - un lien vers le `README.md` du TP.
- **Avant de fusionner** :
  - le `README.md` du TP est à jour, avec les commandes et les résultats ;
  - les images se construisent et les conteneurs démarrent ;
  - aucun fichier généré ou secret n'est commité (`.venv/`, `.env`…).
- **Fusion** avec *Create a merge commit*. On ne fait pas de *squash*, pour garder un commit par étape, et le commit de merge marque la fin du TP dans l'historique.
- La branche est supprimée après la fusion.

Déroulé pour un TP :

```bash
git switch main && git pull
git switch -c feat/tpN-<sujet>
# ... un commit par étape ...
git push -u origin feat/tpN-<sujet>
# puis ouvrir la PR vers main sur GitHub
```

### Docker

- Les versions sont épinglées : dépendances dans `requirements.txt` (`flask==3.1.3`) et tags d'images précis (`mongo:8.2`, `python:3.14-slim`), jamais `latest`.
- Les dépendances sont copiées et installées **avant** le code, pour profiter du cache des couches.
- Les images de base sont `-slim` quand c'est possible.
- Les images sont nommées `tpN-<app>` (ex. `tp1-flask`).
- La configuration (URI de base de données…) passe par des variables d'environnement, pas en dur dans le code.

### Fichiers ignorés

Le [`.gitignore`](.gitignore) exclut :

- Python : `.venv/`, `__pycache__/`, `*.pyc`, caches pytest / mypy / ruff
- Node.js (TP2) : `node_modules/`, logs npm / yarn
- Secrets : `.env`, `.env.*` (sauf `.env.example`)
- IDE / OS : `.vscode/`, `.idea/`, `.DS_Store`…

## Licence

[MIT](LICENSE)
