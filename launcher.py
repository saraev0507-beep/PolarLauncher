import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import json
import os
import subprocess
import requests
import threading
import webbrowser
import random
import smtplib
from email.mime.text import MIMEText
from PIL import Image, ImageTk
from datetime import datetime, timedelta

# ========== ПОЧТОВЫЕ НАСТРОЙКИ ==========
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
EMAIL_LOGIN = "polar.ras@mail.ru"
EMAIL_PASSWORD = "D6uTw5D3HHtIkg04l5J5"

# ========== НАСТРОЙКИ ==========
VERSION = "4.2"
NEWS_URL = "https://max.ru/join/K_eJ9US4BIDMHpIZhPphgAvZZLrG383huYJ2rPIkcaI"
HELP_URL = "https://max.ru/u/f9LHodD0cOIAqDjpESaD9ltaViCsfAuNTDuMgHMDMKR48CM4BKVq9j_B-pk"

THEMES = {
    "Фиолетовая": {"bg": "#0d0a1a", "card_bg": "#1a1338", "accent": "#b87cff", "text": "#ffffff", "glow": "#d9a7ff"},
    "Красная": {"bg": "#1a0a0a", "card_bg": "#2a1010", "accent": "#ff4444", "text": "#ffffff", "glow": "#ff8888"},
    "Тёмная": {"bg": "#121212", "card_bg": "#1e1e1e", "accent": "#6c6c8a", "text": "#cccccc", "glow": "#8a8aa8"}
}

CHEATS = {
    "Wurst 1.19.4": {"url": "https://github.com/Wurst-Imperium/Wurst7/releases/download/v7.35.1/wurst-7.35.1-mc1.19.4.jar", "file": "wurst.jar"},
    "Meteor 1.19.4": {"url": "https://github.com/MeteorDevelopment/meteor-client/releases/download/0.5.4/meteor-client-0.5.4-1.19.4.jar", "file": "meteor.jar"}
}

class PolarLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POLAR LAUNCHER")
        self.root.geometry("1300x750")
        self.root.resizable(True, True)
        self.root.bind("<F12>", self.toggle_fullscreen)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.fullscreen = False
        self.right_panel_visible = True
        self.current_theme = "Фиолетовая"
        self.is_admin = False
        self.users_file = "users.json"
        self.friends_file = "friends.json"
        self.bans_file = "bans.json"
        self.settings_file = "settings.json"
        self.skin_image = None
        self.current_skin_path = None
        self.temp_2fa_code = None
        self.pending_2fa_user = None
        self.temp_code = None
        
        self.load_user_data()
        self.load_friends()
        self.load_bans()
        self.load_settings()
        self.create_widgets()
        self.apply_theme()
    
    def load_user_data(self):
        if os.path.exists(self.users_file) and os.path.getsize(self.users_file) > 0:
            try:
                with open(self.users_file, "r", encoding='utf-8') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        else:
            self.users = {}
        
        if "Admin" not in self.users:
            self.users["Admin"] = {
                "display_name": "Admin",
                "password": "050714",
                "email": EMAIL_LOGIN,
                "email_verified": True,
                "admin": True
            }
            self.save_user_data()
        self.current_user = None
    
    def save_user_data(self):
        with open(self.users_file, "w", encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
    
    def load_friends(self):
        if os.path.exists(self.friends_file):
            with open(self.friends_file, "r", encoding='utf-8') as f:
                self.friends = json.load(f)
        else:
            self.friends = {}
    
    def save_friends(self):
        with open(self.friends_file, "w", encoding='utf-8') as f:
            json.dump(self.friends, f, ensure_ascii=False, indent=4)
    
    def load_bans(self):
        if os.path.exists(self.bans_file):
            with open(self.bans_file, "r", encoding='utf-8') as f:
                self.bans = json.load(f)
        else:
            self.bans = {}
    
    def save_bans(self):
        with open(self.bans_file, "w", encoding='utf-8') as f:
            json.dump(self.bans, f, ensure_ascii=False, indent=4)
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("theme", "Фиолетовая")
            except:
                self.current_theme = "Фиолетовая"
        else:
            self.current_theme = "Фиолетовая"
    
    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding='utf-8') as f:
                json.dump({"theme": self.current_theme}, f, ensure_ascii=False, indent=4)
        except:
            pass
    
    def is_banned(self, username):
        if username in self.bans:
            ban_data = self.bans[username]
            expiry = datetime.fromisoformat(ban_data["expiry"])
            if datetime.now() < expiry:
                return True, ban_data
            else:
                del self.bans[username]
                self.save_bans()
        return False, None
    
    def send_2fa_code(self, email):
        code = str(random.randint(100000, 999999))
        self.temp_2fa_code = code
        msg = MIMEText(f"Ваш код подтверждения для входа в POLAR LAUNCHER: {code}\nНикому не сообщайте этот код!")
        msg["Subject"] = "Код подтверждения входа"
        msg["From"] = EMAIL_LOGIN
        msg["To"] = email
        def send():
            try:
                with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                    server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                print(f"Ошибка отправки 2FA: {e}")
        threading.Thread(target=send).start()
        return code
    
    def send_verification_code(self, email):
        code = str(random.randint(100000, 999999))
        self.temp_code = code
        msg = MIMEText(f"Ваш код подтверждения для POLAR LAUNCHER: {code}\nНикому не сообщайте этот код!")
        msg["Subject"] = "Подтверждение email"
        msg["From"] = EMAIL_LOGIN
        msg["To"] = email
        def send():
            try:
                with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                    server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                print(f"Ошибка: {e}")
        threading.Thread(target=send).start()
    
    def send_mass_mail(self, subject, message):
        recipients = []
        for user, data in self.users.items():
            if data.get("email") and data.get("email_verified"):
                recipients.append(data["email"])
        if not recipients:
            self.log_console("❌ Нет пользователей с подтверждённой почтой")
            return
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_LOGIN
        def send():
            try:
                with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                    server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
                    for email in recipients:
                        msg["To"] = email
                        server.send_message(msg)
                self.log_console(f"✅ Рассылка отправлена {len(recipients)} пользователям")
            except Exception as e:
                self.log_console(f"❌ Ошибка рассылки: {e}")
        threading.Thread(target=send).start()
    
    def apply_theme(self):
        theme = THEMES[self.current_theme]
        self.root.configure(bg=theme["bg"])
        self.save_settings()
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
    
    def create_widgets(self):
        theme = THEMES[self.current_theme]
        for widget in self.root.winfo_children():
            widget.destroy()
        
        top_frame = tk.Frame(self.root, bg=theme["bg"], height=45)
        top_frame.pack(fill="x", pady=5)
        tk.Label(top_frame, text="💬 ЧАТ: СКОРО БУДЕТ", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["accent"]).pack(side="left", padx=20)
        self.online_label = tk.Label(top_frame, text=f"👥 ОНЛАЙН: {random.randint(8, 30)}", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["accent"])
        self.online_label.pack(side="right", padx=20)
        
        left_frame = tk.Frame(self.root, bg=theme["bg"], width=220)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        tabs = {}
        if self.current_user:
            tabs = {
                "🎮 ИГРА": self.show_game_tab,
                "👥 ДРУЗЬЯ": self.show_friends_tab,
                "⚙️ НАСТРОЙКИ": self.show_settings_tab,
                "👤 ПРОФИЛЬ": self.show_profile_tab,
                "❓ ПОМОЩЬ": self.show_help_tab
            }
            if self.is_admin:
                tabs["🖥️ КОНСОЛЬ"] = self.show_console_tab
        else:
            tabs = {
                "🔐 ВХОД / РЕГИСТРАЦИЯ": self.open_login_window,
                "❓ ПОМОЩЬ": self.show_help_tab
            }
        
        for tab_name, command in tabs.items():
            btn = tk.Button(left_frame, text=tab_name, font=("Arial", 12), bg=theme["card_bg"], fg=theme["text"], relief="flat", padx=20, pady=12, anchor="w", command=command)
            btn.pack(fill="x", pady=3)
        
        self.center_frame = tk.Frame(self.root, bg=theme["card_bg"], relief="ridge", bd=2)
        self.center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        if self.current_user:
            self.show_main_screen()
        else:
            self.show_help_tab()
        
        self.right_container = tk.Frame(self.root, bg=theme["bg"])
        self.right_container.pack(side="right", fill="y", padx=(0,10), pady=10)
        self.toggle_btn = tk.Button(self.right_container, text="◀", command=self.toggle_right_panel, bg=theme["accent"], fg="white", font=("Arial", 10, "bold"), width=3)
        self.toggle_btn.pack(side="left", fill="y")
        self.right_panel = tk.Frame(self.right_container, bg=theme["card_bg"], width=300)
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)
        tk.Label(self.right_panel, text="📦 ДОСТУПНЫЕ ЧИТЫ", font=("Arial", 14, "bold"), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=10)
        self.cheat_listbox = tk.Listbox(self.right_panel, bg="#2a1a4a", fg="white", selectbackground=theme["accent"], font=("Consolas", 11), height=6)
        self.cheat_listbox.pack(padx=10, pady=5, fill="both", expand=True)
        for cheat in CHEATS:
            self.cheat_listbox.insert(tk.END, cheat)
        tk.Button(self.right_panel, text="📥 УСТАНОВИТЬ ЧИТ", command=self.install_cheat, bg=theme["accent"], fg="white", font=("Arial", 10, "bold")).pack(pady=5, padx=10, fill="x")
        tk.Button(self.right_panel, text="📂 ОТКРЫТЬ MODS", command=self.open_mods, bg=theme["accent"], fg="white", font=("Arial", 10, "bold")).pack(pady=5, padx=10, fill="x")
        
        bottom_frame = tk.Frame(self.root, bg=theme["bg"], height=60)
        bottom_frame.pack(side="bottom", fill="x")
        if self.current_user:
            display_name = self.users.get(self.current_user, {}).get("display_name", self.current_user)
            self.login_btn = tk.Button(bottom_frame, text=f"👤 {display_name}", command=self.open_login_window, bg=theme["card_bg"], fg=theme["text"], font=("Arial", 10, "bold"))
        else:
            self.login_btn = tk.Button(bottom_frame, text="👤 ВОЙТИ В ПРОФИЛЬ", command=self.open_login_window, bg=theme["card_bg"], fg=theme["text"], font=("Arial", 10, "bold"))
        self.login_btn.pack(side="left", padx=20, pady=10)
        self.status_label = tk.Label(bottom_frame, text="✅ ГОТОВ", bg=theme["bg"], fg=theme["accent"], font=("Arial", 9))
        self.status_label.pack(side="right", padx=20)
    
    def toggle_right_panel(self):
        self.right_panel_visible = not self.right_panel_visible
        if self.right_panel_visible:
            self.right_panel.pack(side="right", fill="y")
            self.toggle_btn.config(text="▶")
        else:
            self.right_panel.pack_forget()
            self.toggle_btn.config(text="◀")
    
    def show_main_screen(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        self.steve_label = tk.Label(self.center_frame, text="🧱", font=("Arial", 100), bg=theme["card_bg"], fg=theme["glow"])
        self.steve_label.pack(pady=20)
        self.steve_label.bind("<Button-1>", lambda e: messagebox.showinfo("Стив", "Смена скина будет доступна в версии 3.5!"))
        tk.Label(self.center_frame, text="POLAR LAUNCHER", font=("Impact", 48), bg=theme["card_bg"], fg=theme["accent"]).pack()
        if self.current_user:
            display_name = self.users.get(self.current_user, {}).get("display_name", self.current_user)
            tk.Label(self.center_frame, text=f"Добро пожаловать, {display_name}!", font=("Arial", 16), bg=theme["card_bg"], fg=theme["text"]).pack(pady=10)
            tk.Label(self.center_frame, text=f"@{self.current_user}", font=("Arial", 12), bg=theme["card_bg"], fg=theme["accent"]).pack()
        
        news_frame = tk.Frame(self.center_frame, bg=theme["bg"], relief="groove", bd=2)
        news_frame.pack(fill="x", padx=50, pady=20)
        tk.Label(news_frame, text="📰 НОВОСТИ", font=("Arial", 14, "bold"), bg=theme["bg"], fg=theme["accent"]).pack(pady=5)
        news_text = tk.Text(news_frame, height=4, bg=theme["bg"], fg=theme["text"], wrap="word", font=("Arial", 10))
        news_text.pack(fill="x", padx=10, pady=5)
        news_text.insert("1.0", "✅ POLAR LAUNCHER v4.2\n✅ Привязка почты\n✅ 2FA при входе\n✅ Рассылки через консоль\n✅ Админ-меню")
        news_text.config(state="disabled")
    
    def show_game_tab(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        tk.Label(self.center_frame, text="🎮 ИГРА", font=("Impact", 36), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=30)
        launch_btn = tk.Button(self.center_frame, text="🚀 ЗАПУСТИТЬ ИГРУ", command=self.launch_game, bg=theme["accent"], fg="white", font=("Arial", 16, "bold"))
        launch_btn.pack(pady=20)
    
    def show_settings_tab(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        tk.Label(self.center_frame, text="⚙️ НАСТРОЙКИ", font=("Impact", 36), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=30)
        
        tk.Label(self.center_frame, text="Тема:", bg=theme["card_bg"], fg=theme["text"], font=("Arial", 12)).pack()
        theme_var = tk.StringVar(value=self.current_theme)
        theme_menu = ttk.Combobox(self.center_frame, textvariable=theme_var, values=list(THEMES.keys()), state="readonly")
        theme_menu.pack(pady=5)
        theme_menu.bind("<<ComboboxSelected>>", lambda e: self.change_theme(theme_var.get()))
        
        # Привязка почты
        tk.Label(self.center_frame, text="📧 ПРИВЯЗКА ПОЧТЫ", font=("Arial", 14, "bold"), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=(20,5))
        email_frame = tk.Frame(self.center_frame, bg=theme["card_bg"])
        email_frame.pack(pady=5)
        self.email_entry = tk.Entry(email_frame, bg=theme["bg"], fg=theme["text"], width=30)
        self.email_entry.pack(side="left", padx=5)
        tk.Button(email_frame, text="ОТПРАВИТЬ КОД", command=self.send_code_for_email, bg=theme["accent"], fg="white").pack(side="left")
        code_frame = tk.Frame(self.center_frame, bg=theme["card_bg"])
        code_frame.pack(pady=5)
        self.code_entry = tk.Entry(code_frame, bg=theme["bg"], fg=theme["text"], width=20)
        self.code_entry.pack(side="left", padx=5)
        tk.Button(code_frame, text="ПОДТВЕРДИТЬ", command=self.verify_email_code, bg=theme["accent"], fg="white").pack(side="left")
        
        # Смена пароля
        tk.Label(self.center_frame, text="🔐 СМЕНА ПАРОЛЯ", font=("Arial", 14, "bold"), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=(20,5))
        old_pass = tk.Entry(self.center_frame, show="*", bg=theme["bg"], fg=theme["text"], width=20)
        old_pass.pack(pady=5)
        new_pass = tk.Entry(self.center_frame, show="*", bg=theme["bg"], fg=theme["text"], width=20)
        new_pass.pack(pady=5)
        def change_password():
            if self.current_user and self.users[self.current_user].get("password") == old_pass.get():
                self.users[self.current_user]["password"] = new_pass.get()
                self.save_user_data()
                self.status_label.config(text="✅ Пароль изменён!")
                messagebox.showinfo("Успех", "Пароль успешно изменён!")
            else:
                messagebox.showerror("Ошибка", "Неверный старый пароль!")
        tk.Button(self.center_frame, text="СМЕНИТЬ ПАРОЛЬ", command=change_password, bg=theme["accent"], fg="white").pack(pady=5)
    
    def send_code_for_email(self):
        email = self.email_entry.get()
        if "@" not in email or "." not in email:
            messagebox.showerror("Ошибка", "Неверный формат email!")
            return
        self.send_verification_code(email)
        messagebox.showinfo("Код отправлен", f"Код подтверждения отправлен на {email}")
    
    def verify_email_code(self):
        if self.code_entry.get() == self.temp_code:
            email = self.email_entry.get()
            self.users[self.current_user]["email"] = email
            self.users[self.current_user]["email_verified"] = True
            self.save_user_data()
            self.status_label.config(text=f"✅ Email {email} подтверждён!")
            messagebox.showinfo("Успех", "Email успешно привязан и подтверждён!")
        else:
            messagebox.showerror("Ошибка", "Неверный код!")
    
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()
        self.create_widgets()
        self.status_label.config(text=f"✅ Тема изменена на {theme_name}")
    
    def show_profile_tab(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        
        if self.current_user:
            user_data = self.users.get(self.current_user, {"display_name": self.current_user})
            tk.Label(self.center_frame, text="👤 ПРОФИЛЬ", font=("Impact", 36), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=20)
            
            if self.skin_image:
                skin_label = tk.Label(self.center_frame, image=self.skin_image, bg=theme["card_bg"])
                skin_label.pack(pady=10)
            tk.Button(self.center_frame, text="📸 ЗАГРУЗИТЬ СКИН", command=self.load_skin, bg=theme["accent"], fg="white", font=("Arial", 10, "bold")).pack(pady=5)
            
            fields_frame = tk.Frame(self.center_frame, bg=theme["card_bg"])
            fields_frame.pack(pady=10)
            
            tk.Label(fields_frame, text="Отображаемое имя:", bg=theme["card_bg"], fg=theme["text"]).grid(row=0, column=0, padx=5, pady=5, sticky="e")
            name_entry = tk.Entry(fields_frame, bg=theme["bg"], fg=theme["text"], insertbackground=theme["text"])
            name_entry.grid(row=0, column=1, padx=5, pady=5)
            name_entry.insert(0, user_data.get("display_name", self.current_user))
            
            tk.Label(fields_frame, text="Юзернейм:", bg=theme["card_bg"], fg=theme["text"]).grid(row=1, column=0, padx=5, pady=5, sticky="e")
            tk.Label(fields_frame, text=f"@{self.current_user}", bg=theme["card_bg"], fg=theme["accent"]).grid(row=1, column=1, padx=5, pady=5, sticky="w")
            
            tk.Label(fields_frame, text="Email:", bg=theme["card_bg"], fg=theme["text"]).grid(row=2, column=0, padx=5, pady=5, sticky="e")
            email_text = user_data.get("email", "Не привязан")
            if user_data.get("email_verified"):
                email_text += " ✓"
            tk.Label(fields_frame, text=email_text, bg=theme["card_bg"], fg=theme["text"]).grid(row=2, column=1, padx=5, pady=5, sticky="w")
            
            if self.current_user == "Admin":
                tk.Label(self.center_frame, text="👑 АДМИНИСТРАТОР", font=("Arial", 12, "bold"), bg=theme["card_bg"], fg="gold").pack(pady=5)
            
            def save_profile():
                self.users[self.current_user]["display_name"] = name_entry.get()
                self.save_user_data()
                self.status_label.config(text="✅ Профиль сохранён!")
                messagebox.showinfo("Успех", "Данные профиля обновлены!")
            
            tk.Button(self.center_frame, text="💾 СОХРАНИТЬ ПРОФИЛЬ", command=save_profile, bg=theme["accent"], fg="white", font=("Arial", 10, "bold")).pack(pady=10)
            tk.Button(self.center_frame, text="🚪 ВЫЙТИ ИЗ ПРОФИЛЯ", command=self.logout, bg="red", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        else:
            tk.Label(self.center_frame, text="❌ Вы не авторизованы", font=("Arial", 16), bg=theme["card_bg"], fg="red").pack(pady=30)
            tk.Button(self.center_frame, text="ВОЙТИ / ЗАРЕГИСТРИРОВАТЬСЯ", command=self.open_login_window, bg=theme["accent"], fg="white", font=("Arial", 12, "bold")).pack(pady=20)
    
    def load_skin(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.current_skin_path = file_path
            img = Image.open(file_path)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            self.skin_image = ImageTk.PhotoImage(img)
            self.status_label.config(text="✅ Скин загружен!")
            self.show_profile_tab()
    
    def show_friends_tab(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        tk.Label(self.center_frame, text="👥 ДРУЗЬЯ", font=("Impact", 36), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=20)
        
        if not self.current_user:
            tk.Label(self.center_frame, text="❌ Войдите в профиль, чтобы видеть друзей", font=("Arial", 14), bg=theme["card_bg"], fg="red").pack(pady=30)
            return
        
        friends_list = tk.Listbox(self.center_frame, bg=theme["bg"], fg=theme["text"], selectbackground=theme["accent"], font=("Arial", 12), height=10)
        friends_list.pack(padx=20, pady=10, fill="both", expand=True)
        
        user_friends = self.friends.get(self.current_user, [])
        for friend in user_friends:
            friends_list.insert(tk.END, friend)
        
        def show_context_menu(event):
            selected = friends_list.curselection()
            if not selected:
                return
            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="💬 Написать", command=lambda: messagebox.showinfo("Чат", "Чат будет в v5.0"))
            menu.add_command(label="🔇 Замутить", command=lambda: messagebox.showinfo("Мут", f"Игрок {friends_list.get(selected[0])} замучен на 30 дней"))
            menu.add_command(label="🚫 Заблокировать", command=lambda: messagebox.showinfo("Блок", f"Игрок {friends_list.get(selected[0])} заблокирован"))
            menu.post(event.x_root, event.y_root)
        
        friends_list.bind("<Button-3>", show_context_menu)
        
        def add_friend():
            dialog = tk.Toplevel(self.root)
            dialog.title("Добавить друга")
            dialog.geometry("300x150")
            dialog.configure(bg=theme["bg"])
            tk.Label(dialog, text="Юзернейм друга (с @):", bg=theme["bg"], fg=theme["text"]).pack(pady=10)
            entry = tk.Entry(dialog, bg=theme["card_bg"], fg=theme["text"])
            entry.pack(pady=5)
            def add():
                friend_name = entry.get().lstrip('@')
                if friend_name == self.current_user:
                    messagebox.showerror("Ошибка", "Нельзя добавить самого себя в друзья!")
                    return
                if friend_name and friend_name not in user_friends and friend_name in self.users:
                    user_friends.append(friend_name)
                    self.friends[self.current_user] = user_friends
                    self.save_friends()
                    friends_list.insert(tk.END, friend_name)
                    dialog.destroy()
                    self.status_label.config(text=f"✅ {friend_name} добавлен в друзья!")
                else:
                    messagebox.showerror("Ошибка", "Пользователь не найден или уже в друзьях!")
            tk.Button(dialog, text="Добавить", command=add, bg=theme["accent"], fg="white").pack(pady=10)
        
        tk.Button(self.center_frame, text="➕ ДОБАВИТЬ ДРУГА", command=add_friend, bg=theme["accent"], fg="white", font=("Arial", 12, "bold")).pack(pady=10)
    
    def show_help_tab(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        tk.Label(self.center_frame, text="❓ ПОМОЩЬ", font=("Impact", 36), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=30)
        tk.Label(self.center_frame, text="Нужна помощь? Напиши в наш чат поддержки!", font=("Arial", 14), bg=theme["card_bg"], fg=theme["text"]).pack(pady=10)
        tk.Button(self.center_frame, text="💬 ОТКРЫТЬ ЧАТ ПОДДЕРЖКИ", command=lambda: webbrowser.open(HELP_URL), bg=theme["accent"], fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        
        # Крестики-нолики с ботом
        tk.Label(self.center_frame, text="🎮 КРЕСТИКИ-НОЛИКИ (с ботом)", font=("Arial", 14, "bold"), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=20)
        self.board = [""] * 9
        self.buttons = []
        game_frame = tk.Frame(self.center_frame, bg=theme["card_bg"])
        game_frame.pack()
        for i in range(9):
            btn = tk.Button(game_frame, text="", font=("Arial", 20), width=4, height=2,
                           command=lambda i=i: self.player_move(i))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)
        
        def reset_game():
            self.board = [""] * 9
            for btn in self.buttons:
                btn.config(text="", state="normal")
            self.status_label.config(text="✅ Новая игра!")
        tk.Button(self.center_frame, text="🔄 ПЕРЕЗАГРУЗИТЬ РАУНД", command=reset_game, bg=theme["accent"], fg="white", font=("Arial", 10, "bold")).pack(pady=10)
    
    def player_move(self, pos):
        if self.board[pos] == "":
            self.board[pos] = "X"
            self.buttons[pos].config(text="X", state="disabled")
            if self.check_winner("X"):
                messagebox.showinfo("Победа!", "Вы выиграли!")
                self.reset_game()
                return
            if "" not in self.board:
                messagebox.showinfo("Ничья", "Ничья!")
                self.reset_game()
                return
            self.bot_move()
    
    def bot_move(self):
        empty = [i for i, val in enumerate(self.board) if val == ""]
        if empty:
            pos = random.choice(empty)
            self.board[pos] = "O"
            self.buttons[pos].config(text="O", state="disabled")
            if self.check_winner("O"):
                messagebox.showinfo("Поражение", "Бот выиграл!")
                self.reset_game()
            elif "" not in self.board:
                messagebox.showinfo("Ничья", "Ничья!")
                self.reset_game()
    
    def check_winner(self, player):
        win_combinations = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a,b,c in win_combinations:
            if self.board[a] == self.board[b] == self.board[c] == player:
                return True
        return False
    
    def reset_game(self):
        self.board = [""] * 9
        for btn in self.buttons:
            btn.config(text="", state="normal")
    
    def show_console_tab(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
        theme = THEMES[self.current_theme]
        tk.Label(self.center_frame, text="🖥️ КОНСОЛЬ АДМИНИСТРАТОРА", font=("Impact", 24), bg=theme["card_bg"], fg=theme["accent"]).pack(pady=20)
        self.console_output = tk.Text(self.center_frame, bg="black", fg="lime", font=("Consolas", 10), height=15, state="normal")
        self.console_output.pack(padx=20, pady=10, fill="both", expand=True)
        cmd_frame = tk.Frame(self.center_frame, bg=theme["card_bg"])
        cmd_frame.pack(pady=10, fill="x", padx=20)
        self.cmd_input = tk.Entry(cmd_frame, bg=theme["bg"], fg=theme["text"], insertbackground=theme["text"], font=("Consolas", 12))
        self.cmd_input.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.cmd_input.bind("<Return>", self.execute_command)
        tk.Button(cmd_frame, text="ВЫПОЛНИТЬ", command=lambda: self.execute_command(None), bg=theme["accent"], fg="white").pack(side="right")
        self.log_console("POLAR ADMIN CONSOLE v4.2")
        self.log_console("Доступные команды: /help, /ban, /unban, /kick, /mute, /unmute, /op, /deop, /mail, /clear, /whoami, /list_users, /delete_user, /broadcast")
    
    def log_console(self, text):
        self.console_output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.console_output.see(tk.END)
    
    def execute_command(self, event):
        cmd = self.cmd_input.get().strip()
        if not cmd:
            return
        self.cmd_input.delete(0, tk.END)
        
        if cmd == "/help":
            self.log_console("POLAR ADMIN CONSOLE - КОМАНДЫ:")
            self.log_console("  /ban [ник] [причина] [число][д/м/г/н] - забанить")
            self.log_console("  /unban [ник] - разбанить")
            self.log_console("  /kick [ник] - кикнуть")
            self.log_console("  /mute [ник] [минуты] - замутить")
            self.log_console("  /unmute [ник] - размутить")
            self.log_console("  /op [ник] - выдать права админа")
            self.log_console("  /deop [ник] - снять права админа")
            self.log_console("  /mail [тема] | [сообщение] - массовая рассылка")
            self.log_console("  /clear - очистить консоль")
            self.log_console("  /whoami - информация о себе")
            self.log_console("  /list_users - список пользователей")
            self.log_console("  /delete_user [ник] - удалить пользователя")
            self.log_console("  /broadcast [сообщение] - отправить всем")
        
        elif cmd.startswith("/mail"):
            parts = cmd[5:].strip().split("|")
            if len(parts) >= 2:
                subject = parts[0].strip()
                message = parts[1].strip()
                self.send_mass_mail(subject, message)
            else:
                self.log_console("❌ Использование: /mail [тема] | [сообщение]")
        
        elif cmd.startswith("/ban"):
            parts = cmd.split(maxsplit=3)
            if len(parts) >= 3:
                username = parts[1]
                reason = parts[2]
                days = 30
                if len(parts) == 4 and parts[3]:
                    dur = parts[3].lower()
                    if dur.endswith('д'):
                        days = int(dur[:-1])
                    elif dur.endswith('м'):
                        days = int(dur[:-1]) * 30
                    elif dur.endswith('г'):
                        days = int(dur[:-1]) * 365
                    elif dur.endswith('н'):
                        days = 36500
                    else:
                        days = int(dur) if dur.isdigit() else 30
                expiry = datetime.now() + timedelta(days=days)
                self.bans[username] = {"reason": reason, "expiry": expiry.isoformat(), "banned_by": self.current_user}
                self.save_bans()
                self.log_console(f"🔨 Игрок {username} забанен на {days} дней. Причина: {reason}")
                if self.current_user == username:
                    self.logout()
                    messagebox.showerror("Бан", f"Вы были забанены!\nПричина: {reason}")
            else:
                self.log_console("❌ Использование: /ban [ник] [причина] [число][д/м/г/н]")
        
        elif cmd.startswith("/unban"):
            parts = cmd.split()
            if len(parts) == 2:
                username = parts[1]
                if username in self.bans:
                    del self.bans[username]
                    self.save_bans()
                    self.log_console(f"✅ Игрок {username} разбанен")
                else:
                    self.log_console(f"❌ Игрок {username} не в бане")
            else:
                self.log_console("❌ Использование: /unban [ник]")
        
        elif cmd.startswith("/kick"):
            parts = cmd.split()
            if len(parts) == 2:
                self.log_console(f"⚠️ Игрок {parts[1]} был кикнут")
                if self.current_user == parts[1]:
                    self.logout()
                    messagebox.showwarning("Кик", "Вы были кикнуты администратором!")
            else:
                self.log_console("❌ Использование: /kick [ник]")
        
        elif cmd.startswith("/mute"):
            parts = cmd.split()
            if len(parts) >= 2:
                self.log_console(f"🔇 Игрок {parts[1]} замучен в чате")
            else:
                self.log_console("❌ Использование: /mute [ник] [минуты]")
        
        elif cmd.startswith("/unmute"):
            parts = cmd.split()
            if len(parts) == 2:
                self.log_console(f"🔊 Игрок {parts[1]} размучен")
            else:
                self.log_console("❌ Использование: /unmute [ник]")
        
        elif cmd == "/clear":
            self.console_output.delete("1.0", tk.END)
            self.log_console("Консоль очищена")
        
        elif cmd == "/whoami":
            self.log_console(f"👤 Текущий пользователь: {self.current_user} | Админ: {self.is_admin}")
        
        elif cmd == "/list_users":
            self.log_console(f"📋 Список пользователей ({len(self.users)}):")
            for username, data in self.users.items():
                banned, _ = self.is_banned(username)
                status = "🔴 ЗАБАНЕН" if banned else "🟢 АКТИВЕН"
                self.log_console(f"  - @{username} ({data.get('display_name', username)}) - {status}")
        
        elif cmd.startswith("/delete_user"):
            parts = cmd.split()
            if len(parts) == 2:
                username = parts[1]
                if username in self.users:
                    del self.users[username]
                    self.save_user_data()
                    self.log_console(f"✅ Пользователь {username} удалён")
                else:
                    self.log_console(f"❌ Пользователь {username} не найден")
            else:
                self.log_console("❌ Использование: /delete_user [ник]")
        
        elif cmd.startswith("/broadcast"):
            msg = cmd[10:].strip()
            if msg:
                self.log_console(f"📢 ВСЕМ: {msg}")
                messagebox.showinfo("Объявление", msg)
            else:
                self.log_console("❌ Использование: /broadcast [сообщение]")
        
        elif cmd.startswith("/op"):
            parts = cmd.split()
            if len(parts) == 2 and self.current_user == "Admin":
                username = parts[1]
                if username in self.users:
                    self.users[username]["admin"] = True
                    self.save_user_data()
                    self.log_console(f"✅ Права админа выданы пользователю {username}")
                else:
                    self.log_console(f"❌ Пользователь {username} не найден")
            else:
                self.log_console("❌ Использование: /op [ник] (только Admin)")
        
        elif cmd.startswith("/deop"):
            parts = cmd.split()
            if len(parts) == 2 and self.current_user == "Admin":
                username = parts[1]
                if username in self.users:
                    self.users[username]["admin"] = False
                    self.save_user_data()
                    self.log_console(f"✅ Права админа сняты с пользователя {username}")
                else:
                    self.log_console(f"❌ Пользователь {username} не найден")
            else:
                self.log_console("❌ Использование: /deop [ник] (только Admin)")
        
        else:
            self.log_console(f"❌ Неизвестная команда: {cmd}. Введите /help")
    
    def open_login_window(self):
        if self.current_user:
            return
        
        theme = THEMES[self.current_theme]
        login_win = tk.Toplevel(self.root)
        login_win.title("Вход / Регистрация")
        login_win.geometry("350x500")
        login_win.configure(bg=theme["bg"])
        
        notebook = ttk.Notebook(login_win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка Входа
        login_frame = tk.Frame(notebook, bg=theme["bg"])
        notebook.add(login_frame, text="Вход")
        tk.Label(login_frame, text="Юзернейм:", bg=theme["bg"], fg=theme["text"]).pack(pady=5)
        username_entry = tk.Entry(login_frame, bg=theme["card_bg"], fg=theme["text"], insertbackground=theme["text"])
        username_entry.pack(pady=5)
        tk.Label(login_frame, text="Пароль:", bg=theme["bg"], fg=theme["text"]).pack(pady=5)
        password_entry = tk.Entry(login_frame, show="*", bg=theme["card_bg"], fg=theme["text"], insertbackground=theme["text"])
        password_entry.pack(pady=5)
        
        # Вкладка Регистрации
        reg_frame = tk.Frame(notebook, bg=theme["bg"])
        notebook.add(reg_frame, text="Регистрация")
        tk.Label(reg_frame, text="Юзернейм (латиница, @ будет добавлен):", bg=theme["bg"], fg=theme["text"]).pack(pady=5)
        reg_username = tk.Entry(reg_frame, bg=theme["card_bg"], fg=theme["text"])
        reg_username.pack(pady=5)
        tk.Label(reg_frame, text="Отображаемое имя:", bg=theme["bg"], fg=theme["text"]).pack(pady=5)
        reg_display = tk.Entry(reg_frame, bg=theme["card_bg"], fg=theme["text"])
        reg_display.pack(pady=5)
        tk.Label(reg_frame, text="Пароль:", bg=theme["bg"], fg=theme["text"]).pack(pady=5)
        reg_pass = tk.Entry(reg_frame, show="*", bg=theme["card_bg"], fg=theme["text"])
        reg_pass.pack(pady=5)
        tk.Label(reg_frame, text="Email (необязательно):", bg=theme["bg"], fg=theme["text"]).pack(pady=5)
        reg_email = tk.Entry(reg_frame, bg=theme["card_bg"], fg=theme["text"])
        reg_email.pack(pady=5)
        
        # 2FA окно (появляется после успешного ввода пароля)
        def show_2fa(username):
            self.pending_2fa_user = username
            user_email = self.users[username].get("email")
            if not user_email or not self.users[username].get("email_verified"):
                # Если почта не подтверждена, входим без 2FA
                self.current_user = username
                self.is_admin = self.users[username].get("admin", False) or (username == "Admin")
                self.status_label.config(text=f"✅ Добро пожаловать, {self.users[username].get('display_name', username)}!")
                login_win.destroy()
                self.create_widgets()
                self.show_profile_tab()
                return
            self.send_2fa_code(user_email)
            code_win = tk.Toplevel(login_win)
            code_win.title("2FA - Код подтверждения")
            code_win.geometry("300x150")
            code_win.configure(bg=theme["bg"])
            tk.Label(code_win, text="Введите код из письма:", bg=theme["bg"], fg=theme["text"]).pack(pady=10)
            code_entry = tk.Entry(code_win, bg=theme["card_bg"], fg=theme["text"])
            code_entry.pack(pady=5)
            def verify():
                if code_entry.get() == self.temp_2fa_code:
                    self.current_user = self.pending_2fa_user
                    self.is_admin = self.users[self.current_user].get("admin", False) or (self.current_user == "Admin")
                    self.status_label.config(text=f"✅ Добро пожаловать, {self.users[self.current_user].get('display_name', self.current_user)}!")
                    login_win.destroy()
                    code_win.destroy()
                    self.create_widgets()
                    self.show_profile_tab()
                else:
                    messagebox.showerror("Ошибка", "Неверный код!")
            tk.Button(code_win, text="ПОДТВЕРДИТЬ", command=verify, bg=theme["accent"], fg="white").pack(pady=10)
        
        def do_login():
            u = username_entry.get()
            p = password_entry.get()
            banned, ban_info = self.is_banned(u)
            if banned:
                messagebox.showerror("Доступ запрещён", f"Вы забанены!\nПричина: {ban_info['reason']}\nДо: {ban_info['expiry']}")
                return
            if u in self.users and self.users[u].get("password") == p:
                show_2fa(u)
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
        
        def do_register():
            u = reg_username.get().strip()
            display = reg_display.get().strip()
            p = reg_pass.get()
            email = reg_email.get().strip()
            if not u or not display or not p:
                messagebox.showerror("Ошибка", "Заполните обязательные поля!")
                return
            if u in self.users:
                messagebox.showerror("Ошибка", "Пользователь уже существует!")
                return
            self.users[u] = {
                "display_name": display,
                "password": p,
                "email": email if email else None,
                "email_verified": False,
                "admin": False
            }
            self.save_user_data()
            messagebox.showinfo("Успех", "Регистрация успешна! Теперь войдите.")
            notebook.select(0)
        
        tk.Button(login_frame, text="ВОЙТИ", command=do_login, bg=theme["accent"], fg="white").pack(pady=10)
        tk.Button(reg_frame, text="ЗАРЕГИСТРИРОВАТЬСЯ", command=do_register, bg=theme["accent"], fg="white").pack(pady=10)
    
    def logout(self):
        self.current_user = None
        self.is_admin = False
        self.skin_image = None
        self.current_skin_path = None
        self.status_label.config(text="✅ Вы вышли из профиля")
        self.create_widgets()
    
    def install_cheat(self):
        sel = self.cheat_listbox.curselection()
        if not sel:
            messagebox.showerror("Ошибка", "Выбери чит!")
            return
        cheat_name = self.cheat_listbox.get(sel[0])
        cheat = CHEATS[cheat_name]
        mods_dir = os.path.join(".minecraft", "mods")
        os.makedirs(mods_dir, exist_ok=True)
        dest = os.path.join(mods_dir, cheat["file"])
        
        def download():
            self.status_label.config(text=f"📥 Скачиваю {cheat_name}...")
            try:
                r = requests.get(cheat["url"], stream=True)
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                self.status_label.config(text=f"✅ {cheat_name} установлен!")
                messagebox.showinfo("Успех", f"{cheat_name} установлен в mods")
            except Exception as e:
                self.status_label.config(text=f"❌ Ошибка: {e}")
        threading.Thread(target=download).start()
    
    def open_mods(self):
        path = os.path.join(".minecraft", "mods")
        os.makedirs(path, exist_ok=True)
        os.startfile(path)
    
    def launch_game(self):
        self.status_label.config(text="🚀 Запуск...")
        self.root.withdraw()
        
        # Пробуем запустить через starter.py
        if os.path.exists("starter.py"):
            try:
                subprocess.Popen(["python", "starter.py"], cwd=os.getcwd())
                self.status_label.config(text="✅ Игра запущена через starter.py!")
                return
            except Exception as e:
                self.status_label.config(text=f"❌ Ошибка starter.py: {e}")
        
        # Если starter.py не сработал — пробуем TLauncher
        tlauncher_path = os.path.expandvars(r"%APPDATA%\.minecraft\TLauncher.exe")
        if os.path.exists(tlauncher_path):
            subprocess.Popen([tlauncher_path])
            self.status_label.config(text="✅ Игра запущена через TLauncher!")
        else:
            self.status_label.config(text="❌ Не найден ни starter.py, ни TLauncher")
            self.root.deiconify()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PolarLauncher()
    app.run()