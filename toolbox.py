# toolbox.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import requests
import subprocess
from leveling.leveling_script import LevelingScript
from common_functions import check_and_install_packages

REPO_URL = "https://api.github.com/repos/seu_usuario/seu_repositorio"
VERSION_FILE = "version.txt"
EXECUTABLE_NAME = "toolbox.exe"

class Toolbox:
    def __init__(self, master):
        self.master = master
        master.title("Ragnarok Toolbox")
        master.geometry("600x650")

        # Definir o ícone da janela
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            master.iconbitmap(icon_path)
        else:
            print("Arquivo de ícone não encontrado.")

        self.current_version = self.get_local_version()
        self.check_for_updates()
        self.create_widgets()

    def create_widgets(self):
        # Configurar o grid do master
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Criar notebook (sistema de abas)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Aba para o script de Leveling
        leveling_frame = ttk.Frame(self.notebook)
        leveling_frame.columnconfigure(0, weight=1)
        leveling_frame.rowconfigure(0, weight=1)
        self.notebook.add(leveling_frame, text='Leveling')
        LevelingScript(leveling_frame)

        # Adicione mais abas aqui para outros scripts


        # Label para mostrar a versão atual
        self.version_label = tk.Label(self.master, text=f"Versão atual: {self.current_version}", 
                                      font=('Segoe UI', 8))
        self.version_label.grid(row=1, column=0, sticky="se", padx=5, pady=5)

    def check_for_updates(self):
        try:
            local_version = self.get_local_version()
            remote_version = self.get_remote_version()

            if remote_version > local_version:
                if messagebox.askyesno("Atualização Disponível", 
                                       f"Uma nova versão ({remote_version}) está disponível. Deseja atualizar?"):
                    self.update_files()
                    messagebox.showinfo("Atualização Concluída", 
                                        "O programa foi atualizado. Será reiniciado agora.")
                    self.restart_application()
        except Exception as e:
            print(f"Erro ao verificar atualizações: {e}")

    def get_local_version(self):
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return f.read().strip()
        return "0.0.0"

    def get_remote_version(self):
        response = requests.get(f"{REPO_URL}/contents/{VERSION_FILE}")
        if response.status_code == 200:
            content = response.json()
            file_content = requests.get(content["download_url"]).text
            return file_content.strip()
        return "0.0.0"

    def download_file(self, file_path):
        response = requests.get(f"{REPO_URL}/contents/{file_path}")
        if response.status_code == 200:
            content = response.json()
            file_content = requests.get(content["download_url"]).text
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(file_content)

    def update_files(self):
        files_to_update = ["toolbox.py", "leveling/leveling_script.py", "common_functions.py", VERSION_FILE]
        for file in files_to_update:
            self.download_file(file)

    def restart_application(self):
        if getattr(sys, 'frozen', False):
            # Se for um executável compilado
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Se for um script Python
            os.execv(sys.executable, [sys.executable] + sys.argv)

    def on_closing(self):
        # Implemente lógica de fechamento se necessário
        self.master.destroy()

def main():
    check_and_install_packages()
    root = tk.Tk()
    app = Toolbox(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()