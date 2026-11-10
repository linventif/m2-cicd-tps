#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("🚀 Tentative de lancement de l'interface graphique...")
        
        has_display = (
            os.environ.get('DISPLAY') or 
            sys.platform == 'win32' or 
            sys.platform == 'darwin'
        )
        
        if has_display:
            try:
                import tkinter
                root = tkinter.Tk()
                root.withdraw()
                root.destroy()
                
                print("✅ Interface graphique disponible!")
                from src.todo_gui import TodoApp
                app = TodoApp()
                app.run()
                return 0
                
            except Exception as gui_error:
                print(f"⚠️  GUI indisponible: {gui_error}")
        else:
            print("⚠️  Variable DISPLAY non définie")
        
        print("🔄 Lancement de la version console...")
        from console_app import TodoConsoleApp
        app = TodoConsoleApp()
        app.run()
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
