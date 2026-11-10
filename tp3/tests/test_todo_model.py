"""
Tests unitaires pour le module todo_model.
"""

import unittest
import sys
import os
from datetime import datetime

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from todo_model import Task, TodoList


class TestTask(unittest.TestCase):
    """Tests pour la classe Task."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.task = Task("Test Task", "Test description", 2)
    
    def test_task_creation(self):
        """Test la création d'une tâche."""
        task = Task("Ma tâche", "Description", 3)
        
        self.assertEqual(task.title, "Ma tâche")
        self.assertEqual(task.description, "Description")
        self.assertEqual(task.priority, 3)
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.id)
        self.assertIsInstance(task.created_at, datetime)
        self.assertIsNone(task.completed_at)
    
    def test_task_creation_with_invalid_priority(self):
        """Test la création d'une tâche avec une priorité invalide."""
        # Priorité trop basse
        task_low = Task("Test", "", 0)
        self.assertEqual(task_low.priority, 1)
        
        # Priorité trop haute
        task_high = Task("Test", "", 5)
        self.assertEqual(task_high.priority, 3)
        
        # Priorité négative
        task_neg = Task("Test", "", -1)
        self.assertEqual(task_neg.priority, 1)
    
    def test_task_creation_minimal(self):
        """Test la création d'une tâche avec paramètres minimaux."""
        task = Task("Simple task")
        
        self.assertEqual(task.title, "Simple task")
        self.assertEqual(task.description, "")
        self.assertEqual(task.priority, 1)
        self.assertFalse(task.completed)
    
    def test_mark_completed(self):
        """Test le marquage d'une tâche comme terminée."""
        self.assertFalse(self.task.completed)
        self.assertIsNone(self.task.completed_at)
        
        self.task.mark_completed()
        
        self.assertTrue(self.task.completed)
        self.assertIsNotNone(self.task.completed_at)
        self.assertIsInstance(self.task.completed_at, datetime)
    
    def test_mark_uncompleted(self):
        """Test le marquage d'une tâche comme non terminée."""
        # D'abord marquer comme terminée
        self.task.mark_completed()
        self.assertTrue(self.task.completed)
        
        # Puis marquer comme non terminée
        self.task.mark_uncompleted()
        
        self.assertFalse(self.task.completed)
        self.assertIsNone(self.task.completed_at)
    
    def test_to_dict(self):
        """Test la conversion en dictionnaire."""
        task_dict = self.task.to_dict()
        
        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict['title'], "Test Task")
        self.assertEqual(task_dict['description'], "Test description")
        self.assertEqual(task_dict['priority'], 2)
        self.assertEqual(task_dict['completed'], False)
        self.assertIsInstance(task_dict['created_at'], str)
        self.assertIsNone(task_dict['completed_at'])
        
        # Test avec tâche terminée
        self.task.mark_completed()
        completed_dict = self.task.to_dict()
        self.assertEqual(completed_dict['completed'], True)
        self.assertIsInstance(completed_dict['completed_at'], str)
    
    def test_str_representation(self):
        """Test la représentation string d'une tâche."""
        # Tâche non terminée
        str_repr = str(self.task)
        self.assertIn("○", str_repr)  # Symbole pour non terminée
        self.assertIn("Test Task", str_repr)
        self.assertIn("★★", str_repr)  # 2 étoiles pour priorité 2
        
        # Tâche terminée
        self.task.mark_completed()
        str_repr = str(self.task)
        self.assertIn("✓", str_repr)  # Symbole pour terminée
    
    def test_repr_representation(self):
        """Test la représentation repr d'une tâche."""
        repr_str = repr(self.task)
        self.assertIn("Task", repr_str)
        self.assertIn(str(self.task.id), repr_str)
        self.assertIn("Test Task", repr_str)
        self.assertIn("completed=False", repr_str)


class TestTodoList(unittest.TestCase):
    """Tests pour la classe TodoList."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.todo_list = TodoList()
    
    def test_todolist_creation(self):
        """Test la création d'une liste de tâches."""
        self.assertEqual(len(self.todo_list), 0)
        self.assertEqual(len(self.todo_list.tasks), 0)
    
    def test_add_task(self):
        """Test l'ajout d'une tâche."""
        task = self.todo_list.add_task("Ma première tâche", "Description", 2)
        
        self.assertIsInstance(task, Task)
        self.assertEqual(task.title, "Ma première tâche")
        self.assertEqual(task.description, "Description")
        self.assertEqual(task.priority, 2)
        self.assertEqual(len(self.todo_list), 1)
    
    def test_add_task_minimal(self):
        """Test l'ajout d'une tâche avec paramètres minimaux."""
        task = self.todo_list.add_task("Tâche simple")
        
        self.assertEqual(task.title, "Tâche simple")
        self.assertEqual(task.description, "")
        self.assertEqual(task.priority, 1)
    
    def test_add_task_with_whitespace(self):
        """Test l'ajout d'une tâche avec espaces en trop."""
        task = self.todo_list.add_task("  Titre avec espaces  ", "  Description  ")
        
        self.assertEqual(task.title, "Titre avec espaces")
        self.assertEqual(task.description, "Description")
    
    def test_add_task_empty_title(self):
        """Test l'ajout d'une tâche avec titre vide."""
        with self.assertRaises(ValueError):
            self.todo_list.add_task("")
        
        with self.assertRaises(ValueError):
            self.todo_list.add_task("   ")  # Seulement des espaces
    
    def test_remove_task(self):
        """Test la suppression d'une tâche."""
        task = self.todo_list.add_task("Tâche à supprimer")
        task_id = task.id
        
        # Vérifier que la tâche existe
        self.assertEqual(len(self.todo_list), 1)
        
        # Supprimer la tâche
        result = self.todo_list.remove_task(task_id)
        
        self.assertTrue(result)
        self.assertEqual(len(self.todo_list), 0)
        self.assertIsNone(self.todo_list.get_task(task_id))
    
    def test_remove_nonexistent_task(self):
        """Test la suppression d'une tâche inexistante."""
        result = self.todo_list.remove_task(99999)
        self.assertFalse(result)
    
    def test_get_task(self):
        """Test la récupération d'une tâche par ID."""
        task = self.todo_list.add_task("Tâche test")
        
        retrieved_task = self.todo_list.get_task(task.id)
        
        self.assertEqual(retrieved_task, task)
        self.assertEqual(retrieved_task.title, "Tâche test")
    
    def test_get_nonexistent_task(self):
        """Test la récupération d'une tâche inexistante."""
        task = self.todo_list.get_task(99999)
        self.assertIsNone(task)
    
    def test_complete_task(self):
        """Test le marquage d'une tâche comme terminée."""
        task = self.todo_list.add_task("Tâche à terminer")
        
        result = self.todo_list.complete_task(task.id)
        
        self.assertTrue(result)
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)
    
    def test_complete_nonexistent_task(self):
        """Test le marquage d'une tâche inexistante comme terminée."""
        result = self.todo_list.complete_task(99999)
        self.assertFalse(result)
    
    def test_uncomplete_task(self):
        """Test le marquage d'une tâche comme non terminée."""
        task = self.todo_list.add_task("Tâche test")
        task.mark_completed()
        
        result = self.todo_list.uncomplete_task(task.id)
        
        self.assertTrue(result)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)
    
    def test_uncomplete_nonexistent_task(self):
        """Test le marquage d'une tâche inexistante comme non terminée."""
        result = self.todo_list.uncomplete_task(99999)
        self.assertFalse(result)
    
    def test_update_task(self):
        """Test la mise à jour d'une tâche."""
        task = self.todo_list.add_task("Titre original", "Description originale", 1)
        
        result = self.todo_list.update_task(
            task.id,
            title="Nouveau titre",
            description="Nouvelle description",
            priority=3
        )
        
        self.assertTrue(result)
        self.assertEqual(task.title, "Nouveau titre")
        self.assertEqual(task.description, "Nouvelle description")
        self.assertEqual(task.priority, 3)
    
    def test_update_task_partial(self):
        """Test la mise à jour partielle d'une tâche."""
        task = self.todo_list.add_task("Titre", "Description", 1)
        
        # Mise à jour seulement du titre
        result = self.todo_list.update_task(task.id, title="Nouveau titre")
        
        self.assertTrue(result)
        self.assertEqual(task.title, "Nouveau titre")
        self.assertEqual(task.description, "Description")  # Inchangé
        self.assertEqual(task.priority, 1)  # Inchangé
    
    def test_update_task_empty_title(self):
        """Test la mise à jour avec un titre vide."""
        task = self.todo_list.add_task("Titre original")
        
        with self.assertRaises(ValueError):
            self.todo_list.update_task(task.id, title="")
        
        with self.assertRaises(ValueError):
            self.todo_list.update_task(task.id, title="   ")
    
    def test_update_nonexistent_task(self):
        """Test la mise à jour d'une tâche inexistante."""
        result = self.todo_list.update_task(99999, title="Nouveau titre")
        self.assertFalse(result)
    
    def test_get_all_tasks(self):
        """Test la récupération de toutes les tâches."""
        # Liste vide
        tasks = self.todo_list.get_all_tasks()
        self.assertEqual(len(tasks), 0)
        
        # Ajouter des tâches
        task1 = self.todo_list.add_task("Tâche 1")
        task2 = self.todo_list.add_task("Tâche 2")
        
        tasks = self.todo_list.get_all_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIn(task1, tasks)
        self.assertIn(task2, tasks)
        
        # Vérifier que c'est une copie (pas la liste originale)
        tasks.append("test")
        self.assertEqual(len(self.todo_list.tasks), 2)
    
    def test_get_completed_tasks(self):
        """Test la récupération des tâches terminées."""
        task1 = self.todo_list.add_task("Tâche 1")
        task2 = self.todo_list.add_task("Tâche 2")
        task3 = self.todo_list.add_task("Tâche 3")
        
        # Marquer certaines comme terminées
        task1.mark_completed()
        task3.mark_completed()
        
        completed = self.todo_list.get_completed_tasks()
        
        self.assertEqual(len(completed), 2)
        self.assertIn(task1, completed)
        self.assertIn(task3, completed)
        self.assertNotIn(task2, completed)
    
    def test_get_pending_tasks(self):
        """Test la récupération des tâches en attente."""
        task1 = self.todo_list.add_task("Tâche 1")
        task2 = self.todo_list.add_task("Tâche 2")
        task3 = self.todo_list.add_task("Tâche 3")
        
        # Marquer une comme terminée
        task2.mark_completed()
        
        pending = self.todo_list.get_pending_tasks()
        
        self.assertEqual(len(pending), 2)
        self.assertIn(task1, pending)
        self.assertIn(task3, pending)
        self.assertNotIn(task2, pending)
    
    def test_get_tasks_by_priority(self):
        """Test la récupération des tâches par priorité."""
        task1 = self.todo_list.add_task("Basse priorité", "", 1)
        task2 = self.todo_list.add_task("Moyenne priorité", "", 2)
        task3 = self.todo_list.add_task("Haute priorité", "", 3)
        task4 = self.todo_list.add_task("Autre haute priorité", "", 3)
        
        # Tester chaque priorité
        low_priority = self.todo_list.get_tasks_by_priority(1)
        self.assertEqual(len(low_priority), 1)
        self.assertIn(task1, low_priority)
        
        medium_priority = self.todo_list.get_tasks_by_priority(2)
        self.assertEqual(len(medium_priority), 1)
        self.assertIn(task2, medium_priority)
        
        high_priority = self.todo_list.get_tasks_by_priority(3)
        self.assertEqual(len(high_priority), 2)
        self.assertIn(task3, high_priority)
        self.assertIn(task4, high_priority)
        
        # Priorité inexistante
        empty = self.todo_list.get_tasks_by_priority(4)
        self.assertEqual(len(empty), 0)
    
    def test_get_statistics(self):
        """Test la récupération des statistiques."""
        # Liste vide
        stats = self.todo_list.get_statistics()
        expected = {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'completion_rate': 0,
            'by_priority': {
                1: {'total': 0, 'completed': 0, 'pending': 0},
                2: {'total': 0, 'completed': 0, 'pending': 0},
                3: {'total': 0, 'completed': 0, 'pending': 0}
            }
        }
        self.assertEqual(stats, expected)
        
        # Ajouter des tâches
        task1 = self.todo_list.add_task("Tâche 1", "", 1)  # Basse
        task2 = self.todo_list.add_task("Tâche 2", "", 2)  # Moyenne
        task3 = self.todo_list.add_task("Tâche 3", "", 3)  # Haute
        task4 = self.todo_list.add_task("Tâche 4", "", 3)  # Haute
        
        # Marquer certaines comme terminées
        task1.mark_completed()
        task3.mark_completed()
        
        stats = self.todo_list.get_statistics()
        
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['completed'], 2)
        self.assertEqual(stats['pending'], 2)
        self.assertEqual(stats['completion_rate'], 50.0)
        
        # Vérifier les statistiques par priorité
        self.assertEqual(stats['by_priority'][1]['total'], 1)
        self.assertEqual(stats['by_priority'][1]['completed'], 1)
        self.assertEqual(stats['by_priority'][1]['pending'], 0)
        
        self.assertEqual(stats['by_priority'][2]['total'], 1)
        self.assertEqual(stats['by_priority'][2]['completed'], 0)
        self.assertEqual(stats['by_priority'][2]['pending'], 1)
        
        self.assertEqual(stats['by_priority'][3]['total'], 2)
        self.assertEqual(stats['by_priority'][3]['completed'], 1)
        self.assertEqual(stats['by_priority'][3]['pending'], 1)
    
    def test_clear_completed(self):
        """Test la suppression de toutes les tâches terminées."""
        task1 = self.todo_list.add_task("Tâche 1")
        task2 = self.todo_list.add_task("Tâche 2")
        task3 = self.todo_list.add_task("Tâche 3")
        task4 = self.todo_list.add_task("Tâche 4")
        
        # Marquer certaines comme terminées
        task1.mark_completed()
        task3.mark_completed()
        task4.mark_completed()
        
        # Supprimer les terminées
        removed_count = self.todo_list.clear_completed()
        
        self.assertEqual(removed_count, 3)
        self.assertEqual(len(self.todo_list), 1)
        self.assertIn(task2, self.todo_list.tasks)  # Seule la non terminée reste
        
        # Test avec aucune tâche terminée
        removed_count = self.todo_list.clear_completed()
        self.assertEqual(removed_count, 0)
    
    def test_clear_all(self):
        """Test la suppression de toutes les tâches."""
        self.todo_list.add_task("Tâche 1")
        self.todo_list.add_task("Tâche 2")
        self.todo_list.add_task("Tâche 3")
        
        self.assertEqual(len(self.todo_list), 3)
        
        self.todo_list.clear_all()
        
        self.assertEqual(len(self.todo_list), 0)
        self.assertEqual(len(self.todo_list.tasks), 0)
    
    def test_len_method(self):
        """Test la méthode __len__."""
        self.assertEqual(len(self.todo_list), 0)
        
        self.todo_list.add_task("Tâche 1")
        self.assertEqual(len(self.todo_list), 1)
        
        self.todo_list.add_task("Tâche 2")
        self.todo_list.add_task("Tâche 3")
        self.assertEqual(len(self.todo_list), 3)
    
    def test_str_representation(self):
        """Test la représentation string de la liste."""
        # Liste vide
        str_repr = str(self.todo_list)
        self.assertEqual(str_repr, "Liste de tâches vide")
        
        # Avec des tâches
        task1 = self.todo_list.add_task("Tâche en attente", "", 1)
        task2 = self.todo_list.add_task("Tâche terminée", "", 2)
        task2.mark_completed()
        
        str_repr = str(self.todo_list)
        self.assertIn("LISTE DE TÂCHES", str_repr)
        self.assertIn("Tâches en attente", str_repr)
        self.assertIn("Tâches terminées", str_repr)
        self.assertIn("Statistiques", str_repr)
        self.assertIn("Tâche en attente", str_repr)
        self.assertIn("Tâche terminée", str_repr)


class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour l'ensemble du système."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.todo_list = TodoList()
    
    def test_full_workflow(self):
        """Test un workflow complet d'utilisation."""
        # Ajouter des tâches
        task1 = self.todo_list.add_task("Faire les courses", "Acheter lait et pain", 2)
        task2 = self.todo_list.add_task("Appeler le médecin", "", 3)
        task3 = self.todo_list.add_task("Lire un livre", "Finir le chapitre 5", 1)
        
        # Vérifier l'état initial
        self.assertEqual(len(self.todo_list), 3)
        self.assertEqual(len(self.todo_list.get_pending_tasks()), 3)
        self.assertEqual(len(self.todo_list.get_completed_tasks()), 0)
        
        # Terminer une tâche
        self.todo_list.complete_task(task1.id)
        self.assertEqual(len(self.todo_list.get_pending_tasks()), 2)
        self.assertEqual(len(self.todo_list.get_completed_tasks()), 1)
        
        # Modifier une tâche
        self.todo_list.update_task(task3.id, title="Lire deux livres", priority=2)
        updated_task = self.todo_list.get_task(task3.id)
        self.assertEqual(updated_task.title, "Lire deux livres")
        self.assertEqual(updated_task.priority, 2)
        
        # Supprimer une tâche
        self.todo_list.remove_task(task2.id)
        self.assertEqual(len(self.todo_list), 2)
        self.assertIsNone(self.todo_list.get_task(task2.id))
        
        # Vérifier les statistiques finales
        stats = self.todo_list.get_statistics()
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['completion_rate'], 50.0)
    
    def test_edge_cases(self):
        """Test des cas limites."""
        # Tâche avec titre très long
        long_title = "A" * 1000
        task = self.todo_list.add_task(long_title)
        self.assertEqual(task.title, long_title)
        
        # Tâche avec caractères spéciaux
        special_task = self.todo_list.add_task("Tâche avec émojis 😀🎉", "Description avec accents éàù")
        self.assertEqual(special_task.title, "Tâche avec émojis 😀🎉")
        self.assertEqual(special_task.description, "Description avec accents éàù")
        
        # Opérations multiples sur la même tâche
        task_id = special_task.id
        self.todo_list.complete_task(task_id)
        self.todo_list.uncomplete_task(task_id)
        self.todo_list.complete_task(task_id)
        
        final_task = self.todo_list.get_task(task_id)
        self.assertTrue(final_task.completed)


if __name__ == '__main__':
    # Configuration pour les tests
    unittest.main(verbosity=2)