"""
Module pour gérer une liste de tâches (TODO list).
"""

from datetime import datetime
from typing import List, Dict, Optional
import json


class Task:
    """Représente une tâche individuelle."""
    
    def __init__(self, title: str, description: str = "", priority: int = 1):
        """
        Initialise une nouvelle tâche.
        
        Args:
            title (str): Titre de la tâche
            description (str): Description détaillée de la tâche
            priority (int): Priorité de la tâche (1=basse, 2=moyenne, 3=haute)
        """
        self.id = id(self)  # Utilise l'ID de l'objet comme identifiant unique
        self.title = title
        self.description = description
        self.priority = max(1, min(3, priority))  # Limite entre 1 et 3
        self.completed = False
        self.created_at = datetime.now()
        self.completed_at = None
    
    def mark_completed(self):
        """Marque la tâche comme terminée."""
        self.completed = True
        self.completed_at = datetime.now()
    
    def mark_uncompleted(self):
        """Marque la tâche comme non terminée."""
        self.completed = False
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        """Convertit la tâche en dictionnaire pour la sérialisation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        priority_str = "★" * self.priority
        return f"{status} [{priority_str}] {self.title}"
    
    def __repr__(self):
        return f"Task(id={self.id}, title='{self.title}', completed={self.completed})"


class TodoList:
    """Gestionnaire de liste de tâches."""
    
    def __init__(self):
        """Initialise une nouvelle liste de tâches."""
        self.tasks: List[Task] = []
        self.next_id = 1
    
    def add_task(self, title: str, description: str = "", priority: int = 1) -> Task:
        """
        Ajoute une nouvelle tâche à la liste.
        
        Args:
            title (str): Titre de la tâche
            description (str): Description de la tâche
            priority (int): Priorité (1=basse, 2=moyenne, 3=haute)
        
        Returns:
            Task: La tâche créée
        
        Raises:
            ValueError: Si le titre est vide
        """
        if not title.strip():
            raise ValueError("Le titre de la tâche ne peut pas être vide")
        
        task = Task(title.strip(), description.strip(), priority)
        self.tasks.append(task)
        return task
    
    def remove_task(self, task_id: int) -> bool:
        """
        Supprime une tâche par son ID.
        
        Args:
            task_id (int): ID de la tâche à supprimer
        
        Returns:
            bool: True si la tâche a été supprimée, False sinon
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Récupère une tâche par son ID.
        
        Args:
            task_id (int): ID de la tâche
        
        Returns:
            Task or None: La tâche trouvée ou None
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def complete_task(self, task_id: int) -> bool:
        """
        Marque une tâche comme terminée.
        
        Args:
            task_id (int): ID de la tâche
        
        Returns:
            bool: True si la tâche a été marquée comme terminée
        """
        task = self.get_task(task_id)
        if task:
            task.mark_completed()
            return True
        return False
    
    def uncomplete_task(self, task_id: int) -> bool:
        """
        Marque une tâche comme non terminée.
        
        Args:
            task_id (int): ID de la tâche
        
        Returns:
            bool: True si la tâche a été marquée comme non terminée
        """
        task = self.get_task(task_id)
        if task:
            task.mark_uncompleted()
            return True
        return False
    
    def update_task(self, task_id: int, title: str = None, description: str = None, priority: int = None) -> bool:
        """
        Met à jour une tâche existante.
        
        Args:
            task_id (int): ID de la tâche
            title (str, optional): Nouveau titre
            description (str, optional): Nouvelle description
            priority (int, optional): Nouvelle priorité
        
        Returns:
            bool: True si la tâche a été mise à jour
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        if title is not None:
            if not title.strip():
                raise ValueError("Le titre de la tâche ne peut pas être vide")
            task.title = title.strip()
        
        if description is not None:
            task.description = description.strip()
        
        if priority is not None:
            task.priority = max(1, min(3, priority))
        
        return True
    
    def get_all_tasks(self) -> List[Task]:
        """Retourne toutes les tâches."""
        return self.tasks.copy()
    
    def get_completed_tasks(self) -> List[Task]:
        """Retourne les tâches terminées."""
        return [task for task in self.tasks if task.completed]
    
    def get_pending_tasks(self) -> List[Task]:
        """Retourne les tâches en attente."""
        return [task for task in self.tasks if not task.completed]
    
    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """
        Retourne les tâches d'une priorité donnée.
        
        Args:
            priority (int): Priorité recherchée (1-3)
        
        Returns:
            List[Task]: Liste des tâches de cette priorité
        """
        return [task for task in self.tasks if task.priority == priority]
    
    def get_statistics(self) -> Dict:
        """
        Retourne des statistiques sur les tâches.
        
        Returns:
            Dict: Statistiques (total, terminées, en attente, par priorité)
        """
        total = len(self.tasks)
        completed = len(self.get_completed_tasks())
        pending = len(self.get_pending_tasks())
        
        priority_stats = {}
        for priority in [1, 2, 3]:
            priority_tasks = self.get_tasks_by_priority(priority)
            priority_stats[priority] = {
                'total': len(priority_tasks),
                'completed': len([t for t in priority_tasks if t.completed]),
                'pending': len([t for t in priority_tasks if not t.completed])
            }
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 1),
            'by_priority': priority_stats
        }
    
    def clear_completed(self) -> int:
        """
        Supprime toutes les tâches terminées.
        
        Returns:
            int: Nombre de tâches supprimées
        """
        completed_tasks = self.get_completed_tasks()
        count = len(completed_tasks)
        
        for task in completed_tasks:
            self.tasks.remove(task)
        
        return count
    
    def clear_all(self):
        """Supprime toutes les tâches."""
        self.tasks.clear()
    
    def __len__(self):
        """Retourne le nombre de tâches."""
        return len(self.tasks)
    
    def __str__(self):
        """Retourne une représentation textuelle de la liste."""
        if not self.tasks:
            return "Liste de tâches vide"
        
        lines = ["=== LISTE DE TÂCHES ==="]
        
        # Tâches en attente
        pending = self.get_pending_tasks()
        if pending:
            lines.append("\n📋 Tâches en attente:")
            for task in sorted(pending, key=lambda t: t.priority, reverse=True):
                lines.append(f"  {task}")
        
        # Tâches terminées
        completed = self.get_completed_tasks()
        if completed:
            lines.append(f"\n✅ Tâches terminées ({len(completed)}):")
            for task in completed[-5:]:  # Affiche seulement les 5 dernières
                lines.append(f"  {task}")
        
        # Statistiques
        stats = self.get_statistics()
        lines.append(f"\n📊 Statistiques: {stats['completed']}/{stats['total']} terminées ({stats['completion_rate']}%)")
        
        return "\n".join(lines)