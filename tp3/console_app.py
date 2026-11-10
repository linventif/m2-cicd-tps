#!/usr/bin/env python3
"""
Application Todo List en mode console
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.todo_model import TodoList

class TodoConsoleApp:
    def __init__(self):
        self.todo_list = TodoList()
        
    def display_menu(self):
        """Affiche le menu principal"""
        print("\n" + "="*50)
        print("📝 TODO LIST - MENU PRINCIPAL")
        print("="*50)
        print("1. Afficher toutes les tâches")
        print("2. Ajouter une tâche")
        print("3. Marquer une tâche comme terminée")
        print("4. Supprimer une tâche")
        print("5. Modifier une tâche")
        print("6. Filtrer les tâches")
        print("7. Sauvegarder")
        print("8. Charger")
        print("9. Quitter")
        print("="*50)
        
    def display_tasks(self, tasks=None):
        """Affiche les tâches"""
        if tasks is None:
            tasks = self.todo_list.get_all_tasks()
            
        if not tasks:
            print("📭 Aucune tâche dans la liste.")
            return
            
        print(f"\n📋 Liste des tâches ({len(tasks)} tâche(s)):")
        print("-" * 50)
        for i, task in enumerate(tasks, 1):
            status = "✅" if task['completed'] else "⏳"
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            priority = priority_icon.get(task['priority'], "⚪")
            
            print(f"{i}. {status} {priority} {task['text']}")
            if task['description']:
                print(f"   📄 {task['description']}")
            print(f"   📅 Créée le: {task['created_at']}")
            if task['due_date']:
                print(f"   ⏰ Échéance: {task['due_date']}")
        print("-" * 50)
        
    def add_task(self):
        """Ajouter une nouvelle tâche"""
        print("\n➕ Ajouter une nouvelle tâche")
        text = input("Titre de la tâche: ").strip()
        if not text:
            print("❌ Le titre ne peut pas être vide.")
            return
            
        description = input("Description (optionnelle): ").strip()
        
        print("Priorité:")
        print("1. Haute (high)")
        print("2. Moyenne (medium)")
        print("3. Basse (low)")
        
        priority_choice = input("Choisir la priorité (1-3, défaut: 2): ").strip()
        priority_map = {"1": "high", "2": "medium", "3": "low"}
        priority = priority_map.get(priority_choice, "medium")
        
        due_date = input("Date d'échéance (YYYY-MM-DD, optionnelle): ").strip()
        if due_date and not self._is_valid_date(due_date):
            print("⚠️ Format de date invalide, pas d'échéance définie.")
            due_date = None
            
        task_id = self.todo_list.add_task(text, description, priority, due_date)
        print(f"✅ Tâche ajoutée avec succès (ID: {task_id})")
        
    def _is_valid_date(self, date_str):
        """Valide le format de date"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
            
    def complete_task(self):
        """Marquer une tâche comme terminée"""
        self.display_tasks()
        try:
            choice = int(input("\nNuméro de la tâche à marquer comme terminée: "))
            tasks = self.todo_list.get_all_tasks()
            if 1 <= choice <= len(tasks):
                task_id = tasks[choice - 1]['id']
                if self.todo_list.complete_task(task_id):
                    print("✅ Tâche marquée comme terminée!")
                else:
                    print("❌ Erreur lors de la modification de la tâche.")
            else:
                print("❌ Numéro de tâche invalide.")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
            
    def delete_task(self):
        """Supprimer une tâche"""
        self.display_tasks()
        try:
            choice = int(input("\nNuméro de la tâche à supprimer: "))
            tasks = self.todo_list.get_all_tasks()
            if 1 <= choice <= len(tasks):
                task_id = tasks[choice - 1]['id']
                if self.todo_list.delete_task(task_id):
                    print("🗑️ Tâche supprimée!")
                else:
                    print("❌ Erreur lors de la suppression.")
            else:
                print("❌ Numéro de tâche invalide.")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
            
    def update_task(self):
        """Modifier une tâche"""
        self.display_tasks()
        try:
            choice = int(input("\nNuméro de la tâche à modifier: "))
            tasks = self.todo_list.get_all_tasks()
            if 1 <= choice <= len(tasks):
                task = tasks[choice - 1]
                print(f"\nModification de la tâche: {task['text']}")
                
                new_text = input(f"Nouveau titre (actuel: {task['text']}): ").strip()
                if not new_text:
                    new_text = task['text']
                    
                new_desc = input(f"Nouvelle description (actuelle: {task['description']}): ").strip()
                if not new_desc:
                    new_desc = task['description']
                    
                print("Nouvelle priorité:")
                print("1. Haute (high)")
                print("2. Moyenne (medium)")
                print("3. Basse (low)")
                
                priority_choice = input(f"Choisir (1-3, actuelle: {task['priority']}): ").strip()
                priority_map = {"1": "high", "2": "medium", "3": "low"}
                new_priority = priority_map.get(priority_choice, task['priority'])
                
                if self.todo_list.update_task(task['id'], new_text, new_desc, new_priority):
                    print("✅ Tâche modifiée avec succès!")
                else:
                    print("❌ Erreur lors de la modification.")
            else:
                print("❌ Numéro de tâche invalide.")
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
            
    def filter_tasks(self):
        """Filtrer les tâches"""
        print("\n🔍 Filtrer les tâches:")
        print("1. Tâches terminées")
        print("2. Tâches en cours")
        print("3. Par priorité")
        
        choice = input("Votre choix (1-3): ").strip()
        
        if choice == "1":
            tasks = self.todo_list.get_completed_tasks()
            print("\n✅ Tâches terminées:")
            self.display_tasks(tasks)
        elif choice == "2":
            tasks = self.todo_list.get_pending_tasks()
            print("\n⏳ Tâches en cours:")
            self.display_tasks(tasks)
        elif choice == "3":
            print("Priorité à filtrer:")
            print("1. Haute")
            print("2. Moyenne")
            print("3. Basse")
            priority_choice = input("Votre choix (1-3): ").strip()
            priority_map = {"1": "high", "2": "medium", "3": "low"}
            priority = priority_map.get(priority_choice)
            
            if priority:
                tasks = self.todo_list.get_tasks_by_priority(priority)
                print(f"\n🎯 Tâches avec priorité {priority}:")
                self.display_tasks(tasks)
            else:
                print("❌ Choix invalide.")
        else:
            print("❌ Choix invalide.")
            
    def save_data(self):
        """Sauvegarder les données"""
        filename = input("Nom du fichier de sauvegarde (défaut: todo_save.json): ").strip()
        if not filename:
            filename = "todo_save.json"
            
        if self.todo_list.save_to_file(filename):
            print(f"💾 Données sauvegardées dans {filename}")
        else:
            print("❌ Erreur lors de la sauvegarde.")
            
    def load_data(self):
        """Charger les données"""
        filename = input("Nom du fichier à charger (défaut: todo_save.json): ").strip()
        if not filename:
            filename = "todo_save.json"
            
        if self.todo_list.load_from_file(filename):
            print(f"📂 Données chargées depuis {filename}")
        else:
            print("❌ Erreur lors du chargement ou fichier non trouvé.")
            
    def run(self):
        """Lance l'application"""
        print("🚀 Bienvenue dans votre Todo List!")
        
        while True:
            self.display_menu()
            choice = input("Votre choix (1-9): ").strip()
            
            if choice == "1":
                self.display_tasks()
            elif choice == "2":
                self.add_task()
            elif choice == "3":
                self.complete_task()
            elif choice == "4":
                self.delete_task()
            elif choice == "5":
                self.update_task()
            elif choice == "6":
                self.filter_tasks()
            elif choice == "7":
                self.save_data()
            elif choice == "8":
                self.load_data()
            elif choice == "9":
                print("👋 Au revoir!")
                break
            else:
                print("❌ Choix invalide. Veuillez choisir entre 1 et 9.")
                
            input("\nAppuyez sur Entrée pour continuer...")

def main():
    app = TodoConsoleApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application fermée par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    main()