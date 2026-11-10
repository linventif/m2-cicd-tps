#!/usr/bin/env bash
# Charge /big (fichier de 5 Mo monté dans le conteneur) en parallèle de / pendant 10 s.
# Montre si /big bloque l'event loop : débit de /big, latence de /, RAM sous charge.
#
# Usage : ./bench-big.sh <image>
# Prérequis : docker, curl, jq, python3, Node.js (autocannon est lancé via npx)
set -euo pipefail

IMG=${1:?usage: bench-big.sh <image>}
NAME="tp2-bench-big"
PORT=${PORT:-3001}
AUTOCANNON=${AUTOCANNON:-"npx -y autocannon@8"}

tmp=$(mktemp -d)
python3 -c "
line = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n'
open('$tmp/big.txt', 'w').write(line * (5_000_000 // len(line)))"
chmod 644 "$tmp/big.txt"

docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" -p "$PORT:3000" -v "$tmp/big.txt:/app/maybe-big-file.txt:ro" "$IMG" >/dev/null
for _ in $(seq 1 100); do
	curl -sf -o /dev/null "http://localhost:$PORT/" && break
	sleep 0.05
done

$AUTOCANNON -c 10 -d 10 -j "http://localhost:$PORT/big" >"$tmp/big.json" 2>/dev/null &
$AUTOCANNON -c 10 -d 10 -j "http://localhost:$PORT/" >"$tmp/root.json" 2>/dev/null &
sleep 5
mem=$(docker stats --no-stream --format '{{.MemUsage}}' "$NAME" | cut -d/ -f1 | tr -d ' ')
wait
docker rm -f "$NAME" >/dev/null

echo "/big : $(jq '.requests.average' "$tmp/big.json") req/s, latence moy. $(jq '.latency.average' "$tmp/big.json") ms"
echo "/    : $(jq '.requests.average' "$tmp/root.json") req/s, latence moy. $(jq '.latency.average' "$tmp/root.json") ms, p99 $(jq '.latency.p99' "$tmp/root.json") ms"
echo "RAM sous charge : $mem"
rm -rf "$tmp"
