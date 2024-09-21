# toolbox.py

import tkinter as tk
from tkinter import ttk
import os
from leveling.leveling_script import LevelingScript
# Importe outros scripts aqui conforme necessário

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
        # Exemplo:
        # farming_frame = ttk.Frame(self.notebook)
        # farming_frame.columnconfigure(0, weight=1)
        # farming_frame.rowconfigure(0, weight=1)
        # self.notebook.add(farming_frame, text='Farming')
        # FarmingScript(farming_frame)

    def on_closing(self):
        # Implemente lógica de fechamento se necessário
        self.master.destroy()

def main():
    root = tk.Tk()
    app = Toolbox(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()