# 📋 Application Todo List

Une application de gestion de tâches complète développée en Python avec interface graphique tkinter.

## 🌟 Fonctionnalités

- ➕ **Ajouter des tâches** avec titre, description et priorité
- ✏️ **Modifier des tâches** existantes
- ✅ **Marquer des tâches** comme terminées/non terminées
- 🗑️ **Supprimer des tâches**
- 🔍 **Filtrer les tâches** par statut (toutes, en attente, terminées) ou priorité
- 📊 **Statistiques détaillées** sur vos tâches
- 🧹 **Nettoyage automatique** des tâches terminées
- 🎯 **Système de priorités** (basse, moyenne, haute)
- 🖱️ **Interface intuitive** avec menus contextuels

## 🚀 Installation et Lancement

### Prérequis

- Python 3.6 ou supérieur
- tkinter (généralement inclus avec Python)
  - Sur Ubuntu/Debian : `sudo apt-get install python3-tk`
  - Sur CentOS/RHEL : `sudo yum install tkinter`

### Lancement de l'application

```bash
# Méthode 1 : Lancer directement
python main.py

# Méthode 2 : Avec données d'exemple
python main.py
# (Choisir 'Oui' pour charger des tâches d'exemple)

# Méthode 3 : Rendre exécutable (Linux/Mac)
chmod +x main.py
./main.py
```

### Options en ligne de commande

```bash
# Afficher l'aide
python main.py --help

# Lancer les tests
python main.py --test

# Afficher la version
python main.py --version
```

## 🧪 Tests

L'application inclut une suite complète de tests unitaires.

```bash
# Lancer tous les tests
python main.py --test

# Ou directement avec unittest
python -m unittest discover tests -v

# Ou lancer un fichier de test spécifique
python -m unittest tests.test_todo_model -v
```

### Couverture des tests

Les tests couvrent :
- ✅ Création et manipulation des tâches
- ✅ Toutes les méthodes de la classe TodoList
- ✅ Gestion des erreurs et cas limites
- ✅ Workflow complet d'utilisation
- ✅ Cas d'intégration

## 📁 Structure du Projet

```
tp-gitlab-nom-prenom/
├── main.py              # Point d'entrée principal
├── README.md            # Cette documentation
├── requirements.txt     # Dépendances (optionnelles)
├── src/
│   ├── todo_model.py    # Classes Task et TodoList
│   └── todo_gui.py      # Interface graphique tkinter
└── tests/
    └── test_todo_model.py # Tests unitaires
```

## 💻 Utilisation de l'Interface

### Ajouter une Tâche

1. Saisissez le **titre** de la tâche (obligatoire)
2. Ajoutez une **description** (optionnel)
3. Choisissez la **priorité** :
   - 🟢 Basse (par défaut)
   - 🟡 Moyenne
   - 🔴 Haute
4. Cliquez sur **"➕ Ajouter"** ou appuyez sur **Entrée**

### Gérer les Tâches

- **Double-clic** sur une tâche pour la modifier
- **Clic droit** pour ouvrir le menu contextuel
- **Sélectionner** une tâche et utiliser les boutons d'action
- **Filtrer** avec le menu déroulant pour voir certaines tâches

### Raccourcis Clavier

- **Entrée** : Ajouter une tâche (dans le champ titre)
- **Double-clic** : Modifier une tâche sélectionnée
- **Clic droit** : Menu contextuel sur une tâche

## 🏗️ Architecture Technique

### Classes Principales

#### `Task`
Représente une tâche individuelle avec :
- `title` : Titre de la tâche
- `description` : Description détaillée
- `priority` : Priorité (1=basse, 2=moyenne, 3=haute)
- `completed` : État de completion
- `created_at` : Date de création
- `completed_at` : Date de completion

#### `TodoList`
Gestionnaire de la collection de tâches avec méthodes :
- `add_task()` : Ajouter une tâche
- `remove_task()` : Supprimer une tâche
- `complete_task()` : Marquer comme terminée
- `update_task()` : Modifier une tâche
- `get_statistics()` : Obtenir des statistiques
- Et bien d'autres...

#### `TodoGUI`
Interface graphique tkinter avec :
- Formulaire d'ajout de tâches
- Liste interactive des tâches
- Filtres et options de tri
- Fenêtres de modification et statistiques

## 🔧 Développement

### Ajouter de nouvelles fonctionnalités

1. **Modifiez `todo_model.py`** pour les nouvelles logiques métier
2. **Ajoutez des tests** dans `test_todo_model.py`
3. **Mettez à jour l'interface** dans `todo_gui.py`
4. **Testez** avec `python main.py --test`

### Structure de test recommandée

```python
def test_nouvelle_fonctionnalite(self):
    """Test pour une nouvelle fonctionnalité."""
    # Arrange - Configuration
    todo_list = TodoList()
    
    # Act - Action
    resultat = todo_list.nouvelle_methode()
    
    # Assert - Vérification
    self.assertEqual(resultat, valeur_attendue)
```

## 📊 Exemples d'Utilisation

### Utilisation Programmatique

```python
from src.todo_model import TodoList, Task

# Créer une liste de tâches
todo = TodoList()

# Ajouter des tâches
task1 = todo.add_task("Faire les courses", "Lait et pain", priority=2)
task2 = todo.add_task("Appeler maman", priority=3)

# Marquer comme terminée
todo.complete_task(task1.id)

# Statistiques
stats = todo.get_statistics()
print(f"Taux de completion : {stats['completion_rate']}%")

# Afficher toutes les tâches
for task in todo.get_all_tasks():
    print(f"- {task}")
```

### Cas d'Usage Typiques

1. **Gestion personnelle** : Tâches quotidiennes, courses, rendez-vous
2. **Projets** : Décomposer un projet en tâches avec priorités
3. **Équipe** : Partager une liste de tâches communes
4. **Suivi** : Analyser la productivité avec les statistiques

## 🚀 Améliorations Possibles

### Fonctionnalités Futures

- 💾 **Sauvegarde** : Persistance des données en JSON/SQLite
- 🔔 **Notifications** : Rappels pour les tâches importantes
- 📅 **Dates d'échéance** : Gestion des deadlines
- 🏷️ **Tags** : Catégorisation des tâches
- 🌙 **Mode sombre** : Interface alternative
- 📱 **Export** : Export vers différents formats
- 🔄 **Synchronisation** : Sync avec services cloud
- 👥 **Collaboration** : Partage de listes entre utilisateurs

### Améliorations Techniques

- 🗄️ **Base de données** : SQLite pour la persistance
- 🌐 **API Web** : Interface REST pour l'accès distant
- 📱 **Version mobile** : Port vers Kivy ou web
- 🔧 **Configuration** : Fichier de config utilisateur
- 📈 **Métriques** : Tracking d'utilisation avancé

## 🤝 Contribution

### Comment Contribuer

1. **Fork** le projet
2. **Créez** une branche pour votre fonctionnalité
3. **Ajoutez** vos modifications avec des tests
4. **Exécutez** les tests : `python main.py --test`
5. **Soumettez** une pull request

### Standards de Code

- **PEP 8** : Style de code Python
- **Docstrings** : Documentation des fonctions
- **Tests** : Couverture minimale de 80%
- **Comments** : Code commenté en français

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Votre Nom**
- Email : votre.email@example.com
- GitHub : [@votre-username](https://github.com/votre-username)

## 🙏 Remerciements

- **Python Community** pour l'excellent écosystème
- **tkinter** pour l'interface graphique simple et efficace
- **Tous les contributeurs** qui améliorent ce projet

---

*Développé avec ❤️ en Python*