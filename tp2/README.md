# TP 2 - CICD - Optimisation Docker

Sujet : [tp_optimisation_docker.pdf](tp_optimisation_docker.pdf)

Le sujet fournit une petite appli Node.js (Express) avec son Dockerfile, que l'on optimise étape par étape dans [`ex3/`](ex3/). Les fichiers ont été importés tels quels au commit `feat(tp2): add provided node.js app and dockerfile`.

## Méthode de mesure

Toutes les mesures viennent de [`bench.sh`](bench.sh), lancé après chaque étape :

```bash
cd tp2
./bench.sh <étape>
```

| Mesure | Comment |
| --- | --- |
| Taille, couches | `docker image inspect` (taille décompressée sur disque) |
| Build à froid | `docker build --no-cache`, avec les images de base déjà téléchargées |
| Rebuild | rebuild après une modification de `server.js` : montre si le cache est bien utilisé |
| Démarrage | du `docker run` à la première réponse HTTP 200 |
| RAM | `docker stats` au repos |
| Débit, latence | `autocannon` sur `/`, avec 50 connexions pendant 10 s |
| Arrêt | durée de `docker stop` |

Machine : 16 cœurs, 29 Go de RAM, Docker 29.8.1, Linux 7.0. Les temps de build dépendent du réseau (`apt-get`, `npm`) : sur deux mesures de départ, le build à froid a pris 12,4 s puis 38,0 s. On compare donc surtout les ordres de grandeur.

## Analyse de départ

Dockerfile fourni :

```dockerfile
FROM node:latest
WORKDIR /app
COPY node_modules ./node_modules
COPY . /app
RUN npm install
RUN apt-get update && apt-get install -y build-essential ca-certificates locales && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
EXPOSE 3000 4000 5000
ENV NODE_ENV=development
RUN npm run build
USER root
CMD ["node", "server.js"]
```

Problèmes relevés :

| # | Problème | Conséquence |
| --- | --- | --- |
| 1 | `FROM node:latest` | image Debian complète (1,8 Go) et version non figée |
| 2 | `COPY node_modules` depuis la machine, sans `.dockerignore` | modules compilés pour l'hôte, envoyés dans le contexte puis copiés dans l'image |
| 3 | `COPY . /app` avant `npm install` | toute modification du code invalide le cache : les dépendances et `apt-get` sont réinstallés |
| 4 | `npm install` au lieu de `npm ci --omit=dev` | installe aussi les devDependencies (`nodemon`) et ne respecte pas strictement le lockfile |
| 5 | `apt-get install build-essential locales…` | inutile (aucun module natif), et les listes apt ne sont pas nettoyées : +50 Mo |
| 6 | `RUN npm run build` | le script `build` ne fait qu'un `echo` |
| 7 | `EXPOSE 3000 4000 5000` | seul le port 3000 est utilisé |
| 8 | `ENV NODE_ENV=development` | Express tourne en mode développement |
| 9 | `USER root` | le conteneur tourne en root |
| 10 | dépendance `mongodb` | jamais utilisée dans le code |
| 11 | middleware de log sur chaque requête | un `console.log` par requête, ce qui ralentit le serveur |
| 12 | `existsSync` + `readFileSync` dans `/big` | lectures synchrones qui bloquent l'event loop |
| 13 | aucune gestion de `SIGTERM` | `node` tourne en PID 1 et ignore le signal : `docker stop` attend 10 s puis tue le process |

Taille des couches (`docker history`) : `apt-get` 50,1 Mo, `COPY node_modules` 14,2 Mo, `npm install` 7,7 Mo, le reste vient de l'image de base.

## Étapes

### 1. `.dockerignore` et suppression de `COPY node_modules`

Le `node_modules` de la machine n'est plus envoyé ni copié dans l'image. Les dépendances sont installées uniquement dans le conteneur.

- Contexte de build : 13,9 Mo → 60 Ko.
- L'image grossit de 6 Mo : `npm install` part maintenant de zéro et laisse son cache dans `/root/.npm` (7,1 Mo). Ce sera corrigé à l'étape 3.

### 2. Suppression des paquets apt, du faux build et des ports inutiles

On retire `apt-get install build-essential ca-certificates locales` (aucun module natif à compiler), `RUN npm run build` (qui ne fait qu'un `echo`) et les ports 4000 et 5000.

- Taille : 1890 → 1815 Mo (−75 Mo).
- Build à froid : 14,0 → 3,4 s, car il n'y a plus d'`apt-get update`.

### 3. Dépendances : cache, `npm ci --omit=dev`, `NODE_ENV=production`

```dockerfile
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server.js ./
```

- Les fichiers `package*.json` sont copiés **avant** le code. Quand seul `server.js` change, la couche des dépendances reste en cache : le rebuild passe de 3,5 à 0,8 s.
- `npm ci` installe exactement les versions du lockfile, et `--omit=dev` laisse `nodemon` de côté : `node_modules` passe de 16 à 14 Mo.
- `npm cache clean` : le cache npm passe de 7,1 Mo à 56 Ko.
- Taille : 1815 → 1802 Mo.

### 4. Image de base `node:26.13.0-alpine`

`node:latest` est une image Debian complète, qui embarque compilateurs, outils et bibliothèques, et dont la version change à chaque release. `node:26.13.0-alpine` contient la même version de Node.js sur Alpine Linux, et la version est figée.

- Taille : 1802 → 271 Mo (−85 %), c'est le plus gros gain du TP.
- Couches : 11 → 7.

## Mesures

| Étape | Taille | Couches | Build à froid | Rebuild (code modifié) | Démarrage | RAM | Débit | Latence moy. | Arrêt | Utilisateur |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0. Départ | 1884 MB | 13 | 12,4 s | 14,5 s | 0,3 s | 19,9 MiB | 25 037 req/s | 1,48 ms | 10,3 s | root |
| 1. `.dockerignore` | 1890 MB | 12 | 14,0 s | 12,1 s | 0,3 s | 19,8 MiB | 27 027 req/s | 1,30 ms | 10,3 s | root |
| 2. Sans apt ni faux build | 1815 MB | 10 | 3,4 s | 3,5 s | 0,3 s | 19,7 MiB | 27 016 req/s | 1,33 ms | 10,3 s | root |
| 3. Dépendances | 1802 MB | 11 | 3,0 s | 0,8 s | 0,5 s | 19,8 MiB | 26 630 req/s | 1,37 ms | 10,3 s | root |
| 4. Alpine | 271 MB | 7 | 4,0 s | 0,9 s | 0,5 s | 20,0 MiB | 25 532 req/s | 1,42 ms | 10,3 s | root |
