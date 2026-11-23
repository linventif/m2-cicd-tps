# TP2 : optimisation Docker

[Sujet](tp_optimisation_docker.pdf). L'application Node.js fournie est optimisée par étapes dans [`ex3/`](ex3/), avec un commit de code puis de documentation par étape.

## Analyse et améliorations

Au départ : image Debian complète avec tag `latest`, modules copiés depuis l'hôte, cache invalidé par le code, dépendances et paquets système inutiles, exécution en root. L'application journalise chaque requête, lit `/big` de manière synchrone et ne traite pas `SIGTERM`.

| Étape | Modification | Intérêt |
| --- | --- | --- |
| 1 | Ajouter `.dockerignore`, retirer `COPY node_modules` | Installer les modules dans l'image et réduire le contexte de 13,9 Mo à 60 Ko |
| 2 | Retirer les paquets apt, le faux build et les ports inutilisés | Éviter les installations et couches inutiles |
| 3 | Copier les manifests avant le code, utiliser `npm ci --omit=dev` et `NODE_ENV=production` | Réutiliser le cache et exclure les dépendances de développement |
| 4 | Utiliser `node:26.13.0-alpine` | Réduire fortement l'image et fixer la version de Node.js |
| 5 | Exécuter avec `USER node` | Éviter les privilèges root |
| 6 | Supprimer la dépendance `mongodb` inutilisée | Réduire les modules installés |
| 7 | Retirer le log par requête | Réduire le coût des écritures dans stdout |
| 8 | Lire et transformer `/big` en streaming | Éviter le blocage de l'event loop et le chargement intégral en mémoire |
| 9 | Gérer `SIGTERM` et `SIGINT` | Terminer les requêtes en cours, puis sortir proprement |
| 10 | Construire en multi-stage | Ne conserver que Node.js, les bibliothèques nécessaires, les modules et l'application |

Le [Dockerfile final](ex3/Dockerfile) installe les dépendances dans un premier stage Node.js. L'image d'exécution utilise `alpine:3.24.4`, alignée sur l'Alpine de l'image Node.js ; npm et les en-têtes de développement n'y sont plus présents. Ce choix réduit la taille mais demande de garder les deux bases compatibles.

## Méthode de mesure

Les mesures datent du **9 novembre 2026** (commit `7aedd6b`), avant les mises à jour de dépendances. Les tailles ont été vérifiées sur les onze images conservées.

Scripts : [`bench.sh`](bench.sh) pour l'image et `/`, [`bench-big.sh`](bench-big.sh) pour la charge simultanée de `/big` et `/`. Prérequis : Docker, curl, jq, Node.js/npm et Python 3 pour le second script.

```bash
cd tp2
./bench.sh verification                # construit et mesure ex3/
./bench-big.sh tp2-app:verification
```

La taille disque vient de `docker image inspect` et la taille compressée de `CONTENT SIZE` dans `docker images`. Le build à froid utilise `--no-cache`, avec les bases déjà téléchargées ; le rebuild modifie uniquement `server.js`.

Le démarrage est mesuré jusqu'au premier HTTP 200, la RAM au repos avec `docker stats`, et l'arrêt avec `docker stop`. Le débit et la latence sont mesurés sur `/` avec autocannon : 50 connexions pendant 10 s, après 3 s de chauffe.

Machine de mesure : 16 cœurs, 29 Go de RAM, Docker 29.8.1, Linux 7.0. Les builds dépendent du réseau et le débit varie d'environ ±10 % : les gains modestes doivent être interprétés avec cette marge.

## Mesures par étape

| Étape | Disque | Compressée | Couches | Build à froid | Rebuild (code modifié) | Démarrage | RAM | Débit | Latence moy. | Arrêt | Utilisateur |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0. Départ | 1884 MB | 474 MB | 13 | 12,4 s | 14,5 s | 0,3 s | 19,9 MiB | 25 037 req/s | 1,48 ms | 10,3 s | root |
| 1. `.dockerignore` | 1890 MB | 476 MB | 12 | 14,0 s | 12,1 s | 0,3 s | 19,8 MiB | 27 027 req/s | 1,30 ms | 10,3 s | root |
| 2. Sans apt ni faux build | 1815 MB | 451 MB | 10 | 3,4 s | 3,5 s | 0,3 s | 19,7 MiB | 27 016 req/s | 1,33 ms | 10,3 s | root |
| 3. Dépendances | 1802 MB | 448 MB | 11 | 3,0 s | 0,8 s | 0,5 s | 19,8 MiB | 26 630 req/s | 1,37 ms | 10,3 s | root |
| 4. Alpine | 271 MB | 65,7 MB | 7 | 4,0 s | 0,9 s | 0,5 s | 20,0 MiB | 25 532 req/s | 1,42 ms | 10,3 s | root |
| 5. Non-root | 271 MB | 65,7 MB | 7 | 3,1 s | 0,9 s | 0,5 s | 20,0 MiB | 25 305 req/s | 1,43 ms | 10,3 s | node |
| 6. Sans `mongodb` | 260 MB | 64,2 MB | 7 | 2,9 s | 0,8 s | 0,4 s | 20,3 MiB | 27 055 req/s | 1,30 ms | 10,3 s | node |
| 7. Sans log par requête | 260 MB | 64,2 MB | 7 | 3,4 s | 0,9 s | 0,4 s | 20,2 MiB | 32 429 req/s | 1,19 ms | 10,3 s | node |
| 8. `/big` en streaming | 260 MB | 64,2 MB | 7 | 3,0 s | 0,8 s | 0,4 s | 20,1 MiB | 35 125 req/s | 1,08 ms | 10,3 s | node |
| 9. Arrêt propre | 260 MB | 64,2 MB | 7 | 2,7 s | 0,8 s | 0,4 s | 20,0 MiB | 35 129 req/s | 1,09 ms | 0,2 s | node |
| 10. Multi-stage | 219 MB | 56,2 MB | 6 | 7,2 s | 0,9 s | 0,4 s | 20,2 MiB | 37 093 req/s | 1,07 ms | 0,2 s | node |

## Vérification de `/big`

Un fichier de 5 Mo est monté dans le conteneur ; `/big` et `/` sont chargés en parallèle pendant 10 s, avec 10 connexions chacun.

| Mesure | Avant : lecture synchrone | Après : streaming |
| --- | --- | --- |
| Débit sur `/big` | 58 req/s | 83 req/s |
| `/` pendant la charge | 69 req/s, 142 ms en moyenne | 5 923 req/s, 1,3 ms en moyenne |
| RAM sous charge | 179 Mio | 113 Mio |

Le contenu et la transformation des sauts de ligne en `<br/>` sont conservés, ainsi que le message `Fichier introuvable` si le fichier est absent.

## Bilan et lancement

L'image passe de **1 884 à 219 Mo sur disque** (−88 %), et de **474 à 56,2 Mo compressés**. Le rebuild passe de **14,5 à 0,9 s** et l'arrêt de **10,3 à 0,2 s**, avec un code de sortie 0. Le débit sur `/` passe de 25 037 à 37 093 req/s ; la suppression des logs apporte +20 % à elle seule, une partie du reste peut venir de la variabilité des mesures.

La version actuelle a également été vérifiée après les mises à jour de dépendances : installation npm, build Docker, routes `/` et `/big`, et arrêt sur `SIGTERM` réussis.

```bash
cd tp2/ex3
docker build -t tp2-app .
docker run -d -p 3000:3000 --name tp2-app tp2-app
curl http://localhost:3000/
docker stop tp2-app
docker rm tp2-app
```
