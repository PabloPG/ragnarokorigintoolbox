# leveling/leveling_script.py

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import threading
import time
from datetime import datetime
import json

from common_functions import check_and_install_packages, send_key, WindowManager

class LevelingScript:
    def __init__(self, master):
        self.master = master
        
        self.running = False
        self.key_cooldowns = {}
        self.key_active = {}
        self.last_pressed = {}
        self.script_thread = None
        self.log_text = None
        self.custom_keys = [None, None]

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # Configuração de estilos
        style = ttk.Style()
        style.configure('TButton', padding=3, font=('Segoe UI', 8))
        style.configure('Green.TButton', background='#90EE90')
        style.configure('Start.TButton', background='#90EE90', padding=5, font=('Segoe UI', 9))
        style.configure('Stop.TButton', background='#FFB6C1', padding=5, font=('Segoe UI', 9))
        style.configure('TEntry', padding=2, font=('Segoe UI', 8))

        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # WindowManager
        self.window_manager = WindowManager(main_frame, self.save_settings)
        self.window_manager.create_widgets()

        # Frame centralizado para botões de teclas e inputs de tempo
        center_frame = ttk.Frame(main_frame)
        center_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        center_frame.columnconfigure(0, weight=1)
        center_frame.rowconfigure(0, weight=1)

        frame_keys = ttk.Frame(center_frame)
        frame_keys.grid(row=0, column=0)

        ttk.Label(frame_keys, text="Configuração de Teclas:", font=('Segoe UI', 9)).grid(row=0, column=0, columnspan=4, pady=(5, 10))

        self.key_buttons = {}
        self.cooldown_entries = {}
        for i in range(1, 7):
            key = str(i)
            row = (i - 1) // 2 + 1
            col = (i - 1) % 2 * 2
            
            btn = ttk.Button(frame_keys, text=f"Tecla {key}", command=lambda k=key: self.toggle_key(k), style='TButton', width=12)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.key_buttons[key] = btn
            
            cooldown_entry = ttk.Entry(frame_keys, width=6, style='TEntry')
            cooldown_entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew")
            cooldown_entry.insert(0, "0")
            self.cooldown_entries[key] = cooldown_entry
            
            self.key_active[key] = False

        # Botões para teclas customizáveis
        for i in range(2):
            custom_btn = ttk.Button(frame_keys, text=f"Custom {i+1}", command=lambda i=i: self.set_custom_key(i), style='TButton', width=12)
            custom_btn.grid(row=4, column=i*2, padx=5, pady=5, sticky="ew")
            setattr(self, f'custom_btn_{i}', custom_btn)
            cooldown_entry = ttk.Entry(frame_keys, width=6, style='TEntry')
            cooldown_entry.grid(row=4, column=i*2+1, padx=5, pady=5, sticky="ew")
            cooldown_entry.insert(0, "0")
            self.cooldown_entries[f'custom_{i}'] = cooldown_entry

        for i in range(5):
            frame_keys.rowconfigure(i, weight=1)
        for i in range(4):
            frame_keys.columnconfigure(i, weight=1)

        # Botão para iniciar/parar o script
        self.btn_start = ttk.Button(main_frame, text="Iniciar Script", command=self.toggle_script, style='Start.TButton', width=20)
        self.btn_start.grid(row=4, column=0, pady=10)

        # Área de logs
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, font=('Segoe UI', 8))
        self.log_text.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        main_frame.rowconfigure(3, weight=1)

    def set_custom_key(self, index):
        custom_btn = getattr(self, f'custom_btn_{index}')
        key = f'custom_{index}'

        if self.key_active.get(key, False):
            # Se a tecla já estiver ativa, desative-a
            self.key_active[key] = False
            custom_btn.configure(style='TButton')
            custom_btn.config(text=f"Custom {index+1}")
            self.custom_keys[index] = None
            self.log(f"Tecla customizada {index + 1} desativada")
        else:
            # Se a tecla estiver inativa, permita a seleção de uma nova tecla
            new_key = simpledialog.askstring("Tecla Customizável", f"Digite a tecla customizada {index + 1}:")
            if new_key:
                self.custom_keys[index] = new_key
                custom_btn.config(text=f"Custom {index+1}: {new_key}")
                self.key_active[key] = True
                custom_btn.configure(style='Green.TButton')
                self.log(f"Tecla customizável {index + 1} definida como: {new_key}")

    def toggle_key(self, key):
        self.key_active[key] = not self.key_active[key]
        if self.key_active[key]:
            self.key_buttons[key].configure(style='Green.TButton')
        else:
            self.key_buttons[key].configure(style='TButton')
        self.log(f"Tecla {key} {'ativada' if self.key_active[key] else 'desativada'}")

    def save_settings(self):
        settings = {
            'cooldowns': {key: entry.get() for key, entry in self.cooldown_entries.items()},
            'active_keys': self.key_active,
            'custom_keys': self.custom_keys
        }
        with open('leveling_settings.json', 'w') as f:
            json.dump(settings, f)
        self.log("Configurações salvas.")

    def load_settings(self):
        try:
            with open('leveling_settings.json', 'r') as f:
                settings = json.load(f)
            for key, cooldown in settings['cooldowns'].items():
                if key in self.cooldown_entries:
                    self.cooldown_entries[key].delete(0, tk.END)
                    self.cooldown_entries[key].insert(0, cooldown)
            for key, active in settings['active_keys'].items():
                if key in self.key_buttons:
                    self.key_active[key] = active
                    if active:
                        self.key_buttons[key].configure(style='Green.TButton')
            self.custom_keys = settings.get('custom_keys', [None, None])
            for i, key in enumerate(self.custom_keys):
                if key:
                    custom_btn = getattr(self, f'custom_btn_{i}')
                    custom_btn.config(text=f"Custom {i+1}: {key}")
                    self.key_active[f'custom_{i}'] = True
                    custom_btn.configure(style='Green.TButton')
            self.log("Configurações carregadas.")
        except FileNotFoundError:
            self.log("Arquivo de configurações não encontrado. Usando padrões.")

    def toggle_script(self):
        if not self.running:
            selected_windows = self.window_manager.get_selected_windows()
            if not selected_windows:
                messagebox.showwarning("Nenhuma Janela Selecionada", 
                                       "Por favor, selecione pelo menos uma janela do jogo antes de iniciar o script.")
                return

            self.start_script()
        else:
            self.stop_script()

    def start_script(self):
        self.running = True
        self.btn_start.configure(text="Parar Script", style='Stop.TButton')
        selected_windows = self.window_manager.get_selected_windows()
        self.last_pressed = {key: 0 for key in self.key_active}

        # Atualizar cooldowns
        for key, entry in self.cooldown_entries.items():
            try:
                self.key_cooldowns[key] = float(entry.get())
            except ValueError:
                self.log(f"Valor inválido para tecla {key}. Usando 0 como padrão.")
                self.key_cooldowns[key] = 0

        def loop_script():
            while self.running:
                current_time = time.time()
                for window in selected_windows:
                    for key in self.key_active:
                        if self.key_active[key] and (current_time - self.last_pressed.get(key, 0)) >= self.key_cooldowns.get(key, 0):
                            if key.startswith('custom_'):
                                custom_key = self.custom_keys[int(key[-1])]
                                if custom_key:
                                    send_key(window, custom_key)
                                    self.log(f"Tecla {custom_key} pressionada em {window}")
                            else:
                                send_key(window, key)
                                self.log(f"Tecla {key} pressionada em {window}")

                            self.last_pressed[key] = current_time

                time.sleep(0.1)

        self.script_thread = threading.Thread(target=loop_script)
        self.script_thread.start()
        self.log("Script iniciado.")

    def stop_script(self):
        self.running = False
        self.btn_start.configure(text="Iniciar Script", style='Start.TButton')
        if self.script_thread:
            self.script_thread.join()
        self.log("Script parado.")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

    def on_closing(self):
        if self.running:
            self.stop_script()

# Não é necessário um bloco if __name__ == "__main__": aqui, pois este script será importado pelo toolbox.py