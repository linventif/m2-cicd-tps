# M2 CI/CD : rendus des TP

Grégoire Bécue — Université Toulouse Capitole.

| TP | Travail réalisé | Sujet | Compte rendu |
| --- | --- | --- | --- |
| **TP1 — Docker** | Conteneurs, Nginx, application Flask et base MongoDB avec Compose | [PDF](tp1/tp_docker.pdf) | [tp1/README.md](tp1/README.md) |
| **TP2 — Optimisation Docker** | Analyse et optimisation progressive d'une application Node.js et de son image | [PDF](tp2/tp_optimisation_docker.pdf) | [tp2/README.md](tp2/README.md) |
| **TP3 — GitLab CI/CD** | GitFlow, contrôles automatisés, tests, Docker Hub et génération de documentation | [PDF](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/blob/v1.1.1/tp_gitlab.pdf) | [REPORT.md sur GitLab](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/blob/main/REPORT.md) |

Les comptes rendus regroupent les commandes, les explications et les résultats. Le code et les fichiers Docker se trouvent dans chaque dossier.

## Résultats vérifiés

- **TP1** : les images Flask se construisent ; la stack Compose démarre, se connecte à MongoDB et enregistre les visites.
- **TP2** : dix étapes d'optimisation documentées. Lors de la campagne de mesure, l'image passe de **1 884 à 219 Mo** sur disque (−88 %) et le rebuild de **14,5 à 0,9 s**. Le compte rendu précise la méthode et les limites des mesures.
- **TP3** : pipeline réussi, **51 tests** et **95,6 % de couverture sur le modèle et la console** ; l'interface graphique est exclue de ce calcul. Image Docker publiée en version `1.1.1`.

## Projet GitLab du TP3

Le TP3 utilise un [dépôt GitLab public](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire), inclus ici comme sous-module `tp3`.

- [Rapport du TP](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/blob/main/REPORT.md) : configuration GitLab, GitFlow et détail du pipeline.
- [Pipelines](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/pipelines) et [merge requests](https://gitlab.com/Linventif/tp-gitlab-launaybecue-gregoire/-/merge_requests?scope=all&state=all).
- [Documentation de l'API sur GitLab Pages](https://linventif.gitlab.io/tp-gitlab-launaybecue-gregoire/).
- [Image Docker Hub](https://hub.docker.com/r/linventif/tp-gitlab-launaybecue-gregoire).

```bash
docker run --rm -it linventif/tp-gitlab-launaybecue-gregoire:1.1.1
```

## Récupérer et lancer les rendus

```bash
git clone --recurse-submodules https://github.com/linventif/m2-cicd-tps.git
cd m2-cicd-tps
# Pour un clone existant :
git submodule sync --recursive
git submodule update --init --recursive
```

Docker Engine avec Compose est nécessaire pour les exercices conteneurisés. Les commandes propres à chaque TP sont dans son compte rendu ; `uv` est facultatif pour lancer le TP1 hors Docker.

Les TPs Kubernetes sont conservés dans le sous-module `tpk8s` et disposent de leur [documentation](https://github.com/linventif/m2-cicd-tps-k8s). Ils ne font pas partie de ces trois rendus.

## Conventions

Branches `<type>/<description>` et commits `<type>(<tp>): <description>` en anglais, avec un commit par étape. Les changements passent par une PR vers `main`, fusionnée avec un commit de merge ; la branche est ensuite supprimée. Le TP3 suit GitFlow dans son dépôt GitLab.

[Licence MIT](LICENSE)
