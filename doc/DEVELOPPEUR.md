# DEVELOPPEMENT

Cette documentation décrit toutes les étapes nécessaires à l'intallation et au développement de l'application Recoco-sync.

Les règles et standards de codage y sont décrits.

## Installation

La plateforme Recoco-sync est open source et la gestion de version est assuré via Github.
La première étape est donc de cloner ce repository github.

### Prérequis

On utilise [uv](https://docs.astral.sh/uv/) pour l'installation de python, ainsi que pour la gestion des dépendances. Le hook precommit uv permet de re-générer le fichier requirements.txt nécessaireau déploiement.

### Environment virtuel python

```sh
make install
```

### Services docker

Plusieurs services sont dockerisés:
- Postgresql: base de donnée de l'application
- Redis: messaging pour les tâches asynchrones
- Grist: une instance standalone pour du test

```sh
docker-compose up -d
```

### Variables d'environnement

Copier les [.env.template](.env.template) dans un fichier `.env` puis mettre à jour les variables d'environements.

```sh
cp .env.sample .env
```

### Executer les migrations

```sh
make migrate
```

### Faire tourner les tests

```sh
make test
```

### Lancer l'applciation

```sh
make runserver
make runworker
```

### Installer les hooks de pre-commit

Pour installer les git hook de pre-commit, installer le package precommit et l'installer:

```sh
pip install pre-commit
pre-commit install
make precommit
```
