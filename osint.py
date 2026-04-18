import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import json
import os
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from datetime import datetime

COLORS = {"bg": "#0d0a1a", "card_bg": "#1a1338", "accent": "#b87cff", "text": "#ffffff", "error": "#ff4444"}
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"Admin": {"password": "050714", "admin": True}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ========== ОКНО ВХОДА/РЕГИСТРАЦИИ ==========
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POLAR OSINT - ВХОД")
        self.root.geometry("400x450")
        self.root.configure(bg=COLORS["bg"])
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self.root, text="POLAR OSINT", font=("Impact", 28), bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=20)
        
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
            self.root.destroy()
            OsintApp(username).run()
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

# ========== ОСНОВНОЕ ПРИЛОЖЕНИЕ ==========
class OsintApp:
    def __init__(self, username):
        self.root = tk.Tk()
        self.root.title("POLAR OSINT PRO")
        self.root.geometry("1100x750")
        self.root.configure(bg=COLORS["bg"])
        self.username = username
        self.create_widgets()
    
    def create_widgets(self):
        # Заголовок
        top_frame = tk.Frame(self.root, bg=COLORS["bg"])
        top_frame.pack(fill="x", pady=10)
        tk.Label(top_frame, text=f"POLAR OSINT PRO - {self.username}", font=("Impact", 24), bg=COLORS["bg"], fg=COLORS["accent"]).pack()
        
        # Ввод данных
        input_frame = tk.Frame(self.root, bg=COLORS["card_bg"], relief="ridge", bd=2)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(input_frame, text="Введите данные (ФИО, телефон, email, ник):", bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        self.query_entry = tk.Entry(input_frame, bg=COLORS["bg"], fg=COLORS["text"], font=("Arial", 12), width=50)
        self.query_entry.pack(pady=5, padx=20, fill="x")
        
        # Кнопки
        btn_frame = tk.Frame(input_frame, bg=COLORS["card_bg"])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔍 НАЧАТЬ ПОИСК", command=self.start_search, bg=COLORS["accent"], fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="🗑️ ОЧИСТИТЬ", command=self.clear_results, bg=COLORS["error"], fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="🚪 ВЫЙТИ", command=self.logout, bg=COLORS["error"], fg="white").pack(side="left", padx=10)
        
        # Результаты
        results_frame = tk.Frame(self.root, bg=COLORS["card_bg"], relief="ridge", bd=2)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="📋 РЕЗУЛЬТАТЫ ПОИСКА", font=("Arial", 14, "bold"), bg=COLORS["card_bg"], fg=COLORS["accent"]).pack(pady=5)
        
        self.results_text = tk.Text(results_frame, bg=COLORS["bg"], fg=COLORS["text"], wrap="word", font=("Courier", 10))
        self.results_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Статус
        self.status_label = tk.Label(self.root, text="✅ Готов к работе", bg=COLORS["bg"], fg=COLORS["accent"])
        self.status_label.pack(pady=5)
    
    def logout(self):
        self.root.destroy()
        LoginWindow().run()
    
    def log(self, text, color="text"):
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def clear_results(self):
        self.results_text.delete("1.0", tk.END)
        self.status_label.config(text="✅ Очищено")
    
    def search_phone(self, phone):
        results = []
        try:
            phone_clean = re.sub(r'\D', '', phone)
            if len(phone_clean) == 11 and phone_clean.startswith('8'):
                phone_clean = '7' + phone_clean[1:]
            elif len(phone_clean) == 10:
                phone_clean = '7' + phone_clean
            
            parsed = phonenumbers.parse(f"+{phone_clean}", None)
            operator = carrier.name_for_number(parsed, "ru")
            results.append(f"📱 Оператор: {operator if operator else 'Не определён'}")
            region = geocoder.description_for_number(parsed, "ru")
            results.append(f"📍 Регион: {region if region else 'Не определён'}")
            tz = timezone.time_zones_for_number(parsed)
            results.append(f"⏰ Часовой пояс: {', '.join(tz) if tz else 'Не определён'}")
            results.append(f"📞 Номер: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        except Exception as e:
            results.append(f"❌ Ошибка: {e}")
        return results
    
    def search_social(self, query):
        results = []
        try:
            r = requests.get(f"https://t.me/{query}", timeout=5)
            if "If you have Telegram" in r.text or "Sorry, this username doesn't exist" not in r.text:
                results.append(f"💬 Telegram: https://t.me/{query}")
        except:
            pass
        try:
            r = requests.get(f"https://api.github.com/users/{query}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                results.append(f"🐙 GitHub: {data.get('html_url')}")
        except:
            pass
        try:
            r = requests.get(f"https://vk.com/{query}", timeout=5)
            if "profile" in r.url:
                results.append(f"📘 VK: https://vk.com/{query}")
        except:
            pass
        try:
            r = requests.get(f"https://www.instagram.com/{query}/", timeout=5)
            if "Page Not Found" not in r.text:
                results.append(f"📸 Instagram: https://www.instagram.com/{query}/")
        except:
            pass
        try:
            r = requests.get(f"https://www.tiktok.com/@{query}", timeout=5)
            if "Couldn't find this account" not in r.text:
                results.append(f"🎵 TikTok: https://www.tiktok.com/@{query}")
        except:
            pass
        try:
            r = requests.get(f"https://www.youtube.com/@{query}", timeout=5)
            if "doesn't exist" not in r.text:
                results.append(f"📺 YouTube: https://www.youtube.com/@{query}")
        except:
            pass
        return results
    
    def start_search(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showerror("Ошибка", "Введите данные для поиска!")
            return
        
        self.results_text.delete("1.0", tk.END)
        self.status_label.config(text="🔍 Поиск...")
        self.root.update()
        
        self.log("=" * 70)
        self.log(f"POLAR OSINT PRO - ОТЧЁТ ПО ЗАПРОСУ: {query}")
        self.log(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70)
        
        if re.match(r'^[\d\s\+\(\)\-]+$', query):
            self.log("\n📞 ИНФОРМАЦИЯ ПО ТЕЛЕФОНУ:")
            for line in self.search_phone(query):
                self.log(f"   {line}")
        
        if '@' in query and '.' in query:
            self.log("\n📧 ИНФОРМАЦИЯ ПО EMAIL:")
            self.log(f"   Email: {query}")
        
        if not re.match(r'^[\d\s\+\(\)\-]+$', query) and '@' not in query:
            self.log("\n🌐 ПРОФИЛИ В СОЦСЕТЯХ:")
            social_results = self.search_social(query)
            if social_results:
                for line in social_results:
                    self.log(f"   {line}")
            else:
                self.log("   ❌ Профили не найдены")
        
        self.log("\n" + "=" * 70)
        self.log("✅ ПОИСК ЗАВЕРШЁН")
        self.status_label.config(text="✅ Поиск завершён")

if __name__ == "__main__":
    app = LoginWindow()
    app.run()