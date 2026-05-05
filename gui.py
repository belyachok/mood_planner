"""
Главный графический интерфейс приложения с улучшенным дизайном
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
from datetime import datetime, date

from config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, TASK_CATEGORIES, CATEGORY_COLORS
from schedule_manager import ScheduleManager
from stats_view import StatisticsView


class MoodPlannerApp:
    """Главное приложение с современным дизайном"""
    
    def __init__(self, db):
        self.db = db
        
        # Цветовая схема
        self.colors = {
            "bg": "#1e1e2e",
            "card_bg": "#2d2d3a",
            "accent": "#7c3aed",
            "accent_light": "#8b5cf6",
            "success": "#10b981",
            "danger": "#ef4444",
            "warning": "#f59e0b",
            "text": "#ffffff",
            "text_secondary": "#a1a1aa",
            "border": "#3f3f46"
        }
        
        # Создаём главное окно
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(1000, 600)
        self.root.configure(bg=self.colors["bg"])
        
        # Настройка стилей ttk
        self.setup_styles()
        
        # Создаём вкладки с иконками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Создаём вкладки
        self.create_schedule_tab()
        self.create_tasks_tab()
        self.create_habits_tab()
        self.create_stats_tab()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def setup_styles(self):
        """Настройка стилей для ttk виджетов"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["card_bg"], 
                        foreground=self.colors["text"], padding=[15, 5],
                        font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])])
        
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabelframe", background=self.colors["card_bg"], 
                        foreground=self.colors["text"], bordercolor=self.colors["border"])
        style.configure("TLabelframe.Label", background=self.colors["card_bg"], 
                        foreground=self.colors["text"], font=("Segoe UI", 10, "bold"))
        
        style.configure("TButton", background=self.colors["accent"], 
                        foreground="white", borderwidth=0, focuscolor="none",
                        font=("Segoe UI", 10))
        style.map("TButton", background=[("active", self.colors["accent_light"])])
        
        style.configure("TEntry", fieldbackground=self.colors["card_bg"], 
                        foreground=self.colors["text"], borderwidth=1)
        
        style.configure("TCombobox", fieldbackground=self.colors["card_bg"], 
                        foreground=self.colors["text"])
    
    def create_schedule_tab(self):
        """Вкладка расписания"""
        self.schedule_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.schedule_frame, text="📅 Расписание")
        
        self.schedule_manager = ScheduleManager(self.schedule_frame, self.db)
    
    def create_tasks_tab(self):
        """Вкладка управления задачами"""
        self.tasks_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tasks_frame, text="📝 Задачи")
        
        # Контейнер
        container = tk.Frame(self.tasks_frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Форма добавления задачи
        form_card = tk.Frame(container, bg=self.colors["card_bg"], relief="flat",
                              highlightbackground=self.colors["border"], highlightthickness=1)
        form_card.pack(fill="x", pady=5)
        
        form_inner = tk.Frame(form_card, bg=self.colors["card_bg"])
        form_inner.pack(fill="x", padx=15, pady=15)
        
        tk.Label(form_inner, text="➕ Добавить новую задачу", 
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors["card_bg"], fg=self.colors["text"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        # Название
        tk.Label(form_inner, text="Название:", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=1, column=0, sticky="w", pady=5)
        self.task_title = tk.Entry(form_inner, width=40, font=("Segoe UI", 10),
                                    bg=self.colors["bg"], fg=self.colors["text"],
                                    insertbackground=self.colors["text"])
        self.task_title.grid(row=1, column=1, pady=5)
        
        # Категория
        tk.Label(form_inner, text="Категория:", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=2, column=0, sticky="w", pady=5)
        self.task_category = ttk.Combobox(form_inner, values=TASK_CATEGORIES, width=37)
        self.task_category.grid(row=2, column=1, pady=5)
        self.task_category.set(TASK_CATEGORIES[0])
        
        # Уровень энергии
        tk.Label(form_inner, text="Энергозатратность (1-10):", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=3, column=0, sticky="w", pady=5)
        self.task_energy = tk.Scale(form_inner, from_=1, to=10, orient="horizontal", 
                                     length=200, bg=self.colors["card_bg"], fg=self.colors["text"],
                                     troughcolor=self.colors["border"], highlightthickness=0)
        self.task_energy.grid(row=3, column=1, pady=5)
        self.task_energy.set(5)
        
        # Длительность
        tk.Label(form_inner, text="Длительность (мин):", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=4, column=0, sticky="w", pady=5)
        self.task_duration = ttk.Spinbox(form_inner, from_=15, to=240, increment=15, width=10)
        self.task_duration.grid(row=4, column=1, pady=5, sticky="w")
        self.task_duration.set(30)
        
        # Кнопка добавления
        add_btn = tk.Button(form_inner, text="➕ Добавить задачу", 
                            bg=self.colors["accent"], fg="white",
                            font=("Segoe UI", 10, "bold"),
                            relief="flat", padx=15, pady=5,
                            command=self.add_task)
        add_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Список задач
        tasks_card = tk.Frame(container, bg=self.colors["card_bg"], relief="flat",
                               highlightbackground=self.colors["border"], highlightthickness=1)
        tasks_card.pack(fill="both", expand=True, pady=5)
        
        tasks_inner = tk.Frame(tasks_card, bg=self.colors["card_bg"])
        tasks_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        tk.Label(tasks_inner, text="📋 Мои задачи", 
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors["card_bg"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        
        scrollbar = tk.Scrollbar(tasks_inner)
        scrollbar.pack(side="right", fill="y")
        
        self.task_listbox = tk.Listbox(tasks_inner, yscrollcommand=scrollbar.set,
                                        font=("Segoe UI", 10), height=8,
                                        bg=self.colors["bg"], fg=self.colors["text"],
                                        selectbackground=self.colors["accent"],
                                        relief="flat", borderwidth=0)
        self.task_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        # Кнопка удаления
        del_btn = tk.Button(tasks_inner, text="🗑 Удалить выбранную задачу",
                            bg=self.colors["danger"], fg="white", 
                            font=("Segoe UI", 10),
                            relief="flat", padx=10, pady=5,
                            command=self.delete_task)
        del_btn.pack(pady=10)
        
        self.refresh_task_list()
    
    def create_habits_tab(self):
        """Вкладка привычек"""
        self.habits_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.habits_frame, text="🔥 Привычки")
        
        container = tk.Frame(self.habits_frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Форма добавления привычки
        form_card = tk.Frame(container, bg=self.colors["card_bg"], relief="flat",
                              highlightbackground=self.colors["border"], highlightthickness=1)
        form_card.pack(fill="x", pady=5)
        
        form_inner = tk.Frame(form_card, bg=self.colors["card_bg"])
        form_inner.pack(fill="x", padx=15, pady=15)
        
        tk.Label(form_inner, text="➕ Добавить привычку", 
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors["card_bg"], fg=self.colors["text"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        tk.Label(form_inner, text="Название:", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=1, column=0, sticky="w", pady=5)
        self.habit_name = tk.Entry(form_inner, width=30, font=("Segoe UI", 10),
                                    bg=self.colors["bg"], fg=self.colors["text"])
        self.habit_name.grid(row=1, column=1, pady=5)
        
        tk.Label(form_inner, text="Категория:", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=2, column=0, sticky="w", pady=5)
        self.habit_category = ttk.Combobox(form_inner, values=TASK_CATEGORIES, width=27)
        self.habit_category.grid(row=2, column=1, pady=5)
        self.habit_category.set("Здоровье")
        
        tk.Label(form_inner, text="Частота:", bg=self.colors["card_bg"], 
                 fg=self.colors["text_secondary"]).grid(row=3, column=0, sticky="w", pady=5)
        self.habit_frequency = ttk.Combobox(form_inner, values=["daily", "weekly"], width=27)
        self.habit_frequency.grid(row=3, column=1, pady=5)
        self.habit_frequency.set("daily")
        
        add_btn = tk.Button(form_inner, text="➕ Добавить привычку", 
                            bg=self.colors["accent"], fg="white",
                            font=("Segoe UI", 10, "bold"),
                            relief="flat", padx=15, pady=5,
                            command=self.add_habit)
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Список привычек
        habits_card = tk.Frame(container, bg=self.colors["card_bg"], relief="flat",
                                highlightbackground=self.colors["border"], highlightthickness=1)
        habits_card.pack(fill="both", expand=True, pady=5)
        
        habits_inner = tk.Frame(habits_card, bg=self.colors["card_bg"])
        habits_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        tk.Label(habits_inner, text="🔥 Мои привычки", 
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors["card_bg"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        
        self.habits_listbox = tk.Listbox(habits_inner, font=("Segoe UI", 10), height=6,
                                          bg=self.colors["bg"], fg=self.colors["text"],
                                          selectbackground=self.colors["accent"],
                                          relief="flat", borderwidth=0)
        self.habits_listbox.pack(fill="both", expand=True)
        
        complete_btn = tk.Button(habits_inner, text="✓ Отметить выполнение сегодня",
                                  bg=self.colors["success"], fg="white",
                                  font=("Segoe UI", 10, "bold"),
                                  relief="flat", padx=15, pady=8,
                                  command=self.complete_habit)
        complete_btn.pack(pady=10)
        
        self.refresh_habits()
    
    def create_stats_tab(self):
        """Вкладка статистики"""
        self.stats_frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.stats_frame, text="📊 Статистика")
        
        self.statistics = StatisticsView(self.stats_frame, self.db)
    
    def add_task(self):
        """Добавление задачи-шаблона"""
        title = self.task_title.get().strip()
        category = self.task_category.get()
        energy = self.task_energy.get()
        duration = int(self.task_duration.get())
        
        if not title:
            messagebox.showwarning("Внимание", "Введите название задачи!")
            return
        
        self.db.add_task(title, category, energy, duration)
        self.task_title.delete(0, tk.END)
        self.task_energy.set(5)
        self.refresh_task_list()
        messagebox.showinfo("Успех", "Задача добавлена!")
    
    def refresh_task_list(self):
        """Обновление списка задач"""
        self.task_listbox.delete(0, tk.END)
        tasks = self.db.get_all_tasks()
        
        if not tasks:
            self.task_listbox.insert(tk.END, "📭 Нет задач. Добавьте свою первую задачу!")
        else:
            for task in tasks:
                duration = task.get('estimated_duration', 30)
                display_text = f"{task['title']} [{task['category']}] | ⚡{task['energy_level']} | {duration} мин"
                self.task_listbox.insert(tk.END, display_text)
    
    def delete_task(self):
        """Удаление задачи-шаблона"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите задачу для удаления!")
            return
        
        tasks = self.db.get_all_tasks()
        if tasks and selection[0] < len(tasks):
            task_id = tasks[selection[0]]['id']
            if messagebox.askyesno("Подтверждение", "Удалить эту задачу?"):
                self.db.delete_task(task_id)
                self.refresh_task_list()
                messagebox.showinfo("Успех", "Задача удалена!")
    
    def add_habit(self):
        """Добавление привычки"""
        name = self.habit_name.get().strip()
        category = self.habit_category.get()
        frequency = self.habit_frequency.get()
        
        if not name:
            messagebox.showwarning("Внимание", "Введите название привычки!")
            return
        
        self.db.add_habit(name, category, frequency)
        self.habit_name.delete(0, tk.END)
        self.refresh_habits()
        messagebox.showinfo("Успех", "Привычка добавлена!")
    
    def refresh_habits(self):
        """Обновление списка привычек"""
        self.habits_listbox.delete(0, tk.END)
        habits = self.db.get_all_habits()
        
        for habit in habits:
            streak = self.db.get_habit_streak(habit['id'])
            display_text = f"{habit['name']} [{habit['category']}] | Серия: {streak} дней"
            self.habits_listbox.insert(tk.END, display_text)
    
    def complete_habit(self):
        """Отметить выполнение привычки"""
        selection = self.habits_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите привычку!")
            return
        
        habits = self.db.get_all_habits()
        if habits and selection[0] < len(habits):
            habit_id = habits[selection[0]]['id']
            today_str = date.today().strftime("%Y-%m-%d")
            
            if self.db.complete_habit(habit_id, today_str):
                self.refresh_habits()
                messagebox.showinfo("Успех", "Привычка отмечена! Серия продолжается! 🔥")
            else:
                messagebox.showinfo("Информация", "Вы уже отмечали эту привычку сегодня")
    
    def on_closing(self):
        """Закрытие приложения"""
        self.db.close()
        self.root.destroy()