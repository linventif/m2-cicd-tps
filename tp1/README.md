# TP 1 - CICD - Docker
<!--
TP Docker
1. Instructions d'installation de Docker

Pour installer Docker sur votre machine :
1. Rendez-vous sur le site officiel : https://docs.docker.com/get-docker/
2. Choisissez votre système d’exploitation (Windows, macOS, Linux).
3. Téléchargez et installez Docker Desktop ou Docker Engine selon votre configuration.
4. Vérifiez l’installation avec la commande :
   docker --version

2. Objectif pédagogique

L’objectif de ce TP est de vous familiariser avec les concepts fondamentaux de Docker,
la création et la gestion de conteneurs, l’utilisation des images, ainsi que les
commandes essentielles pour manipuler l’écosystème Docker.

Rendu attendu :
Le dépôt git contenant :
• Un readme avec l’ensemble des tâches réalisés
• Les fichiers par TP organisé par dossier. Avec l’arborescence suivante :
o TP Docker
▪ Fichier TP
▪ Readme.md
3. Exercice : Manipulation de base des conteneurs

Étapes :
1. Vérifiez la version de Docker :
   docker --version
   → Affiche la version installée de Docker.

2. Listez les images disponibles sur votre machine :
   docker images
   → Montre toutes les images stockées localement.



 Harold Parpex 2
 Université Toulouse Capitole
3. Téléchargez une image depuis Docker Hub :
   docker pull hello-world
   → Télécharge l'image officielle "hello-world".

4. Exécutez un conteneur à partir de l'image :
   docker run hello-world
   → Lance un conteneur qui affiche un message de bienvenue.

5. Listez les conteneurs en cours d'exécution :
   docker ps
   → Montre les conteneurs actifs.

6. Listez tous les conteneurs (actifs et stoppés) :
   docker ps -a
   → Affiche tout l’historique des conteneurs.

7. Supprimez un conteneur :
   docker rm <ID_conteneur>

8. Supprimez une image :
   docker rmi <ID_image>

4. Exercice : Création d'un serveur web avec Docker

1. Téléchargez l'image officielle Nginx :
   docker pull nginx

2. Lancez un conteneur Nginx en arrière-plan :
   docker run -d -p 8080:80 --name mon_nginx nginx
   → Démarre un serveur web accessible sur http://localhost:8080.

3. Vérifiez que le conteneur est actif :
   docker ps

4. Accédez à la page dans votre navigateur pour voir la page par défaut de Nginx.

5. Arrêtez le conteneur :
   docker stop mon_nginx



 Harold Parpex 3
 Université Toulouse Capitole
6. Supprimez le conteneur :
   docker rm mon_nginx
5. Exercice : Déploiement d'une application Python Flask

Objectif : Créer et lancer une application web simple avec Flask à l’aide de Docker.

Consignes :
- Créez un fichier app.py contenant une application Flask minimale. (hello world)
- Écrivez un Dockerfile pour construire l’image de l’application.
- Construisez l’image et lancez un conteneur.
- Testez l’application depuis votre navigateur.

Durée estimée : 1h.
6. Exercice : Utilisation de docker compose
Objectif : Déployer une application complexe avec Docker.

Consignes :
- Compléter votre fichier app.py afin de lui ajouter une connexion a un bdd mongoDB
- Écrivez un fichier docker compose avec vos deux conteneurs
- Lancer le docker compose puis à minima vérifier que la connexion c’est bien effectuer sur la
base de données

Durée estimée : 1h.
7. Cheatsheet Docker
Commande Description
docker --version Affiche la version installée de Docker
docker images Liste les images disponibles localement
docker pull <image> Télécharge une image depuis Docker Hub
docker run <image> Lance un conteneur à partir d'une image
docker ps Liste les conteneurs en cours d'exécution
docker ps -a Liste tous les conteneurs, actifs et stoppés
docker stop <id|nom> Arrête un conteneur en cours
docker rm <id|nom> Supprime un conteneur
docker rmi <id|nom> Supprime une image
docker exec -it <id|nom> bash Ouvre un terminal interactif dans un
conteneur
docker build -t <nom_image> . Construit une image à partir d’un Dockerfil -->

## 0. Environnement Python

L'environnement du TP1 est géré avec uv, en Python 3.14. Il contient `flask` (ex5) et `pymongo` (ex6). L'organisation du dépôt et les conventions sont décrites dans le [README racine](../README.md).

```bash
cd tp1
uv sync                      # crée le .venv à partir du uv.lock
uv run python ex5/app.py     # lance l'app Flask hors Docker
```

## 1.1 Installation de Docker

Pour installer Docker sur Linux : <https://docs.docker.com/engine/install/ubuntu/>

## 1.2 Vérification de l'installation

```bash
$ docker --version
Docker version 29.8.1, build 4a63305
```

## 1.3 Manipulation de base des conteneurs

```bash
$ docker images
IMAGE                    ID             DISK USAGE   CONTENT SIZE
nginx:latest             165ddde8751e        243MB         66.8MB
tp1-flask:latest         72640d79547e        201MB           49MB
...

$ docker pull hello-world
Status: Downloaded newer image for hello-world:latest

$ docker run hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.
...

$ docker ps        # hello-world n'y est pas : il s'arrête après avoir affiché son message
$ docker ps -a
CONTAINER ID   IMAGE         COMMAND    STATUS                      NAMES
70289374b4f7   hello-world   "/hello"   Exited (0) 1 second ago     crazy_almeida
...

$ docker rm 70289374b4f7
70289374b4f7

$ docker rmi hello-world
Untagged: hello-world:latest
Deleted: sha256:c567b231f65614688711a75f31518a064258a51d442117a3e771a3a8fdba78ef
```

Le conteneur doit être supprimé avant l'image : même arrêté, il l'utilise encore.

## 1.4 Création d'un serveur web avec Docker

```bash
$ docker pull nginx
$ docker run -d -p 8080:80 --name mon_nginx nginx
$ docker ps
CONTAINER ID   IMAGE   STATUS          PORTS                  NAMES
671afe42df98   nginx   Up 1 second     0.0.0.0:8080->80/tcp   mon_nginx

$ curl -s http://localhost:8080 | grep '<title>'
<title>Welcome to nginx!</title>

$ docker stop mon_nginx
$ docker rm mon_nginx
```

`-p 8080:80` publie le port 80 du conteneur sur le port 8080 de la machine. La page par défaut de Nginx est donc accessible sur <http://localhost:8080>.

## 1.5 Déploiement d'une application Python Flask

Fichiers dans [`ex5/`](ex5/) : `app.py` (Hello World Flask), `requirements.txt` (`flask==3.1.3`) et le `Dockerfile` :

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
```

L'app écoute sur `0.0.0.0`. Sur `127.0.0.1` (l'adresse par défaut), elle ne serait pas joignable depuis l'extérieur du conteneur.

```bash
$ cd tp1/ex5
$ docker build -t tp1-flask .
$ docker run -d -p 5000:5000 --name tp1_flask tp1-flask
$ curl http://localhost:5000/
Hello, World!
```

## 1.6 Utilisation de docker compose

Fichiers dans [`ex6/`](ex6/) :

- `app.py` : l'app de l'ex5, avec en plus une connexion MongoDB (`pymongo`). L'URI de la base est lue dans `MONGO_URI`, et deux routes s'ajoutent : `/health` (ping de la base) et `/visits` (compteur enregistré en base).
- `requirements.txt` : `flask` et `pymongo`.
- `Dockerfile` : le même que pour l'ex5.
- `compose.yaml` :

```yaml
services:
  web:
    build: .
    image: tp1-flask-mongo
    ports:
      - "5000:5000"
    environment:
      MONGO_URI: mongodb://mongo:27017
      MONGO_DB: tp1
    depends_on:
      mongo:
        condition: service_healthy

  mongo:
    image: mongo:8.2
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping').ok"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  mongo-data:
```

Dans le réseau créé par Compose, `web` joint la base par le nom de son service (`mongo`). `depends_on` le fait attendre que la base soit *healthy* avant de démarrer.

On utilise `mongo:8.2` et pas `8.0`, parce que MongoDB 8.0 ne démarre pas sur un noyau Linux ≥ 6.19 ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)).

```bash
$ cd tp1/ex6
$ docker compose up -d --build
$ curl http://localhost:5000/health
{"mongo":"connected","status":"ok"}
$ curl http://localhost:5000/visits
{"visits":1}
$ curl http://localhost:5000/visits
{"visits":2}
```
