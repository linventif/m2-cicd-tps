# M2 CI/CD : TPs

Rendus des TPs du cours CI/CD (Université Toulouse Capitole).

| TP | Sujet | Branche | Rendu |
| --- | --- | --- | --- |
| TP1 | Docker : conteneurs, Dockerfile, docker compose | `feat/tp1-docker` | [tp1/README.md](tp1/README.md) |
| TP2 | Optimisation d'une image Docker (appli Node.js) | `feat/tp2-docker-optimisation` | [tp2/README.md](tp2/README.md) |
| TP3 | GitLab : GitFlow, pipeline CI/CD, Docker Hub, GitLab Pages | dépôt GitLab dédié, sous-module `tp3` | [section TP3](#tp3--projet-gitlab), [REPORT.md](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/blob/main/REPORT.md) |
| Kubernetes | Pods, Deployments, Services, namespaces et ConfigMaps | dépôt GitHub dédié, sous-module `tpk8s` | [tpk8s/README.md](tpk8s/README.md), [TP2 Kubernetes](tpk8s/tp2/README.md) |

## Structure du dépôt

```text
.
├── README.md                # organisation et conventions du dépôt
├── .gitignore
├── LICENSE
└── tpN/                     # un dossier par TP
    ├── README.md            # tâches réalisées, commandes, résultats
    ├── <sujet>.pdf          # sujet du TP
    ├── pyproject.toml       # environnement Python du TP, si le TP est en Python (uv)
    ├── uv.lock
    └── exN/                 # un dossier par exercice
```

## TP3 : projet GitLab

Le TP3 impose un dépôt GitLab public avec son propre pipeline. Il vit dans [son dépôt](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire) et apparaît ici comme le sous-module `tp3`, fixé sur la version `v1.1.1`. Pour tout récupérer d'un coup :

```bash
git clone --recurse-submodules git@github.com:linventif/m2-cicd-tps.git
# dans un clone existant :
git submodule update --init
```

| Documentation | Lien |
| --- | --- |
| Rapport : mise en place GitLab, GitFlow, pipeline, Docker | [REPORT.md](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/blob/main/REPORT.md) |
| Documentation de l'API (pdoc, GitLab Pages) | <https://linventif.gitlab.io/tp-gitlab-launaybecue-gregoire/> |
| Image Docker (version console) | [linventif/tp-gitlab-launaybecue-gregoire](https://hub.docker.com/r/linventif/tp-gitlab-launaybecue-gregoire) : `docker run -it linventif/tp-gitlab-launaybecue-gregoire` |
| Historique des versions | [CHANGELOG.md](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/blob/main/CHANGELOG.md) |
| Pipelines CI/CD | [pipelines](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/pipelines) |
| Merge requests (une par feature, GitFlow) | [merge requests](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/merge_requests?scope=all&state=all) |

Le pipeline enchaîne build → lint (pylint) → security (bandit, gitleaks, pip-audit) → quality (pytest, couverture) → docker (build, test, publication Docker Hub) → deploy (documentation sur GitLab Pages). Une merge request n'est fusionnée que si tout le pipeline passe.

Sur le projet fourni, le pipeline a fait passer pylint de 6,08 à 10/10 et les tests de 36 à 51, avec 96 % de couverture. Il a surtout révélé deux vrais bugs : la version console plantait, et l'interface graphique ne se lançait jamais.

## TPs Kubernetes

Les sujets et les manifests Kubernetes sont regroupés dans [un dépôt dédié](https://github.com/linventif/m2-cicd-tps-k8s), intégré ici comme sous-module `tpk8s`. Les manifests du TP1 et les premières étapes du TP2 (namespaces et ConfigMaps) sont versionnés. Les exercices Secrets et DNS du TP2 restent à réaliser.

Le [README Kubernetes](tpk8s/README.md) présente les sujets et leur état ; le [README du TP2](tpk8s/tp2/README.md) décrit les commandes et les validations réalisées. Les manifests ont été analysés localement ; leur déploiement sur cluster reste à vérifier.

```bash
git submodule update --init --recursive
```

## Prérequis

- [Docker Engine](https://docs.docker.com/engine/install/) avec le plugin Docker Compose v2 (`docker compose`)
- [uv](https://docs.astral.sh/uv/) pour Python (installe Python 3.14 si besoin)

## Environnement Python

Chaque TP en Python (TP1) a son propre environnement, géré avec uv : un `pyproject.toml` pour les dépendances, un `uv.lock` pour les versions exactes, et un `.venv/` local qui n'est pas versionné.

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
