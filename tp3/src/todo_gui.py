"""
Interface graphique pour l'application Todo List.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional
from todo_model import TodoList, Task


class TodoGUI:
    """Interface graphique pour la gestion des tâches."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialise l'interface graphique.
        
        Args:
            root (tk.Tk): Fenêtre principale Tkinter
        """
        self.root = root
        self.todo_list = TodoList()
        
        # Configuration de la fenêtre principale
        self.root.title("📋 Todo List")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Variables Tkinter
        self.task_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.priority_var = tk.IntVar(value=1)
        self.filter_var = tk.StringVar(value="all")
        
        # Créer l'interface
        self.setup_ui()
        
        # Rafraîchir l'affichage initial
        self.refresh_task_list()
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === Section d'ajout de tâche ===
        add_frame = ttk.LabelFrame(main_frame, text="➕ Ajouter une tâche", padding="10")
        add_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        
        # Titre de la tâche
        ttk.Label(add_frame, text="Titre:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        title_entry = ttk.Entry(add_frame, textvariable=self.task_var, width=40)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        title_entry.bind('<Return>', lambda e: self.add_task())
        
        # Description
        ttk.Label(add_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        desc_entry = ttk.Entry(add_frame, textvariable=self.description_var, width=40)
        desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Priorité
        priority_frame = ttk.Frame(add_frame)
        priority_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(priority_frame, text="Priorité:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="🟢 Basse", variable=self.priority_var, value=1).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="🟡 Moyenne", variable=self.priority_var, value=2).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="🔴 Haute", variable=self.priority_var, value=3).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton d'ajout
        add_btn = ttk.Button(add_frame, text="➕ Ajouter", command=self.add_task)
        add_btn.grid(row=2, column=1, sticky=tk.E, pady=(10, 0))
        
        # === Section de filtrage ===
        filter_frame = ttk.Frame(main_frame)
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filtre:").pack(side=tk.LEFT, padx=(0, 10))
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                  values=["all", "pending", "completed", "priority_high", "priority_medium", "priority_low"],
                                  state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Mapping des valeurs pour l'affichage
        filter_mapping = {
            "all": "📋 Toutes",
            "pending": "⏳ En attente",
            "completed": "✅ Terminées",
            "priority_high": "🔴 Haute priorité",
            "priority_medium": "🟡 Priorité moyenne",
            "priority_low": "🟢 Basse priorité"
        }
        
        # Configurer l'affichage du combobox
        def format_filter_display(event):
            current = self.filter_var.get()
            return filter_mapping.get(current, current)
        
        # Boutons d'action rapide
        ttk.Button(filter_frame, text="🧹 Nettoyer terminées", 
                  command=self.clear_completed).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(filter_frame, text="📊 Statistiques", 
                  command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        
        # === Liste des tâches ===
        list_frame = ttk.LabelFrame(main_frame, text="📝 Liste des tâches", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview pour afficher les tâches
        columns = ('ID', 'Statut', 'Priorité', 'Titre', 'Description', 'Créée le')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        self.tree.heading('ID', text='ID')
        self.tree.heading('Statut', text='Statut')
        self.tree.heading('Priorité', text='Priorité')
        self.tree.heading('Titre', text='Titre')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Créée le', text='Créée le')
        
        self.tree.column('ID', width=60, anchor=tk.CENTER)
        self.tree.column('Statut', width=80, anchor=tk.CENTER)
        self.tree.column('Priorité', width=80, anchor=tk.CENTER)
        self.tree.column('Titre', width=200)
        self.tree.column('Description', width=250)
        self.tree.column('Créée le', width=120, anchor=tk.CENTER)
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement du treeview et scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # === Boutons d'action ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="✅ Marquer terminé", 
                  command=self.toggle_task_completion).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✏️ Modifier", 
                  command=self.edit_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Supprimer", 
                  command=self.delete_task).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bind double-click pour modifier
        self.tree.bind('<Double-1>', lambda e: self.edit_task())
        
        # Bind right-click pour menu contextuel
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Menu contextuel
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✅ Marquer terminé/non terminé", command=self.toggle_task_completion)
        self.context_menu.add_command(label="✏️ Modifier", command=self.edit_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Supprimer", command=self.delete_task)
    
    def add_task(self):
        """Ajoute une nouvelle tâche."""
        title = self.task_var.get().strip()
        description = self.description_var.get().strip()
        priority = self.priority_var.get()
        
        if not title:
            messagebox.showwarning("Erreur", "Veuillez entrer un titre pour la tâche.")
            return
        
        try:
            self.todo_list.add_task(title, description, priority)
            
            # Réinitialiser les champs
            self.task_var.set("")
            self.description_var.set("")
            self.priority_var.set(1)
            
            # Rafraîchir l'affichage
            self.refresh_task_list()
            
            messagebox.showinfo("Succès", f"Tâche '{title}' ajoutée avec succès!")
            
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
    
    def refresh_task_list(self):
        """Rafraîchit l'affichage de la liste des tâches."""
        # Vider le treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtenir les tâches selon le filtre
        filter_type = self.filter_var.get()
        
        if filter_type == "all":
            tasks = self.todo_list.get_all_tasks()
        elif filter_type == "pending":
            tasks = self.todo_list.get_pending_tasks()
        elif filter_type == "completed":
            tasks = self.todo_list.get_completed_tasks()
        elif filter_type == "priority_high":
            tasks = self.todo_list.get_tasks_by_priority(3)
        elif filter_type == "priority_medium":
            tasks = self.todo_list.get_tasks_by_priority(2)
        elif filter_type == "priority_low":
            tasks = self.todo_list.get_tasks_by_priority(1)
        else:
            tasks = self.todo_list.get_all_tasks()
        
        # Ajouter les tâches au treeview
        for task in tasks:
            status = "✅ Terminé" if task.completed else "⏳ En attente"
            priority_text = {1: "🟢 Basse", 2: "🟡 Moyenne", 3: "🔴 Haute"}[task.priority]
            created_date = task.created_at.strftime("%d/%m/%Y %H:%M")
            
            # Tags pour le style
            tags = []
            if task.completed:
                tags.append("completed")
            if task.priority == 3:
                tags.append("high_priority")
            
            self.tree.insert("", "end", values=(
                task.id,
                status,
                priority_text,
                task.title,
                task.description,
                created_date
            ), tags=tags)
        
        # Configuration des styles
        self.tree.tag_configure("completed", foreground="gray")
        self.tree.tag_configure("high_priority", foreground="red")
        
        # Mettre à jour le titre de la section
        stats = self.todo_list.get_statistics()
        list_frame = self.tree.master
        list_frame.configure(text=f"📝 Liste des tâches ({len(tasks)} affichées, {stats['pending']} en attente)")
    
    def get_selected_task(self) -> Optional[Task]:
        """Retourne la tâche sélectionnée dans le treeview."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une tâche.")
            return None
        
        item = self.tree.item(selection[0])
        task_id = int(item['values'][0])
        return self.todo_list.get_task(task_id)
    
    def toggle_task_completion(self):
        """Bascule l'état de completion d'une tâche."""
        task = self.get_selected_task()
        if not task:
            return
        
        if task.completed:
            self.todo_list.uncomplete_task(task.id)
            status = "non terminée"
        else:
            self.todo_list.complete_task(task.id)
            status = "terminée"
        
        self.refresh_task_list()
        messagebox.showinfo("Succès", f"Tâche '{task.title}' marquée comme {status}.")
    
    def edit_task(self):
        """Modifie une tâche sélectionnée."""
        task = self.get_selected_task()
        if not task:
            return
        
        # Créer une fenêtre de modification
        edit_window = tk.Toplevel(self.root)
        edit_window.title("✏️ Modifier la tâche")
        edit_window.geometry("500x300")
        edit_window.resizable(False, False)
        
        # Variables pour les champs
        new_title = tk.StringVar(value=task.title)
        new_description = tk.StringVar(value=task.description)
        new_priority = tk.IntVar(value=task.priority)
        
        # Interface de modification
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="Titre:").pack(anchor=tk.W, pady=(0, 5))
        title_entry = ttk.Entry(main_frame, textvariable=new_title, width=50)
        title_entry.pack(fill=tk.X, pady=(0, 10))
        title_entry.focus()
        
        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor=tk.W, pady=(0, 5))
        desc_entry = ttk.Entry(main_frame, textvariable=new_description, width=50)
        desc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Priorité
        ttk.Label(main_frame, text="Priorité:").pack(anchor=tk.W, pady=(0, 5))
        priority_frame = ttk.Frame(main_frame)
        priority_frame.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Radiobutton(priority_frame, text="🟢 Basse", variable=new_priority, value=1).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="🟡 Moyenne", variable=new_priority, value=2).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="🔴 Haute", variable=new_priority, value=3).pack(side=tk.LEFT)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_changes():
            title = new_title.get().strip()
            if not title:
                messagebox.showwarning("Erreur", "Le titre ne peut pas être vide.")
                return
            
            try:
                self.todo_list.update_task(
                    task.id,
                    title=title,
                    description=new_description.get().strip(),
                    priority=new_priority.get()
                )
                
                edit_window.destroy()
                self.refresh_task_list()
                messagebox.showinfo("Succès", f"Tâche '{title}' modifiée avec succès!")
                
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
        
        ttk.Button(button_frame, text="💾 Sauvegarder", command=save_changes).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Annuler", command=edit_window.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter pour sauvegarder
        edit_window.bind('<Return>', lambda e: save_changes())
        edit_window.bind('<Escape>', lambda e: edit_window.destroy())
    
    def delete_task(self):
        """Supprime une tâche sélectionnée."""
        task = self.get_selected_task()
        if not task:
            return
        
        # Confirmation
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer la tâche '{task.title}' ?",
            icon='warning'
        )
        
        if result:
            self.todo_list.remove_task(task.id)
            self.refresh_task_list()
            messagebox.showinfo("Succès", f"Tâche '{task.title}' supprimée.")
    
    def clear_completed(self):
        """Supprime toutes les tâches terminées."""
        completed_count = len(self.todo_list.get_completed_tasks())
        
        if completed_count == 0:
            messagebox.showinfo("Information", "Aucune tâche terminée à supprimer.")
            return
        
        result = messagebox.askyesno(
            "Confirmation",
            f"Supprimer {completed_count} tâche(s) terminée(s) ?",
            icon='warning'
        )
        
        if result:
            removed_count = self.todo_list.clear_completed()
            self.refresh_task_list()
            messagebox.showinfo("Succès", f"{removed_count} tâche(s) terminée(s) supprimée(s).")
    
    def show_statistics(self):
        """Affiche les statistiques des tâches."""
        stats = self.todo_list.get_statistics()
        
        # Créer la fenêtre des statistiques
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Statistiques")
        stats_window.geometry("400x300")
        stats_window.resizable(False, False)
        
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="📊 Statistiques des tâches", font=('TkDefaultFont', 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Statistiques générales
        general_frame = ttk.LabelFrame(main_frame, text="Général", padding="10")
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(general_frame, text=f"Total des tâches: {stats['total']}").pack(anchor=tk.W)
        ttk.Label(general_frame, text=f"Tâches terminées: {stats['completed']}").pack(anchor=tk.W)
        ttk.Label(general_frame, text=f"Tâches en attente: {stats['pending']}").pack(anchor=tk.W)
        ttk.Label(general_frame, text=f"Taux de completion: {stats['completion_rate']}%").pack(anchor=tk.W)
        
        # Statistiques par priorité
        priority_frame = ttk.LabelFrame(main_frame, text="Par priorité", padding="10")
        priority_frame.pack(fill=tk.X)
        
        priority_names = {1: "🟢 Basse", 2: "🟡 Moyenne", 3: "🔴 Haute"}
        
        for priority in [3, 2, 1]:  # Afficher de haute à basse priorité
            p_stats = stats['by_priority'][priority]
            name = priority_names[priority]
            
            if p_stats['total'] > 0:
                completion_rate = round((p_stats['completed'] / p_stats['total'] * 100), 1)
                text = f"{name}: {p_stats['completed']}/{p_stats['total']} ({completion_rate}%)"
            else:
                text = f"{name}: Aucune tâche"
            
            ttk.Label(priority_frame, text=text).pack(anchor=tk.W)
        
        # Bouton de fermeture
        ttk.Button(main_frame, text="Fermer", command=stats_window.destroy).pack(pady=(20, 0))
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel."""
        # Sélectionner l'item sous le curseur
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)


def main():
    """Fonction principale pour lancer l'application."""
    root = tk.Tk()
    app = TodoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()