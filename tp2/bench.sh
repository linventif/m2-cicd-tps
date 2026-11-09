#!/usr/bin/env bash
# Mesure l'image de l'appli TP2 : build à froid, rebuild après modification du code,
# taille, couches, utilisateur, démarrage, RAM, débit HTTP et temps d'arrêt.
#
# Usage : ./bench.sh <tag> [contexte]        (contexte par défaut : ex3/)
# Prérequis : docker, curl, jq, Node.js (autocannon est lancé via npx)
set -euo pipefail

TAG=${1:?usage: bench.sh <tag> [contexte]}
CTX=${2:-"$(dirname "$0")/ex3"}
IMG="tp2-app:$TAG"
NAME="tp2-bench"
PORT=${PORT:-3000}
AUTOCANNON=${AUTOCANNON:-"npx -y autocannon@8"}

now() { date +%s.%N; }
since() { awk -v a="$1" -v b="$(now)" 'BEGIN { printf "%.1f", b - a }'; }

# 1. Build à froid (sans cache, images de base déjà téléchargées)
t=$(now)
docker build -q --no-cache -t "$IMG" "$CTX" >/dev/null
build_cold=$(since "$t")

# 2. Rebuild après modification de server.js (le cache du build précédent est réutilisable)
tmp=$(mktemp -d)
cp -a "$CTX/." "$tmp/"
echo "// bench $(date +%s%N)" >>"$tmp/server.js"
t=$(now)
docker build -q -t "$IMG-rebuild" "$tmp" >/dev/null
build_warm=$(since "$t")
docker rmi -f "$IMG-rebuild" >/dev/null
rm -rf "$tmp"

# 3. Image
size_mb=$(docker image inspect -f '{{.Size}}' "$IMG" | awk '{ printf "%.0f", $1 / 1000000 }')
compressed=$(docker images "$IMG" | awk 'NR == 2 { print $4 }') # CONTENT SIZE : ce qui est téléchargé au pull
layers=$(docker image inspect -f '{{len .RootFS.Layers}}' "$IMG")
user=$(docker image inspect -f '{{.Config.User}}' "$IMG")
user=${user:-root}

# 4. Démarrage : du docker run à la première réponse HTTP 200
docker rm -f "$NAME" >/dev/null 2>&1 || true
t=$(now)
docker run -d --name "$NAME" -p "$PORT:3000" "$IMG" >/dev/null
for _ in $(seq 1 300); do
	curl -sf -o /dev/null "http://localhost:$PORT/" && break
	sleep 0.05
done
startup=$(since "$t")

# 5. RAM au repos
sleep 2
mem=$(docker stats --no-stream --format '{{.MemUsage}}' "$NAME" | cut -d/ -f1 | tr -d ' ')

# 6. Débit sur / : 50 connexions pendant 10 s (après 3 s de chauffe)
$AUTOCANNON -c 50 -d 3 "http://localhost:$PORT/" >/dev/null 2>&1
res=$($AUTOCANNON -c 50 -d 10 -j "http://localhost:$PORT/" 2>/dev/null)
rps=$(jq '.requests.average | floor' <<<"$res")
lat=$(jq '.latency.average' <<<"$res")

# 7. Arrêt : docker stop attend 10 s avant SIGKILL si le process ignore SIGTERM
t=$(now)
docker stop "$NAME" >/dev/null
stop=$(since "$t")
docker rm "$NAME" >/dev/null

echo "| Étape | Disque | Compressée | Couches | Build à froid | Rebuild (code modifié) | Démarrage | RAM | Débit | Latence moy. | Arrêt | Utilisateur |"
echo "| $TAG | $size_mb MB | $compressed | $layers | $build_cold s | $build_warm s | $startup s | $mem | $rps req/s | $lat ms | $stop s | $user |"
