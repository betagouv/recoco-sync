# Recoco-sync

Recoco-sync est une application qui permet la synchronisation des portails de [Recommandations Collaboratives](https://github.com/betagouv/recommandations-collaboratives) avec des applications tierces.

Un webhook permet de notifier des modifications apportées sur les projets. Recoco-sync permet de créer une configuration pour s'abonner à ces événements de webhook et pousser les données vers des applications tierces.

## Solution technique

La plateforme est basée sur le framework [Django](https://www.djangoproject.com/), et une base de donnée [PostgreSQL](https://www.postgresql.org/).

Des tâches asynchrones sont déployées, notamment pour traiter les événements entrants du webhook. La librairie [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) est utilisée pour cela, avec [Redis](https://redis.io/fr/).

Plusieurs outils et processus sont utilisés pour gérer la qualité de code.

Trouvez les détails d'installation de l'application en local pour le développement sur la documentation dédiée : [DEVELOPPEUR.md](doc/DEVELOPPEUR.md).

Trouvez les détails du déploiement de l'application sur la documentation dédiée : [DEPLOIEMENT.md](doc/DEPLOIEMENT.md).

Les prochaines étapes sont listées [ici](doc/TODO.md).
