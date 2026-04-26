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
    
    def __init__(self, db, recommendation_engine):
        self.db = db
        self.recommendation_engine = recommendation_engine
        
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
    
    def create_mood_tab(self):
        """Вкладка многокомпонентной оценки состояния"""
        self.mood_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mood_frame, text="🎭 Моё состояние")
        
        # Заголовок
        title = tk.Label(self.mood_frame, text="Оцените своё состояние", 
                        font=("Segoe UI", 18, "bold"),
                        bg=self.colors["bg"], fg=self.colors["text"])
        title.pack(pady=20)
        
        # Шкала ЭНЕРГИИ
        energy_frame = tk.Frame(self.mood_frame, bg=self.colors["bg"])
        energy_frame.pack(pady=10, fill="x", padx=50)
        
        tk.Label(energy_frame, text="⚡ Уровень энергии", font=("Segoe UI", 12, "bold"),
                bg=self.colors["bg"], fg=self.colors["text"]).pack()
        tk.Label(energy_frame, text="(насколько вы бодры и готовы действовать)", 
                font=("Segoe UI", 9), bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack()
        
        self.energy_slider = tk.Scale(energy_frame, from_=1, to=10, orient="horizontal",
                                    length=400, font=("Segoe UI", 10))
        self.energy_slider.pack(pady=5)
        self.energy_slider.set(5)
        self.energy_value = tk.Label(energy_frame, text="5/10", font=("Segoe UI", 10),
                                    bg=self.colors["bg"], fg=self.colors["accent_light"])
        self.energy_value.pack()
        
        # Шкала СПОКОЙСТВИЯ
        calm_frame = tk.Frame(self.mood_frame, bg=self.colors["bg"])
        calm_frame.pack(pady=10, fill="x", padx=50)
        
        tk.Label(calm_frame, text="🧘 Уровень спокойствия", font=("Segoe UI", 12, "bold"),
                bg=self.colors["bg"], fg=self.colors["text"]).pack()
        tk.Label(calm_frame, text="(насколько вы расслаблены и свободны от тревоги)", 
                font=("Segoe UI", 9), bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack()
        
        self.calm_slider = tk.Scale(calm_frame, from_=1, to=10, orient="horizontal",
                                    length=400, font=("Segoe UI", 10))
        self.calm_slider.pack(pady=5)
        self.calm_slider.set(5)
        self.calm_value = tk.Label(calm_frame, text="5/10", font=("Segoe UI", 10),
                                    bg=self.colors["bg"], fg=self.colors["accent_light"])
        self.calm_value.pack()
        
        # Шкала МОТИВАЦИИ
        motivation_frame = tk.Frame(self.mood_frame, bg=self.colors["bg"])
        motivation_frame.pack(pady=10, fill="x", padx=50)
        
        tk.Label(motivation_frame, text="🎯 Уровень мотивации", font=("Segoe UI", 12, "bold"),
                bg=self.colors["bg"], fg=self.colors["text"]).pack()
        tk.Label(motivation_frame, text="(насколько вам хочется что-то делать)", 
                font=("Segoe UI", 9), bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack()
        
        self.motivation_slider = tk.Scale(motivation_frame, from_=1, to=10, orient="horizontal",
                                        length=400, font=("Segoe UI", 10))
        self.motivation_slider.pack(pady=5)
        self.motivation_slider.set(5)
        self.motivation_value = tk.Label(motivation_frame, text="5/10", font=("Segoe UI", 10),
                                        bg=self.colors["bg"], fg=self.colors["accent_light"])
        self.motivation_value.pack()
        
        def update_energy(val):
            self.energy_value.config(text=f"{int(float(val))}/10")
        
        def update_calm(val):
            self.calm_value.config(text=f"{int(float(val))}/10")
        
        def update_motivation(val):
            self.motivation_value.config(text=f"{int(float(val))}/10")
        
        self.energy_slider.config(command=update_energy)
        self.calm_slider.config(command=update_calm)
        self.motivation_slider.config(command=update_motivation)
        
        # Кнопка получения рекомендаций
        get_rec_btn = tk.Button(self.mood_frame, text="Получить рекомендации", 
                                font=("Segoe UI", 14, "bold"), bg="#4CAF50", fg="white",
                                command=self.get_recommendations)
        get_rec_btn.pack(pady=20)
        
        # Область для вывода рекомендаций
        self.recommendations_text = scrolledtext.ScrolledText(
            self.mood_frame, width=80, height=18, font=("Segoe UI", 11), wrap=tk.WORD,
            bg=self.colors["card_bg"], fg=self.colors["text"]
        )
        self.recommendations_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        def update_mood_value(val):
            self.mood_value_label.config(text=f"{int(float(val))}/10")
        
        self.mood_slider.config(command=update_mood_value)
        
        # Кнопка получения рекомендаций
        get_rec_btn = tk.Button(center_frame, text="Получить рекомендации", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg=self.colors["success"], fg="white",
                                 relief="flat", padx=30, pady=10,
                                 command=self.get_recommendations)
        get_rec_btn.pack(pady=20)
        
        # Область для вывода рекомендаций
        rec_frame = tk.Frame(self.mood_frame, bg=self.colors["bg"])
        rec_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.recommendations_text = scrolledtext.ScrolledText(
            rec_frame, width=80, height=12, font=("Segoe UI", 11), 
            wrap=tk.WORD, bg=self.colors["card_bg"], fg=self.colors["text"],
            insertbackground=self.colors["text"], relief="flat",
            borderwidth=1, highlightbackground=self.colors["border"]
        )
        self.recommendations_text.pack(fill="both", expand=True)
        
        # Кнопка для предложения расписания
        suggest_btn = tk.Button(self.mood_frame, text="📅 Предложить расписание на день",
                                 font=("Segoe UI", 10), bg=self.colors["warning"], fg="white",
                                 relief="flat", padx=15, pady=5,
                                 command=self.suggest_daily_schedule)
        suggest_btn.pack(pady=10)
    
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
    
    def get_recommendations(self):
        """Получение рекомендаций с учётом трёх показателей и загрузки дня"""
        energy = int(self.energy_slider.get())
        calm = int(self.calm_slider.get())
        motivation = int(self.motivation_slider.get())
        
        today_str = date.today().strftime("%Y-%m-%d")
        schedule = self.db.get_schedule_for_date(today_str)
        schedule_list = [dict(item) for item in schedule] if schedule else []
        
        # Анализ загрузки
        free_slots = self.db.get_free_time_slots(today_str)
        total_tasks = len(schedule_list)
        load_percent = min(100, total_tasks * 15)
        
        # Определяем сезон
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = "зима"
            temp = -10
        elif month in [3, 4, 5]:
            season = "весна"
            temp = 5
        elif month in [6, 7, 8]:
            season = "лето"
            temp = 22
        else:
            season = "осень"
            temp = 8
        
        # Определяем профиль состояния
        state_profile = self.recommendation_engine.get_state_profile(energy, calm, motivation)
        
        # Формируем выходной текст
        output = f"{state_profile['profile_desc']}\n\n"
        output += f"⚡ Энергия: {energy}/10  |  🧘 Спокойствие: {calm}/10  |  🎯 Мотивация: {motivation}/10\n\n"
        output += "━" * 40 + "\n\n"
        
        output += f"📊 АНАЛИЗ ЗАГРУЗКИ ДНЯ\n"
        output += f"   • Запланировано задач: {total_tasks}\n"
        output += f"   • Загрузка дня: {load_percent}%\n"
        output += f"   • Свободных окон: {len(free_slots)}\n"
        output += f"   • Сезон: {season} (средняя температура {temp}°C)\n\n"
        
        output += "⏰ ВАШЕ РАСПИСАНИЕ\n"
        if schedule_list:
            for task in schedule_list:
                status = "✓" if task.get('is_completed') else "○"
                output += f"   {status} {task['start_time']}-{task['end_time']}: {task['task_title']}\n"
        else:
            output += "   Нет запланированных задач\n"
        
        output += "\n💡 РЕКОМЕНДАЦИИ ДЛЯ СВОБОДНОГО ВРЕМЕНИ\n"
        
        if free_slots:
            for slot in free_slots[:4]:
                duration = (int(slot['end'][:2])*60 + int(slot['end'][3:])) - (int(slot['start'][:2])*60 + int(slot['start'][3:]))
                
                if state_profile['profile'] == "идеальное":
                    rec = "🔨 Возьмись за сложную задачу" if duration > 30 else "💪 Сделай короткое дело"
                elif state_profile['profile'] == "тревожное":
                    rec = "🧘 Сделай дыхательную гимнастику или прогулку"
                elif state_profile['profile'] == "усталое":
                    rec = "😴 Отдохни, не делай ничего"
                elif state_profile['profile'] == "апатичное":
                    rec = "🎬 Посмотри мотивирующий контент"
                else:
                    rec = "📋 Сделай запланированные дела"
                
                output += f"   • {slot['start']}-{slot['end']}: {rec}\n"
        else:
            output += "   Нет свободного времени\n"
        
        output += "\n🌿 СОВЕТЫ НА ДЕНЬ\n"
        if state_profile['profile'] == "идеальное":
            output += "   • Используй свою энергию для самых важных дел\n"
            output += "   • Не забывай делать короткие перерывы\n"
        elif state_profile['profile'] == "тревожное":
            output += "   • Попробуй технику 'заземления': 5 вещей, которые ты видишь, 4 на ощупь, 3 слышишь, 2 чувствуешь запах, 1 на вкус\n"
            output += "   • Сделай 10 глубоких вдохов\n"
        elif state_profile['profile'] == "усталое":
            output += "   • Лучшее, что можно сделать — отдохнуть\n"
            output += "   • Не корите себя за низкую продуктивность\n"
        elif state_profile['profile'] == "апатичное":
            output += "   • Начни с самого маленького дела\n"
            output += "   • Попробуй метод 'помидора': 25 минут работы, 5 отдыха\n"
        elif state_profile['profile'] == "выгоревшее":
            output += "   • ВОЗЬМИ ОТПУСК! Твоё состояние критическое\n"
            output += "   • Обратись за поддержкой к близким или специалисту\n"
        else:
            output += "   • Продолжай в том же духе\n"
        
        if temp > 20:
            output += "   • Пей больше воды, избегай солнца в пик\n"
        elif temp < 0:
            output += "   • Одевайся теплее, пей горячий чай\n"
        
        self.recommendations_text.delete(1.0, tk.END)
        self.recommendations_text.insert(tk.END, output)
    
    def suggest_daily_schedule(self):
        """Предложение расписания на день"""
        mood_score = int(self.mood_slider.get())
        suggestions = self.recommendation_engine.get_daily_plan_suggestion(mood_score)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Предлагаемое расписание на день")
        dialog.geometry("450x550")
        dialog.transient(self.root)
        dialog.configure(bg=self.colors["bg"])
        
        text = tk.Text(dialog, wrap="word", font=("Segoe UI", 11),
                        bg=self.colors["card_bg"], fg=self.colors["text"],
                        relief="flat", padx=10, pady=10)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        
        output = f"🌤 Рекомендуемое расписание для настроения {mood_score}/10\n"
        output += "━" * 40 + "\n\n"
        for slot in suggestions:
            output += f"🕐 {slot['time']}  {slot['activity']}\n\n"
        
        text.insert(1.0, output)
        text.config(state="disabled")
        
        tk.Button(dialog, text="Закрыть", command=dialog.destroy,
                  bg=self.colors["accent"], fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=15, pady=5).pack(pady=10)
    
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
        self.refresh_task_list()  # <-- проверьте, что этот метод вызывается
        messagebox.showinfo("Успех", "Задача добавлена!")
    
    def refresh_task_list(self):
        """Обновление списка задач"""
        self.task_listbox.delete(0, tk.END)
        tasks = self.db.get_all_tasks()
        
        print(f"DEBUG: Получено задач из БД: {len(tasks)}")  # временно для отладки
        
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