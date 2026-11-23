# TP1 : Docker

[Sujet](tp_docker.pdf). Manipuler des conteneurs, servir une page avec Nginx, puis déployer Flask seul et avec MongoDB.

## 3. Manipulation des conteneurs

Docker Engine 29.8.1 était installé lors de la réalisation du TP. [Instructions d'installation](https://docs.docker.com/engine/install/ubuntu/).

```bash
docker --version
docker images
docker pull hello-world
docker run --name tp1-hello hello-world  # affiche « Hello from Docker! » puis s'arrête
docker ps
docker ps -a                            # le conteneur apparaît avec le statut Exited (0)
docker rm tp1-hello
docker rmi hello-world
```

## 4. Serveur web Nginx

```bash
docker pull nginx
docker run -d -p 8080:80 --name mon_nginx nginx
docker ps
curl http://localhost:8080/             # page « Welcome to nginx! »
docker stop mon_nginx
docker rm mon_nginx
```

Le port 80 du conteneur est publié sur le port 8080 de la machine.

## 5. Application Flask

Fichiers : [application](ex5/app.py), [dépendances](ex5/requirements.txt), [Dockerfile](ex5/Dockerfile).

L'image utilise `python:3.14-slim` et `flask==3.1.3`. Flask écoute sur `0.0.0.0:5000` pour être accessible depuis l'hôte.

Depuis la racine du dépôt :

```bash
cd tp1/ex5
docker build -t tp1-flask .
docker run -d -p 5000:5000 --name tp1_flask tp1-flask
curl http://localhost:5000/             # Hello, World!
docker stop tp1_flask
docker rm tp1_flask
```

L'arrêt libère le port 5000 pour l'exercice suivant.

## 6. Flask et MongoDB avec Compose

Fichiers : [application](ex6/app.py), [dépendances](ex6/requirements.txt), [Dockerfile](ex6/Dockerfile), [compose.yaml](ex6/compose.yaml).

Le service `web` rejoint `mongo:8.2` par son nom réseau. L'URI passe par `MONGO_URI`, le démarrage attend que MongoDB soit sain et un volume conserve les données.

Depuis la racine du dépôt :

```bash
cd tp1/ex6
docker compose up -d --build
docker compose ps
curl http://localhost:5000/health
# {"mongo":"connected","status":"ok"}
curl http://localhost:5000/visits
# {"visits":1}
curl http://localhost:5000/visits
# {"visits":2}
docker compose down
```

Ces résultats ont été vérifiés avec un volume neuf. Le compteur reprend sa valeur si le volume existe déjà ; `down` le conserve.

## Exécution sans Docker (facultatif)

```bash
cd tp1
uv sync
uv run python ex5/app.py
```
