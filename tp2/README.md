# TP 2 - CICD - Optimisation Docker

Sujet : [tp_optimisation_docker.pdf](tp_optimisation_docker.pdf)

Le sujet fournit une petite appli Node.js (Express) avec son Dockerfile, que l'on optimise étape par étape dans [`ex3/`](ex3/). Les fichiers ont été importés tels quels au commit `feat(tp2): add provided node.js app and dockerfile`.

## Méthode de mesure

Les mesures du tableau viennent de [`bench.sh`](bench.sh), lancé après chaque étape. La route `/big` est mesurée à part avec [`bench-big.sh`](bench-big.sh) (voir l'étape 8). Il faut Docker, `jq` et Node.js (pour lancer `autocannon` via `npx`).

```bash
cd tp2
./bench.sh <étape>
```

| Mesure | Comment |
| --- | --- |
| Disque | espace occupé par l'image (`docker image inspect`). Avec le stockage containerd, cela inclut les couches décompressées et les blobs compressés |
| Compressée | colonne CONTENT SIZE de `docker images` : ce qu'un registry transfère à chaque `docker pull` |
| Couches | nombre de couches du système de fichiers |
| Build à froid | `docker build --no-cache`, avec les images de base déjà téléchargées |
| Rebuild | rebuild après une modification de `server.js` : montre si le cache est bien utilisé |
| Démarrage | du `docker run` à la première réponse HTTP 200 |
| RAM | `docker stats` au repos |
| Débit, latence | `autocannon` sur `/`, avec 50 connexions pendant 10 s |
| Arrêt | durée de `docker stop` |

Machine : 16 cœurs, 29 Go de RAM, Docker 29.8.1, Linux 7.0. Les temps de build dépendent du réseau (`apt-get`, `npm`) : sur deux mesures de départ, le build à froid a pris 12,4 s puis 38,0 s. Le débit varie d'environ ±10 % entre deux mesures identiques (25 037 puis 23 697 req/s au départ). On compare donc surtout les ordres de grandeur.

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

### 5. Utilisateur non-root

`USER root` devient `USER node`, l'utilisateur fourni par l'image officielle. Les fichiers de l'appli appartiennent toujours à root : le process peut les lire mais pas les modifier (`touch /app/server.js` → `Permission denied`). Les performances ne changent pas.

### 6. Suppression de la dépendance `mongodb`

`server.js` ne charge que `express`, `fs` et `path` : `mongodb` ne sert à rien. On la retire avec `npm uninstall mongodb --package-lock-only`.

- `node_modules` : 14 → 4,4 Mo (78 → 67 paquets).
- Taille : 271 → 260 Mo.

### 7. Suppression du middleware de log

Le middleware écrivait une ligne dans `stdout` à chaque requête. Docker capture ces logs, et à plus de 25 000 req/s cela coûte cher. Pour journaliser les requêtes en production, il vaut mieux un logger asynchrone (`pino`, par exemple) ou les logs du reverse proxy.

- Débit : 27 055 → 32 429 req/s (+20 %).
- Latence moyenne : 1,30 → 1,19 ms.

### 8. `/big` en streaming

`existsSync` puis `readFileSync` chargeaient tout le fichier en mémoire, et `replace` le transformait en une seule fois. Pendant ce temps, l'event loop était bloquée : le serveur ne répondait plus à aucune autre requête. Maintenant, le fichier est lu par morceaux et transformé au fil de l'eau :

```js
const file = fs.createReadStream(BIG_FILE, 'utf8');
// ...
pipeline(file, newlinesToBr, res, () => {});   // newlinesToBr : Transform qui remplace \n par <br/>
```

La réponse est identique à l'octet près, et le message `Fichier introuvable` est conservé.

`bench.sh` ne charge que `/`, et le fichier n'existe pas dans l'image. [`bench-big.sh`](bench-big.sh) monte donc un fichier de 5 Mo et charge `/big` et `/` en même temps pendant 10 s (10 connexions chacun) :

| | Avant (synchrone) | Après (streaming) |
| --- | --- | --- |
| `/big` | 58 req/s | 83 req/s |
| `/` pendant la charge | 69 req/s, latence 142 ms (p99 178 ms) | 5 923 req/s, latence 1,3 ms (p99 4 ms) |
| RAM sous charge | 179 Mio | 113 Mio |

### 9. Arrêt propre sur `SIGTERM`

Dans le conteneur, `node` est le PID 1 : sans handler, il ignore `SIGTERM`. `docker stop` attendait donc 10 s, puis tuait le process avec `SIGKILL` (code 137). Maintenant, le serveur termine les requêtes en cours puis s'arrête :

```js
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => {
    server.close(() => process.exit(0));
  });
}
```

- Arrêt : 10,3 → 0,2 s, avec un code de sortie 0. Cela accélère les redéploiements et les `docker compose down`.

### 10. Build multi-stage

Un premier stage installe les dépendances avec npm. L'image finale part d'une Alpine nue et ne reçoit que le binaire `node`, les bibliothèques dont il dépend (`libstdc++`, `libgcc`, `libatomic`), `node_modules` et `server.js`. npm (18 Mo), les en-têtes C (6,6 Mo) et le cache npm ne sont plus dans l'image. L'Alpine finale est dans la même version (3.24.4) que celle de `node:26.13.0-alpine`, ce qui garantit la même ABI musl.

- Taille sur disque : 260 → 219 Mo ; taille compressée : 64,2 → 56,2 Mo (−12 %) ; couches : 7 → 6.
- Comme npm n'est plus dans l'image, la surface d'attaque est plus petite.
- En contrepartie, le build à froid passe de 2,7 à 7,2 s (deux stages et un `apk add`), le rebuild reste à 0,9 s, et il faut garder la version d'Alpine alignée sur celle de l'image `node`.
- Testée aussi : `gcr.io/distroless/nodejs26-debian13` fait 243 Mo seule, donc pas mieux.

## Mesures

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

## Résultat

Dockerfile final ([`ex3/Dockerfile`](ex3/Dockerfile)) :

```dockerfile
# Stage 1 : installation des dépendances de production
FROM node:26.13.0-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Stage 2 : image d'exécution, Alpine + binaire node seul (sans npm ni en-têtes)
FROM alpine:3.24.4
RUN apk add --no-cache libstdc++ libgcc libatomic \
    && addgroup -g 1000 node \
    && adduser -u 1000 -G node -s /bin/sh -D node
COPY --from=deps /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY server.js ./
EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

| | Départ | Final | |
| --- | --- | --- | --- |
| Taille sur disque | 1884 Mo | 219 Mo | −88 % |
| Taille compressée (`docker pull`) | 474 Mo | 56,2 Mo | −88 % |
| Couches | 13 | 6 | |
| Contexte de build | 13,9 Mo | 60 Ko | |
| Rebuild après modification du code | 14,5 s | 0,9 s | ×16 plus rapide |
| Débit sur `/` | 25 037 req/s | 37 093 req/s | +48 % ¹ |
| `/` pendant une charge sur `/big` | 69 req/s | 5 900 à 8 200 req/s | plus de blocage |
| Arrêt (`docker stop`) | 10,3 s | 0,2 s | |
| Utilisateur | root | node | |

¹ Dont +20 % mesurés à l'étape 7 (suppression du log). Le reste est en partie du bruit de mesure (±10 %).

Ce qui a le plus pesé : l'image de base (−85 % à elle seule), l'ordre des couches pour le cache (rebuild ×16), et les corrections du code (débit, blocage de l'event loop, arrêt).

Lancer l'appli :

```bash
cd tp2/ex3
docker build -t tp2-app .
docker run -d -p 3000:3000 --name tp2-app tp2-app
curl http://localhost:3000/
```
