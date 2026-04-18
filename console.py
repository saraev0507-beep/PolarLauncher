import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import smtplib
import threading
from email.mime.text import MIMEText

# ========== НАСТРОЙКИ ПОЧТЫ ==========
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
EMAIL_LOGIN = "polar.ras@mail.ru"
EMAIL_PASSWORD = "D6uTw5D3HHtIkg04l5J5"

# ========== ЦВЕТА ==========
COLORS = {"bg": "#0d0a1a", "card_bg": "#1a1338", "accent": "#b87cff", "text": "#ffffff", "error": "#ff4444"}
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"Admin": {"password": "050714", "admin": True, "email": EMAIL_LOGIN}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def send_mass_mail(subject, message):
    users = load_users()
    recipients = []
    for username, data in users.items():
        if data.get("email"):
            recipients.append(data["email"])
    
    if not recipients:
        return False, "Нет email адресов в базе"
    
    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_LOGIN
    
    def send():
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
                for email in recipients:
                    msg["To"] = email
                    server.send_message(msg)
        except Exception as e:
            print(f"Ошибка: {e}")
    
    threading.Thread(target=send).start()
    return True, f"Рассылка отправлена {len(recipients)} пользователям"

# ========== ОКНО ВХОДА/РЕГИСТРАЦИИ ==========
class ConsoleLogin:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POLAR CONSOLE - ВХОД")
        self.root.geometry("400x450")
        self.root.configure(bg=COLORS["bg"])
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self.root, text="POLAR CONSOLE", font=("Impact", 28), bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=20)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Вкладка Входа
        login_frame = tk.Frame(notebook, bg=COLORS["card_bg"])
        notebook.add(login_frame, text="Вход")
        
        tk.Label(login_frame, text="Логин:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.login_user = tk.Entry(login_frame, bg=COLORS["bg"], fg=COLORS["text"])
        self.login_user.pack(pady=5, padx=20, fill="x")
        
        tk.Label(login_frame, text="Пароль:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.login_pass = tk.Entry(login_frame, show="*", bg=COLORS["bg"], fg=COLORS["text"])
        self.login_pass.pack(pady=5, padx=20, fill="x")
        
        self.login_error = tk.Label(login_frame, text="", bg=COLORS["card_bg"], fg=COLORS["error"])
        self.login_error.pack()
        
        tk.Button(login_frame, text="ВОЙТИ", command=self.do_login, bg=COLORS["accent"], fg="white").pack(pady=20, padx=20, fill="x")
        
        # Вкладка Регистрации
        reg_frame = tk.Frame(notebook, bg=COLORS["card_bg"])
        notebook.add(reg_frame, text="Регистрация")
        
        tk.Label(reg_frame, text="Логин:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.reg_user = tk.Entry(reg_frame, bg=COLORS["bg"], fg=COLORS["text"])
        self.reg_user.pack(pady=5, padx=20, fill="x")
        
        tk.Label(reg_frame, text="Пароль:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.reg_pass = tk.Entry(reg_frame, show="*", bg=COLORS["bg"], fg=COLORS["text"])
        self.reg_pass.pack(pady=5, padx=20, fill="x")
        
        tk.Label(reg_frame, text="Имя (отображаемое):", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.reg_name = tk.Entry(reg_frame, bg=COLORS["bg"], fg=COLORS["text"])
        self.reg_name.pack(pady=5, padx=20, fill="x")
        
        self.reg_error = tk.Label(reg_frame, text="", bg=COLORS["card_bg"], fg=COLORS["error"])
        self.reg_error.pack()
        
        tk.Button(reg_frame, text="ЗАРЕГИСТРИРОВАТЬСЯ", command=self.do_register, bg=COLORS["accent"], fg="white").pack(pady=20, padx=20, fill="x")
    
    def do_login(self):
        users = load_users()
        username = self.login_user.get()
        password = self.login_pass.get()
        
        if username in users and users[username]["password"] == password:
            if users[username].get("admin", False) or username == "Admin":
                self.root.destroy()
                ConsoleApp(username).run()
            else:
                self.login_error.config(text="Доступ запрещён! Требуются права администратора.")
        else:
            self.login_error.config(text="Неверный логин или пароль!")
    
    def do_register(self):
        users = load_users()
        username = self.reg_user.get()
        password = self.reg_pass.get()
        name = self.reg_name.get()
        
        if not username or not password or not name:
            self.reg_error.config(text="Заполните все поля!")
            return
        
        if username in users:
            self.reg_error.config(text="Пользователь уже существует!")
            return
        
        users[username] = {"password": password, "display_name": name, "admin": False}
        save_users(users)
        messagebox.showinfo("Успех", "Регистрация успешна!")
        self.reg_user.delete(0, tk.END)
        self.reg_pass.delete(0, tk.END)
        self.reg_name.delete(0, tk.END)
        self.reg_error.config(text="")
    
    def run(self):
        self.root.mainloop()

# ========== ОСНОВНОЕ ПРИЛОЖЕНИЕ КОНСОЛИ ==========
class ConsoleApp:
    def __init__(self, username):
        self.root = tk.Tk()
        self.root.title("POLAR CONSOLE")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLORS["bg"])
        self.username = username
        self.create_widgets()
    
    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg=COLORS["bg"])
        top_frame.pack(fill="x", pady=10)
        tk.Label(top_frame, text=f"POLAR CONSOLE - {self.username}", font=("Arial", 18, "bold"), bg=COLORS["bg"], fg=COLORS["accent"]).pack()
        
        # Левая панель
        left_frame = tk.Frame(self.root, bg=COLORS["bg"])
        left_frame.pack(side="left", fill="y", padx=20)
        
        buttons = [
            ("👥 ВСЕ ПОЛЬЗОВАТЕЛИ", self.show_users),
            ("📧 РАССЫЛКА", self.show_mail),
            ("📊 СТАТИСТИКА", self.show_stats),
            ("⚙️ ДОБАВИТЬ EMAIL", self.show_add_email),
            ("🚪 ВЫХОД", self.logout)
        ]
        
        for text, cmd in buttons:
            tk.Button(left_frame, text=text, command=cmd, bg=COLORS["card_bg"], fg=COLORS["text"], width=30, pady=10).pack(pady=5)
        
        # Центральная панель
        self.center_frame = tk.Frame(self.root, bg=COLORS["card_bg"], relief="ridge", bd=2)
        self.center_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.show_users()
    
    def clear_center(self):
        for w in self.center_frame.winfo_children():
            w.destroy()
    
    def show_users(self):
        self.clear_center()
        tk.Label(self.center_frame, text="👥 ВСЕ ПОЛЬЗОВАТЕЛИ POLAR", font=("Arial", 16, "bold"), bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(pady=10)
        
        users = load_users()
        
        columns = ("Логин", "Имя", "Права", "Email")
        tree = ttk.Treeview(self.center_frame, columns=columns, show="headings", height=20)
        tree.heading("Логин", text="Логин")
        tree.heading("Имя", text="Имя")
        tree.heading("Права", text="Права")
        tree.heading("Email", text="Email")
        tree.column("Логин", width=150)
        tree.column("Имя", width=150)
        tree.column("Права", width=100)
        tree.column("Email", width=250)
        
        for u, data in users.items():
            admin = "👑 Админ" if data.get("admin") else "👤 Пользователь"
            name = data.get("display_name", "-")
            email = data.get("email", "-")
            tree.insert("", tk.END, values=(u, name, admin, email))
        
        tree.pack(padx=20, pady=10, fill="both", expand=True)
        tk.Label(self.center_frame, text=f"📊 Всего: {len(users)} пользователей", bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(pady=5)
    
    def show_mail(self):
        self.clear_center()
        tk.Label(self.center_frame, text="📧 МАССОВАЯ РАССЫЛКА", font=("Arial", 16, "bold"), bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(pady=10)
        
        users = load_users()
        recipients = [f"{u} ({data.get('email', 'нет email')})" for u, data in users.items() if data.get("email")]
        
        tk.Label(self.center_frame, text="Получатели (есть email):", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        recipients_text = tk.Text(self.center_frame, bg=COLORS["bg"], fg=COLORS["text"], height=5, width=60)
        recipients_text.pack(padx=20, pady=5, fill="x")
        recipients_text.insert("1.0", "\n".join(recipients) if recipients else "Нет получателей")
        recipients_text.config(state="disabled")
        
        tk.Label(self.center_frame, text="Тема:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.subject_entry = tk.Entry(self.center_frame, bg=COLORS["bg"], fg=COLORS["text"], width=60)
        self.subject_entry.pack(pady=5, padx=20, fill="x")
        
        tk.Label(self.center_frame, text="Сообщение:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.msg_text = tk.Text(self.center_frame, bg=COLORS["bg"], fg=COLORS["text"], height=10, width=60)
        self.msg_text.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.send_btn = tk.Button(self.center_frame, text="📨 ОТПРАВИТЬ РАССЫЛКУ", command=self.do_send_mail, bg=COLORS["accent"], fg="white", font=("Arial", 12, "bold"))
        self.send_btn.pack(pady=10, padx=20, fill="x")
        
        self.mail_status = tk.Label(self.center_frame, text="", bg=COLORS["card_bg"], fg=COLORS["accent"])
        self.mail_status.pack(pady=5)
    
    def do_send_mail(self):
        subject = self.subject_entry.get().strip()
        message = self.msg_text.get("1.0", tk.END).strip()
        
        if not subject or not message:
            self.mail_status.config(text="❌ Заполните тему и сообщение!", fg=COLORS["error"])
            return
        
        self.send_btn.config(state="disabled", text="⏳ ОТПРАВКА...")
        self.mail_status.config(text="⏳ Отправка...", fg=COLORS["accent"])
        self.root.update()
        
        success, msg = send_mass_mail(subject, message)
        
        if success:
            self.mail_status.config(text=f"✅ {msg}", fg="green")
            self.subject_entry.delete(0, tk.END)
            self.msg_text.delete("1.0", tk.END)
        else:
            self.mail_status.config(text=f"❌ {msg}", fg=COLORS["error"])
        
        self.send_btn.config(state="normal", text="📨 ОТПРАВИТЬ РАССЫЛКУ")
    
    def show_stats(self):
        self.clear_center()
        users = load_users()
        tk.Label(self.center_frame, text="📊 СТАТИСТИКА", font=("Arial", 16, "bold"), bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(pady=10)
        
        stats_text = tk.Text(self.center_frame, bg=COLORS["bg"], fg=COLORS["text"], font=("Courier", 12))
        stats_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        stats = f"""
╔══════════════════════════════════════╗
║         ПОЛЯРНАЯ СТАТИСТИКА          ║
╠══════════════════════════════════════╣
║  👥 Всего пользователей: {len(users)}           
║  👑 Администраторов: {sum(1 for u in users.values() if u.get('admin'))}         
║  📧 С email: {sum(1 for u in users.values() if u.get('email'))}            
╠══════════════════════════════════════╣
║  🎮 POLAR LAUNCHER    v4.2          ║
║  🖥️ POLAR CONSOLE     v1.0          ║
║  🔍 POLAR OSINT       v1.0          ║
╚══════════════════════════════════════╝
        """
        stats_text.insert("1.0", stats)
        stats_text.config(state="disabled")
    
    def show_add_email(self):
        self.clear_center()
        tk.Label(self.center_frame, text="⚙️ ДОБАВИТЬ EMAIL ПОЛЬЗОВАТЕЛЮ", font=("Arial", 16, "bold"), bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(pady=10)
        
        users = load_users()
        
        tk.Label(self.center_frame, text="Выберите пользователя:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.user_var = tk.StringVar()
        user_menu = ttk.Combobox(self.center_frame, textvariable=self.user_var, values=list(users.keys()), state="readonly", width=30)
        user_menu.pack(pady=5)
        
        tk.Label(self.center_frame, text="Email:", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.email_entry = tk.Entry(self.center_frame, bg=COLORS["bg"], fg=COLORS["text"], width=40)
        self.email_entry.pack(pady=5)
        
        self.email_status = tk.Label(self.center_frame, text="", bg=COLORS["card_bg"], fg=COLORS["accent"])
        self.email_status.pack(pady=5)
        
        def add_email():
            username = self.user_var.get()
            email = self.email_entry.get().strip()
            if not username or not email:
                self.email_status.config(text="❌ Выберите пользователя и введите email!", fg=COLORS["error"])
                return
            if "@" not in email or "." not in email:
                self.email_status.config(text="❌ Неверный формат email!", fg=COLORS["error"])
                return
            
            users[username]["email"] = email
            save_users(users)
            self.email_status.config(text=f"✅ Email для {username} добавлен!", fg="green")
            self.email_entry.delete(0, tk.END)
            self.show_users()
        
        tk.Button(self.center_frame, text="💾 СОХРАНИТЬ", command=add_email, bg=COLORS["accent"], fg="white", font=("Arial", 12)).pack(pady=20, padx=20, fill="x")
    
    def logout(self):
        self.root.destroy()
        ConsoleLogin().run()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ConsoleLogin()
    app.run()