# common_functions.py

import subprocess
import sys
import logging
import win32gui
from pywinauto.application import Application
import tkinter as tk
from tkinter import ttk, Listbox, MULTIPLE

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_packages():
    required_packages = {
        "win32gui": "pywin32",
        "pywinauto": "pywinauto",
        "requests": "requests"
    }
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            logging.info(f"{module} não encontrado. Instalando {package}...")
            install(package)

def rename_windows(prefix="Ragnarok Origin Global"):
    ragnas = []
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if prefix in title:
            new_title = f"{hwnd} - {title}" if not title.startswith(str(hwnd)) else title
            win32gui.SetWindowText(hwnd, new_title)
            ragnas.append(new_title)

    win32gui.EnumWindows(callback, None)
    return ragnas

def send_key(window_title, key):
    target_window = win32gui.FindWindow(None, window_title)
    if target_window:
        win32gui.ShowWindow(target_window, 5)
        app = Application().connect(handle=target_window)
        window = app.window(handle=target_window)
        window.send_keystrokes(key)
        window.send_keystrokes(key)  # Enviando duas vezes para garantir
    else:
        logging.warning(f"Janela não encontrada: {window_title}")

class WindowManager:
    def __init__(self, master, save_callback):
        self.master = master
        self.ragnas = []
        self.listbox = None
        self.save_callback = save_callback

    def create_widgets(self):
        # Top frame para botões padrão
        top_frame = ttk.Frame(self.master)
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        top_frame.columnconfigure(0, weight=1)

        # Botões no canto superior direito
        self.btn_save = ttk.Button(top_frame, text="Salvar Config", command=self.save_callback)
        self.btn_save.grid(row=0, column=2, sticky="e")

        self.btn_rename = ttk.Button(top_frame, text="Renomear Janelas", command=self.renomear_janelas)
        self.btn_rename.grid(row=0, column=1, sticky="e", padx=(0, 5))

        # Label para "Janelas do Jogo"
        label = ttk.Label(self.master, text="Janelas do Jogo:", font=('Segoe UI', 9))
        label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="w")

        # Listbox para janelas
        self.listbox = Listbox(self.master, selectmode=MULTIPLE)
        self.listbox.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="nsew")

        # Configuração de expansão
        self.master.rowconfigure(2, weight=1)
        self.master.columnconfigure(0, weight=1)

    def renomear_janelas(self):
        self.ragnas = rename_windows()
        self.listar_janelas()

    def listar_janelas(self):
        self.listbox.delete(0, tk.END)
        for janela in self.ragnas:
            self.listbox.insert(tk.END, janela)

    def get_selected_windows(self):
        selected_indices = self.listbox.curselection()
        return [self.listbox.get(i) for i in selected_indices]


# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')