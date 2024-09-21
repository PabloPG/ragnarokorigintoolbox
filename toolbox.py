# toolbox.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import requests
import subprocess
import time
from leveling.leveling_script import LevelingScript
from common_functions import check_and_install_packages

REPO_URL = "https://api.github.com/repos/PabloPG/ragnarokorigintoolbox"
VERSION_FILE = "version.txt"
EXECUTABLE_NAME = "Ragnarok Toolbox.exe"

class UpdateLoader(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Atualizando...")
        self.geometry("300x100")
        self.progress = ttk.Progressbar(self, length=250, mode='indeterminate')
        self.progress.pack(pady=20)
        self.label = tk.Label(self, text="Baixando atualizações...")
        self.label.pack()
        self.progress.start()

class Toolbox:
    def __init__(self, master):
        self.master = master
        master.title("Ragnarok Toolbox")
        master.geometry("600x650")

        self.base_path = self.get_base_path()
        
        # Definir o ícone da janela
        icon_path = os.path.join(self.base_path, "icon.ico")
        if os.path.exists(icon_path):
            master.iconbitmap(icon_path)
        else:
            print(f"Arquivo de ícone não encontrado em: {icon_path}")

        self.current_version = self.get_local_version()
        self.check_for_updates()
        self.create_widgets()

    def get_base_path(self):
        if getattr(sys, 'frozen', False):
            # Se estiver rodando como executável compilado
            return os.path.dirname(sys.executable)
        else:
            # Se estiver rodando como script
            return os.path.dirname(os.path.abspath(__file__))

    def create_widgets(self):
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        leveling_frame = ttk.Frame(self.notebook)
        leveling_frame.columnconfigure(0, weight=1)
        leveling_frame.rowconfigure(0, weight=1)
        self.notebook.add(leveling_frame, text='Leveling')
        LevelingScript(leveling_frame)

        self.version_label = tk.Label(self.master, text=f"Versão atual: {self.current_version}", 
                                      font=('Segoe UI', 8))
        self.version_label.grid(row=1, column=0, sticky="se", padx=5, pady=5)

    def check_for_updates(self):
        try:
            remote_version = self.get_remote_version()
            if remote_version > self.current_version:
                if messagebox.askyesno("Atualização Disponível", 
                                       f"Uma nova versão ({remote_version}) está disponível. Deseja atualizar?"):
                    self.update_files(remote_version)
        except Exception as e:
            print(f"Erro ao verificar atualizações: {e}")
            messagebox.showerror("Erro", f"Não foi possível verificar atualizações: {e}")

    def get_local_version(self):
        version_path = os.path.join(self.base_path, VERSION_FILE)
        try:
            if os.path.exists(version_path):
                with open(version_path, "r") as f:
                    version = f.read().strip()
                    print(f"Versão local lida: {version}")
                    return version
            else:
                print(f"Arquivo de versão não encontrado: {version_path}")
        except Exception as e:
            print(f"Erro ao ler versão local: {e}")
        return "0.0.0"

    def get_remote_version(self):
        try:
            response = requests.get(f"{REPO_URL}/contents/{VERSION_FILE}")
            if response.status_code == 200:
                content = response.json()
                file_content = requests.get(content["download_url"]).text
                return file_content.strip()
            else:
                print(f"Falha ao obter versão remota. Status code: {response.status_code}")
        except Exception as e:
            print(f"Erro ao obter versão remota: {e}")
        return "0.0.0"

    def download_file(self, file_path):
        try:
            response = requests.get(f"{REPO_URL}/contents/{file_path}")
            if response.status_code == 200:
                content = response.json()
                file_content = requests.get(content["download_url"]).text
                local_path = os.path.join(self.base_path, file_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "w", encoding='utf-8') as f:
                    f.write(file_content)
                print(f"Arquivo baixado com sucesso: {local_path}")
            else:
                print(f"Falha ao baixar {file_path}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Erro ao baixar {file_path}: {e}")
            raise

    def update_files(self, new_version):
        loader = UpdateLoader(self.master)
        self.master.update()
        try:
            files_to_update = ["toolbox.py", "leveling/leveling_script.py", "common_functions.py", VERSION_FILE]
            for file in files_to_update:
                self.download_file(file)
            
            # Atualizar a versão local
            version_path = os.path.join(self.base_path, VERSION_FILE)
            with open(version_path, "w") as f:
                f.write(new_version)

            loader.destroy()
            messagebox.showinfo("Atualização Concluída", 
                                "O programa foi atualizado. Será reiniciado agora.")
            self.restart_application()
        except Exception as e:
            loader.destroy()
            print(f"Erro durante a atualização: {e}")
            messagebox.showerror("Erro de Atualização", f"Ocorreu um erro durante a atualização: {e}")

    def restart_application(self):
        if getattr(sys, 'frozen', False):
            # Se for um executável compilado
            os.execl(sys.executable, f'"{sys.executable}"', *sys.argv)
        else:
            # Se for um script Python
            os.execl(sys.executable, sys.executable, *sys.argv)

    def on_closing(self):
        self.master.destroy()

def main():
    check_and_install_packages()
    root = tk.Tk()
    app = Toolbox(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()