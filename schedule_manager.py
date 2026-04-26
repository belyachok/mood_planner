"""
Модуль управления расписанием и календарём
С улучшенным дизайном и календарём
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime, timedelta, date
import calendar

from config import CATEGORY_COLORS


class ScheduleManager:
    """Класс для управления отображением и редактированием расписания"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.current_date = date.today()
        self.selected_date = date.today()
        
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
        
        self.create_widgets()
        self.load_schedule()
    
    def create_widgets(self):
        """Создание виджетов расписания с улучшенным дизайном"""
        
        # Основной контейнер
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Создаём панель с календарём и расписанием в два столбца
        paned = ttk.PanedWindow(main_container, orient="horizontal")
        paned.pack(fill="both", expand=True)
        
        # Левый блок - календарь
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=35)
        self.create_calendar(left_frame)
        
        # Правый блок - расписание
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=65)
        self.create_schedule_panel(right_frame)
    
    def create_calendar(self, parent):
        """Создание календаря"""
        
        # Карточка календаря
        calendar_card = tk.Frame(parent, bg=self.colors["card_bg"], 
                                   relief="flat", bd=0)
        calendar_card.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Заголовок с навигацией
        nav_frame = tk.Frame(calendar_card, bg=self.colors["card_bg"])
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        # Кнопки навигации
        prev_btn = tk.Button(nav_frame, text="◀", font=("Segoe UI", 12, "bold"),
                              bg=self.colors["accent"], fg="white",
                              relief="flat", padx=10, pady=5,
                              command=self.prev_month)
        prev_btn.pack(side="left")
        
        self.month_label = tk.Label(nav_frame, font=("Segoe UI", 14, "bold"),
                                      bg=self.colors["card_bg"], fg=self.colors["text"])
        self.month_label.pack(side="left", expand=True)
        
        next_btn = tk.Button(nav_frame, text="▶", font=("Segoe UI", 12, "bold"),
                              bg=self.colors["accent"], fg="white",
                              relief="flat", padx=10, pady=5,
                              command=self.next_month)
        next_btn.pack(side="right")
        
        # Дни недели
        days_frame = tk.Frame(calendar_card, bg=self.colors["card_bg"])
        days_frame.pack(fill="x", padx=10, pady=5)

        weekdays = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
        for i, day in enumerate(weekdays):
            color = self.colors["danger"] if i >= 5 else self.colors["text"]
            lbl = tk.Label(days_frame, text=day, font=("Segoe UI", 10, "bold"),
                        bg=self.colors["card_bg"], fg=color)
            lbl.grid(row=0, column=i, padx=1, pady=2, sticky="nsew")
            days_frame.columnconfigure(i, weight=1, uniform="col")

        # Устанавливаем высоту для строки дней недели
        days_frame.rowconfigure(0, weight=1)
                
        # Сетка календаря
        self.calendar_grid = tk.Frame(calendar_card, bg=self.colors["card_bg"])
        self.calendar_grid.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Индикатор выбранной даты
        self.selected_label = tk.Label(calendar_card, 
                                         text=f"Выбрано: {self.selected_date.strftime('%d.%m.%Y')}",
                                         font=("Segoe UI", 10),
                                         bg=self.colors["card_bg"], fg=self.colors["text_secondary"])
        self.selected_label.pack(pady=5)
        
        # Обновляем календарь
        self.update_calendar()
    
    def update_calendar(self):
        """Обновление отображения календаря"""
        # Очищаем сетку
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
        
        # Получаем данные о календаре
        year = self.current_date.year
        month = self.current_date.month
        
        # Заголовок месяца
        month_name = calendar.month_name[month]
        self.month_label.config(text=f"{month_name} {year}")
        
        # Получаем первый день месяца и количество дней
        first_weekday = calendar.monthrange(year, month)[0]
        # В Python понедельник = 0, но в calendar понедельник = 0? Проверим
        # calendar.monthrange возвращает (день_недели_первого_дня, количество_дней)
        # где день_недели: 0=пн, 1=вт, ..., 6=вс
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Получаем задачи за месяц для подсветки
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)
        schedule_data = self.db.get_schedule_for_range(
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        # Группируем задачи по дням
        tasks_by_day = {}
        for item in schedule_data:
            day_num = int(item['date'].split('-')[2])
            if day_num not in tasks_by_day:
                tasks_by_day[day_num] = []
            tasks_by_day[day_num].append(item)
        
        # Создаём ячейки календаря
        row = 0
        col = 0
        
        # Пустые ячейки до первого дня
        for i in range(first_weekday):
            empty_cell = tk.Frame(self.calendar_grid, width=50, height=60,
                                   bg=self.colors["card_bg"])
            empty_cell.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            empty_cell.grid_propagate(False)
            col += 1
        
        # Дни месяца
        for day in range(1, days_in_month + 1):
            cell_date = date(year, month, day)
            is_today = cell_date == date.today()
            is_selected = cell_date == self.selected_date
            
            # Определяем цвет фона
            # Определяем цвет фона
            if is_selected:
                bg_color = self.colors["accent"]      # фиолетовый для выбранной даты
                fg_color = "white"
            elif is_today:
                bg_color = "#2ecc71"                  # зелёный для сегодняшнего дня
                fg_color = "white"
            else:
                bg_color = self.colors["card_bg"]     # тёмно-серый для обычных дней
                fg_color = self.colors["text"]
            
            # Создаём ячейку с одинаковыми размерами
            cell = tk.Frame(self.calendar_grid, bg=bg_color, relief="flat", bd=1,
                            highlightbackground=self.colors["border"], highlightthickness=1)
            cell.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            
            # Настраиваем одинаковую высоту и ширину для всех ячеек
            cell.grid_propagate(True)
            cell.config(width=70, height=70)
            
            # Число
            day_label = tk.Label(cell, text=str(day), font=("Segoe UI", 11, "bold"),
                                bg=bg_color, fg=fg_color)
            day_label.pack(anchor="nw", padx=5, pady=2)
            
            # Индикаторы задач
            if day in tasks_by_day:
                indicators_frame = tk.Frame(cell, bg=bg_color)
                indicators_frame.pack(fill="both", expand=True, padx=2, pady=2)
                
                completed = sum(1 for t in tasks_by_day[day] if t['is_completed'])
                total = len(tasks_by_day[day])
                
                # Показываем только количество задач
                task_info = tk.Label(indicators_frame, text=f"📋 {completed}/{total}",
                                    font=("Segoe UI", 8), bg=bg_color, fg=self.colors["text_secondary"])
                task_info.pack()
            
            # Привязываем клик
            cell.bind("<Button-1>", lambda e, d=cell_date: self.select_date(d))
            day_label.bind("<Button-1>", lambda e, d=cell_date: self.select_date(d))
            
            col += 1
            if col > 6:
                col = 0
                row += 1

        # Настройка веса строк и столбцов для равномерного растяжения
        for i in range(7):
            self.calendar_grid.columnconfigure(i, weight=1, uniform="col")
        for i in range(6):
            self.calendar_grid.rowconfigure(i, weight=1, uniform="row")
    
    def select_date(self, target_date):
        """Выбор даты в календаре"""
        self.selected_date = target_date
        self.current_date = target_date
        self.selected_label.config(text=f"Выбрано: {target_date.strftime('%d.%m.%Y')}")
        self.update_calendar()
        self.load_schedule()
    
    def prev_month(self):
        """Предыдущий месяц"""
        year = self.current_date.year
        month = self.current_date.month
        
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        
        # Безопасно создаём дату первого числа следующего месяца
        self.current_date = date(year, month, 1)
        self.update_calendar()

    def next_month(self):
        """Следующий месяц"""
        year = self.current_date.year
        month = self.current_date.month
        
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        
        # Безопасно создаём дату первого числа следующего месяца
        self.current_date = date(year, month, 1)
        self.update_calendar()
    
    def create_schedule_panel(self, parent):
        """Создание панели расписания"""
        
        # Карточка расписания
        schedule_card = tk.Frame(parent, bg=self.colors["card_bg"])
        schedule_card.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Заголовок с датой
        header_frame = tk.Frame(schedule_card, bg=self.colors["card_bg"])
        header_frame.pack(fill="x", padx=15, pady=10)
        
        weekday_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        weekday_num = self.selected_date.weekday()
        
        self.date_header = tk.Label(header_frame, 
                                    text=f"{weekday_names[weekday_num]}, {self.selected_date.strftime('%d %B %Y')}",
                                    font=("Segoe UI", 16, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["text"])
        self.date_header.pack(side="left")
        
        # Кнопка добавления
        add_btn = tk.Button(header_frame, text="+ Добавить задачу", 
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors["accent"], fg="white",
                            relief="flat", padx=15, pady=5,
                            command=self.open_add_task_dialog)
        add_btn.pack(side="right")
        
        # Область для списка задач (с прокруткой)
        tasks_container = tk.Frame(schedule_card, bg=self.colors["card_bg"])
        tasks_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаём canvas с прокруткой
        self.tasks_canvas = tk.Canvas(tasks_container, bg=self.colors["card_bg"],
                                    highlightthickness=0)
        scrollbar = ttk.Scrollbar(tasks_container, orient="vertical", 
                                command=self.tasks_canvas.yview)
        self.scrollable_tasks = tk.Frame(self.tasks_canvas, bg=self.colors["card_bg"])
        
        self.scrollable_tasks.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))
        )
        
        # Привязываем изменение размера canvas к изменению размера окна
        def on_canvas_configure(event):
            self.tasks_canvas.itemconfig("tasks_window", width=event.width)
        
        self.tasks_canvas.bind("<Configure>", on_canvas_configure)
        
        self.tasks_canvas.create_window((0, 0), window=self.scrollable_tasks, anchor="nw", tags=("tasks_window",))
        self.tasks_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.tasks_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.schedule_frame = self.scrollable_tasks
        
        # Кнопка быстрого предложения расписания
        quick_suggest = tk.Button(schedule_card, text="✨ Предложить расписание на день",
                                font=("Segoe UI", 10),
                                bg=self.colors["warning"], fg="white",
                                relief="flat", pady=8,
                                command=self.suggest_schedule)
        quick_suggest.pack(fill="x", padx=10, pady=10)
    
    def load_schedule(self):
        """Загрузка расписания на выбранную дату"""
        # Обновляем заголовок
        weekday_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        weekday_num = self.selected_date.weekday()
        self.date_header.config(text=f"{weekday_names[weekday_num]}, {self.selected_date.strftime('%d %B %Y')}")
        
        # Очищаем старые виджеты
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        # Получаем расписание из БД
        schedule = self.db.get_schedule_for_date(self.selected_date.strftime("%Y-%m-%d"))
        
        if not schedule:
            empty_frame = tk.Frame(self.schedule_frame, bg=self.colors["card_bg"])
            empty_frame.pack(fill="both", expand=True, pady=50)
            
            empty_icon = tk.Label(empty_frame, text="📭", font=("Segoe UI", 48),
                                   bg=self.colors["card_bg"], fg=self.colors["text_secondary"])
            empty_icon.pack()
            
            empty_label = tk.Label(empty_frame, text="Нет запланированных задач на этот день",
                                    font=("Segoe UI", 12),
                                    bg=self.colors["card_bg"], fg=self.colors["text_secondary"])
            empty_label.pack(pady=10)
            
            hint_label = tk.Label(empty_frame, text="Нажмите кнопку '+' чтобы добавить задачу",
                                   font=("Segoe UI", 10),
                                   bg=self.colors["card_bg"], fg=self.colors["accent_light"])
            hint_label.pack()
            return
        
        # Сортируем по времени
        schedule = sorted(schedule, key=lambda x: x['start_time'])
        
        # Создаём строки расписания
        for item in schedule:
            self.create_schedule_row(item)
    
    def create_schedule_row(self, item):
        """Создание стильной строки расписания"""
        
        # Карточка задачи
        task_card = tk.Frame(self.schedule_frame, bg=self.colors["bg"], 
                            relief="flat", bd=1,
                            highlightbackground=self.colors["border"], 
                            highlightthickness=1)
        task_card.pack(fill="x", expand=True, padx=5, pady=3)  # ← expand=True
        
        # Внутренний контейнер
        inner = tk.Frame(task_card, bg=self.colors["bg"])
        inner.pack(fill="x", expand=True, padx=10, pady=8)
        
        # Левая часть с временем
        time_frame = tk.Frame(inner, bg=self.colors["bg"])
        time_frame.pack(side="left", fill="y")
        
        time_label = tk.Label(time_frame, text=f"{item['start_time']} - {item['end_time']}",
                            font=("Segoe UI", 11, "bold"),
                            bg=self.colors["bg"], fg=self.colors["accent_light"])
        time_label.pack()
        
        # Центральная часть с задачей - растягивается
        task_frame = tk.Frame(inner, bg=self.colors["bg"])
        task_frame.pack(side="left", fill="x", expand=True, padx=15)
        
        title = item['task_title']
        if item['is_completed']:
            title = f"✓ {title}"
            title_color = self.colors["success"]
        else:
            title_color = self.colors["text"]
        
        title_label = tk.Label(task_frame, text=title, font=("Segoe UI", 11),
                            bg=self.colors["bg"], fg=title_color)
        title_label.pack(anchor="w")
        
        # Категория и энергия
        meta_frame = tk.Frame(task_frame, bg=self.colors["bg"])
        meta_frame.pack(anchor="w")
        
        category = item['category']
        cat_color = CATEGORY_COLORS.get(category, "#6b7280")
        cat_badge = tk.Label(meta_frame, text=category, font=("Segoe UI", 8),
                            bg=cat_color, fg="white", padx=6, pady=2)
        cat_badge.pack(side="left")
        
        energy = item['energy_level'] or 5
        energy_text = "⚡" * (energy // 2) + "·" * ((10 - energy) // 2)
        energy_label = tk.Label(meta_frame, text=energy_text, font=("Segoe UI", 9),
                            bg=self.colors["bg"], fg=self.colors["warning"])
        energy_label.pack(side="left", padx=10)
        
        # Правая часть с кнопками
        buttons_frame = tk.Frame(inner, bg=self.colors["bg"])
        buttons_frame.pack(side="right", fill="y")
        
        if not item['is_completed']:
            complete_btn = tk.Button(buttons_frame, text="✓ Выполнено",
                                    font=("Segoe UI", 9),
                                    bg=self.colors["success"], fg="white",
                                    relief="flat", padx=10, pady=3,
                                    command=lambda i=item['id']: self.complete_task(i))
            complete_btn.pack(side="left", padx=2)
            
            postpone_btn = tk.Button(buttons_frame, text="😴 Я устал",
                                    font=("Segoe UI", 9),
                                    bg=self.colors["warning"], fg="white",
                                    relief="flat", padx=8, pady=3,
                                    command=lambda i=item['id'], 
                                        t=item['task_title'],
                                        s=item['start_time'],
                                        e=item['end_time'],
                                        c=item['category'],
                                        el=item['energy_level'] if item['energy_level'] else 5: 
                                    self.postpone_task(i, t, s, e, c, el))
            postpone_btn.pack(side="left", padx=2)
        
        delete_btn = tk.Button(buttons_frame, text="🗑",
                            font=("Segoe UI", 9),
                            bg=self.colors["danger"], fg="white",
                            relief="flat", padx=8, pady=3,
                            command=lambda i=item['id']: self.delete_task(i))
        delete_btn.pack(side="left", padx=2)
        
        if item['is_completed']:
            completed_badge = tk.Label(buttons_frame, text="✅ Выполнено",
                                    font=("Segoe UI", 9),
                                    bg=self.colors["success"], fg="white",
                                    padx=8, pady=3)
            completed_badge.pack(side="left")
    

    def postpone_task(self, item_id, task_title, old_start, old_end, category="Без категории", energy_level=5):
        """Перенос задачи на указанное количество дней вперёд"""
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Перенос задачи")
        dialog.geometry("350x220")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.colors["bg"])
        
        tk.Label(dialog, text=f"Задача: {task_title}", 
                font=("Segoe UI", 11, "bold"),
                bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=10)
        
        tk.Label(dialog, text="На сколько дней перенести?", 
                bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack()
        
        days_var = tk.IntVar(value=2)
        days_spinbox = tk.Spinbox(dialog, from_=1, to=7, textvariable=days_var,
                                font=("Segoe UI", 12), width=5)
        days_spinbox.pack(pady=10)
        
        def confirm_postpone():
            days = days_var.get()
            current_date = self.selected_date
            new_date = current_date + timedelta(days=days)
            
            # Рассчитываем длительность задачи в минутах
            start_hour = int(old_start[:2])
            start_min = int(old_start[3:])
            end_hour = int(old_end[:2])
            end_min = int(old_end[3:])
            duration = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
            
            self.db.delete_schedule_item(item_id)
            self.db.add_to_schedule(
                None, task_title, category, energy_level, 
                new_date.strftime("%Y-%m-%d"),
                old_start, old_end, duration
            )
            
            dialog.destroy()
            self.load_schedule()
            self.update_calendar()
            messagebox.showinfo("Перенос", f"Задача \"{task_title}\" перенесена на {new_date.strftime('%d.%m.%Y')}")
        
        tk.Button(dialog, text="Перенести", command=confirm_postpone,
                bg=self.colors["accent"], fg="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat", padx=15, pady=5).pack(pady=15)
        
        tk.Button(dialog, text="Отмена", command=dialog.destroy,
                bg=self.colors["danger"], fg="white",
                font=("Segoe UI", 10),
                relief="flat", padx=15, pady=5).pack(pady=5)

    def complete_task(self, item_id):
        """Отметить задачу выполненной"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Оценка настроения")
        dialog.geometry("320x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Стилизация диалога
        dialog.configure(bg=self.colors["bg"])
        
        tk.Label(dialog, text="Как настроение перед выполнением?", 
                 font=("Segoe UI", 12),
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=15)
        
        mood_var = tk.IntVar(value=5)
        mood_slider = tk.Scale(dialog, from_=1, to=10, orient="horizontal",
                                variable=mood_var, length=250,
                                bg=self.colors["bg"], fg=self.colors["text"],
                                troughcolor=self.colors["border"])
        mood_slider.pack(pady=10)
        
        
        def update_value(val):
            mood_value.config(text=f"{int(float(val))}/10")
        
        mood_slider.config(command=update_value)
        
        def confirm():
            self.db.complete_schedule_item(item_id, mood_var.get())
            dialog.destroy()
            self.load_schedule()
            self.update_calendar()
            messagebox.showinfo("Успех", "Задача отмечена как выполненная!")
        
        tk.Button(dialog, text="Подтвердить", command=confirm,
                  bg=self.colors["success"], fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=20, pady=5).pack(pady=15)

    def delete_task(self, item_id):
        """Удалить задачу из расписания"""
        if messagebox.askyesno("Подтверждение", "Удалить задачу из расписания?"):
            self.db.delete_schedule_item(item_id)
            self.load_schedule()
            self.update_calendar()

    def open_add_task_dialog(self):
        """Диалог добавления задачи в расписание"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить задачу")
        dialog.geometry("450x550")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.colors["bg"])
        
        # Заголовок
        tk.Label(dialog, text="Добавить задачу в расписание", 
                 font=("Segoe UI", 14, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=10)
        
        # Вкладки: существующая / новая
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Вкладка "Выбрать задачу"
        existing_frame = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(existing_frame, text="📋 Выбрать задачу")
        
        tasks = self.db.get_all_tasks()
        
        if tasks:
            task_listbox = tk.Listbox(existing_frame, font=("Segoe UI", 10),
                                       bg=self.colors["card_bg"], fg=self.colors["text"],
                                       selectbackground=self.colors["accent"])
            task_listbox.pack(fill="both", expand=True, padx=10, pady=10)
            
            for task in tasks:
                display = f"{task['title']} [{task['category']}] ⚡{task['energy_level']} {task.get('estimated_duration', 30)}мин"
                task_listbox.insert(tk.END, display)
        else:
            tk.Label(existing_frame, text="Нет сохранённых задач.\nСоздайте новую на следующей вкладке",
                     font=("Segoe UI", 10), bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack(pady=50)
            task_listbox = None
        
        # Вкладка "Новая задача"
        new_frame = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(new_frame, text="✨ Новая задача")
        
        # Форма новой задачи
        form_frame = tk.Frame(new_frame, bg=self.colors["bg"])
        form_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(form_frame, text="Название:", bg=self.colors["bg"], fg=self.colors["text"]).grid(row=0, column=0, sticky="w", pady=5)
        new_title = tk.Entry(form_frame, font=("Segoe UI", 10), width=30)
        new_title.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Категория:", bg=self.colors["bg"], fg=self.colors["text"]).grid(row=1, column=0, sticky="w", pady=5)
        new_category = ttk.Combobox(form_frame, values=list(CATEGORY_COLORS.keys()), width=27)
        new_category.grid(row=1, column=1, pady=5)
        new_category.set("Работа")
        
        tk.Label(form_frame, text="Энергозатратность (1-10):", bg=self.colors["bg"], fg=self.colors["text"]).grid(row=2, column=0, sticky="w", pady=5)
        new_energy = tk.Scale(form_frame, from_=1, to=10, orient="horizontal", length=200)
        new_energy.grid(row=2, column=1, pady=5)
        new_energy.set(5)
        
        tk.Label(form_frame, text="Длительность (мин):", bg=self.colors["bg"], fg=self.colors["text"]).grid(row=3, column=0, sticky="w", pady=5)
        new_duration = ttk.Spinbox(form_frame, from_=15, to=240, increment=15, width=10)
        new_duration.grid(row=3, column=1, pady=5)
        new_duration.set(30)
        
        # Время
        time_frame = tk.LabelFrame(dialog, text="Время выполнения", 
                                    font=("Segoe UI", 10, "bold"),
                                    bg=self.colors["bg"], fg=self.colors["text"])
        time_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(time_frame, text="Время начала:", bg=self.colors["bg"], fg=self.colors["text"]).pack(side="left", padx=5)
        start_hour = ttk.Spinbox(time_frame, from_=0, to=23, width=3)
        start_hour.pack(side="left")
        tk.Label(time_frame, text=":", bg=self.colors["bg"], fg=self.colors["text"]).pack(side="left")
        start_min = ttk.Spinbox(time_frame, from_=0, to=55, increment=30, width=3)
        start_min.pack(side="left")
        start_hour.set(9)
        start_min.set(0)
        
        # Кнопка добавления
        def add_to_schedule():
            target_date = self.selected_date.strftime("%Y-%m-%d")
            
            # Защита от некорректных значений
            try:
                hour = int(start_hour.get())
                minute = int(start_min.get())
                if hour < 0 or hour > 23:
                    hour = 9
                if minute < 0 or minute > 55:
                    minute = 0
            except:
                hour = 9
                minute = 0
            
            start_time = f"{hour:02d}:{minute:02d}"
            duration_min = int(new_duration.get())
            
            start = datetime.strptime(start_time, "%H:%M")
            end = start + timedelta(minutes=duration_min)
            end_time = end.strftime("%H:%M")

            # Если выбрана существующая задача
            if task_listbox and task_listbox.curselection():
                idx = task_listbox.curselection()[0]
                task = tasks[idx]
                self.db.add_to_schedule(
                    task['id'], task['title'], task['category'],
                    task['energy_level'], target_date, start_time, end_time, duration_min
                )
                messagebox.showinfo("Успех", "Задача добавлена в расписание!")
                dialog.destroy()
                self.load_schedule()
                self.update_calendar()
            # Если создана новая
            elif new_title.get().strip():
                task_id = self.db.add_task(
                    new_title.get(), new_category.get(), new_energy.get(), duration_min
                )
                self.db.add_to_schedule(
                    task_id, new_title.get(), new_category.get(),
                    new_energy.get(), target_date, start_time, end_time, duration_min
                )
                messagebox.showinfo("Успех", "Новая задача создана и добавлена в расписание!")
                dialog.destroy()
                self.load_schedule()
                self.update_calendar()
            else:
                messagebox.showwarning("Внимание", "Выберите или создайте задачу!")
        
        tk.Button(dialog, text="➕ Добавить в расписание", command=add_to_schedule,
                  bg=self.colors["accent"], fg="white",
                  font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=20, pady=8).pack(pady=15)

    def suggest_schedule(self):
        """Предложить расписание на день на основе настроения, загрузки и сезона"""
        from datetime import datetime
        
        # Берём месяц из ВЫБРАННОЙ даты
        month = self.selected_date.month
        
        # Определяем сезон, температуру и иконку для каждого месяца
        if month == 12 or month == 1 or month == 2:
            if month == 12:
                temp = -8
                season = "зима (декабрь)"
            elif month == 1:
                temp = -12
                season = "зима (январь)"
            else:  # февраль
                temp = -10
                season = "зима (февраль)"
            weather_icon = "❄️"
            weather_tip = "На улице холодно, одевайтесь теплее. Рекомендуются indoor-активности."
        
        elif month == 3 or month == 4 or month == 5:
            if month == 3:
                temp = 0
                season = "весна (март)"
            elif month == 4:
                temp = 8
                season = "весна (апрель)"
            else:  # май
                temp = 15
                season = "весна (май)"
            weather_icon = "🌱"
            weather_tip = "Погода переменчива, берите зонт. Хорошее время для прогулок."
        
        elif month == 6 or month == 7 or month == 8:
            if month == 6:
                temp = 20
                season = "лето (июнь)"
            elif month == 7:
                temp = 25
                season = "лето (июль)"
            else:  # август
                temp = 22
                season = "лето (август)"
            weather_icon = "☀️"
            weather_tip = "Тепло, отличное время для активного отдыха на свежем воздухе."
        
        else:  # 9, 10, 11
            if month == 9:
                temp = 12
                season = "осень (сентябрь)"
            elif month == 10:
                temp = 5
                season = "осень (октябрь)"
            else:  # ноябрь
                temp = 0
                season = "осень (ноябрь)"
            weather_icon = "🍂"
            weather_tip = "Прохладно, одевайтесь по погоде. Самое время для культурного досуга."
        
        # Анализируем загрузку дня
# Анализируем загрузку дня по ВЫБРАННОЙ дате в календаре
        target_date_str = self.selected_date.strftime("%Y-%m-%d")
        schedule = self.db.get_schedule_for_date(target_date_str)
        schedule_list = [dict(item) for item in schedule] if schedule else []
        total_tasks = len(schedule_list)
        
        # Расчёт загрузки
        total_minutes = 0
        for task in schedule_list:
            start = int(task['start_time'][:2]) * 60 + int(task['start_time'][3:])
            end = int(task['end_time'][:2]) * 60 + int(task['end_time'][3:])
            total_minutes += end - start
        load_percent = min(100, int((total_minutes / (14 * 60)) * 100)) if total_minutes > 0 else 0
        
        # Создаём диалог
        dialog = tk.Toplevel(self.parent)
        dialog.title("Создание расписания")
        dialog.geometry("500x480")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.configure(bg=self.colors["bg"])
        
        # Информация о сезоне и загрузке
        tk.Label(dialog, text=f"{weather_icon} {season.upper()} | Средняя температура: {temp}°C", 
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["bg"], fg=self.colors["accent_light"]).pack(pady=10)
        
        tk.Label(dialog, text=f"📊 Загрузка дня: {load_percent}%", 
                font=("Segoe UI", 11),
                bg=self.colors["bg"], fg=self.colors["text"]).pack()
        
        tk.Label(dialog, text=f"⏰ Запланировано задач: {total_tasks}", 
                font=("Segoe UI", 11),
                bg=self.colors["bg"], fg=self.colors["text"]).pack()
        
        tk.Label(dialog, text=f"🌿 {weather_tip}", 
                font=("Segoe UI", 10),
                bg=self.colors["bg"], fg=self.colors["warning"]).pack(pady=10)
        
        separator = tk.Frame(dialog, height=2, bg=self.colors["border"])
        separator.pack(fill="x", padx=20, pady=10)
        
        # Заголовок
        tk.Label(dialog, text="Оцените своё состояние:", 
                font=("Segoe UI", 12, "bold"),
                bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=10)

        # Контейнер для всех шкал с выравниванием по сетке
        scales_frame = tk.Frame(dialog, bg=self.colors["bg"])
        scales_frame.pack(fill="x", padx=40, pady=10)

        # Переменные для трёх показателей
        energy_var = tk.IntVar(value=5)
        calm_var = tk.IntVar(value=5)
        motivation_var = tk.IntVar(value=5)

        # Шкала ЭНЕРГИИ (строка 0)
        tk.Label(scales_frame, text="⚡ Энергия:", font=("Segoe UI", 10),
                bg=self.colors["bg"], fg=self.colors["text"]).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        energy_slider = tk.Scale(scales_frame, from_=1, to=10, orient="horizontal",
                                variable=energy_var, length=200,
                                bg=self.colors["bg"], fg=self.colors["text"],
                                troughcolor=self.colors["border"], highlightthickness=0)
        energy_slider.grid(row=0, column=1, padx=10, pady=5)

        energy_value = tk.Label(scales_frame, text="5", width=3,
                                bg=self.colors["bg"], fg=self.colors["accent_light"],
                                font=("Segoe UI", 10, "bold"))
        energy_value.grid(row=0, column=2, padx=5, pady=5)

        # Шкала СПОКОЙСТВИЯ (строка 1)
        tk.Label(scales_frame, text="🧘 Спокойствие:", font=("Segoe UI", 10),
                bg=self.colors["bg"], fg=self.colors["text"]).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        calm_slider = tk.Scale(scales_frame, from_=1, to=10, orient="horizontal",
                                variable=calm_var, length=200,
                                bg=self.colors["bg"], fg=self.colors["text"],
                                troughcolor=self.colors["border"], highlightthickness=0)
        calm_slider.grid(row=1, column=1, padx=10, pady=5)

        calm_value = tk.Label(scales_frame, text="5", width=3,
                            bg=self.colors["bg"], fg=self.colors["accent_light"],
                            font=("Segoe UI", 10, "bold"))
        calm_value.grid(row=1, column=2, padx=5, pady=5)

        # Шкала МОТИВАЦИИ (строка 2)
        tk.Label(scales_frame, text="🎯 Мотивация:", font=("Segoe UI", 10),
                bg=self.colors["bg"], fg=self.colors["text"]).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        motivation_slider = tk.Scale(scales_frame, from_=1, to=10, orient="horizontal",
                                    variable=motivation_var, length=200,
                                    bg=self.colors["bg"], fg=self.colors["text"],
                                    troughcolor=self.colors["border"], highlightthickness=0)
        motivation_slider.grid(row=2, column=1, padx=10, pady=5)

        motivation_value = tk.Label(scales_frame, text="5", width=3,
                                    bg=self.colors["bg"], fg=self.colors["accent_light"],
                                    font=("Segoe UI", 10, "bold"))
        motivation_value.grid(row=2, column=2, padx=5, pady=5)

        # Функции обновления значений
        def update_energy(val):
            energy_value.config(text=str(int(float(val))))
        def update_calm(val):
            calm_value.config(text=str(int(float(val))))
        def update_motivation(val):
            motivation_value.config(text=str(int(float(val))))

        energy_slider.config(command=update_energy)
        calm_slider.config(command=update_calm)
        motivation_slider.config(command=update_motivation)

        # Настройка веса столбцов для равномерного распределения
        scales_frame.columnconfigure(0, weight=1)
        scales_frame.columnconfigure(1, weight=2)
        scales_frame.columnconfigure(2, weight=0)
        
# Показываем уже запланированные задачи
        if schedule_list:
            tk.Label(dialog, text="📋 Уже запланировано на этот день:", 
                    font=("Segoe UI", 10, "bold"),
                    bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=(10,0))
            
            tasks_frame = tk.Frame(dialog, bg=self.colors["bg"])
            tasks_frame.pack(pady=5)
            
            for task in schedule_list[:3]:  # показываем не более 3 задач
                tk.Label(tasks_frame, text=f"   • {task['start_time']}-{task['end_time']}: {task['task_title']}",
                        font=("Segoe UI", 9),
                        bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack()
            
            if len(schedule_list) > 3:
                tk.Label(tasks_frame, text=f"   ... и ещё {len(schedule_list) - 3} задач",
                        font=("Segoe UI", 9),
                        bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack()

        
        def apply_suggestion():
            energy = energy_var.get()
            calm = calm_var.get()
            motivation = motivation_var.get()
            avg_mood = (energy + calm + motivation) // 3
            
            # Базовая сетка расписания
            base_schedule = [
                ("08:00", "09:00", "🌅 Утро: зарядка и завтрак"),
                ("09:00", "12:00", "💼 Рабочие задачи"),
                ("12:00", "13:00", "🍲 Обед и отдых"),
                ("13:00", "15:00", "📊 Продолжение работы"),
                ("15:00", "17:00", "🎯 Важные дела"),
                ("17:00", "18:00", "🏃 Активность/спорт"),
                ("18:00", "19:30", "🍽 Ужин"),
                ("19:30", "21:30", "🎮 Отдых, хобби"),
                ("21:30", "22:30", "😴 Подготовка ко сну")
            ]
            
            # Корректировка в зависимости от настроения (avg_mood) и сезона
            if avg_mood >= 7:
                base_schedule[1] = ("09:00", "12:00", "💪 САМЫЕ ВАЖНЫЕ ЗАДАЧИ (3 часа)")
                base_schedule[4] = ("15:00", "17:00", "🎯 Дополнительные задачи")
                if "лето" in season or "весна" in season:
                    base_schedule[5] = ("17:00", "18:30", "🏃 Активный отдых на улице")
            elif avg_mood >= 4:
                base_schedule[1] = ("09:00", "11:00", "📋 Несложные задачи")
                base_schedule[2] = ("11:00", "12:00", "☕ Перерыв")
                base_schedule[4] = ("14:00", "16:00", "🎨 Творческая задача")
            else:
                base_schedule[0] = ("08:30", "09:30", "🛌 Медленное пробуждение")
                base_schedule[1] = ("09:30", "11:00", "🧹 Одно простое дело")
                base_schedule[2] = ("11:00", "12:00", "📺 Отдых")
                base_schedule[4] = ("14:00", "15:00", "🎵 Приятное занятие")
                base_schedule[5] = ("15:00", "17:00", "😴 Время для себя")
            
            target_date = self.selected_date.strftime("%Y-%m-%d")
            
            # Сначала удаляем старые рекомендации
            old_schedule = self.db.get_schedule_for_date(target_date)
            for item in old_schedule:
                if item['category'] == "Рекомендация":
                    self.db.delete_schedule_item(item['id'])
            
            # Добавляем новые
            for start, end, title in base_schedule:
                duration = (int(end[:2])*60 + int(end[3:])) - (int(start[:2])*60 + int(start[3:]))
                self.db.add_to_schedule(None, title, "Рекомендация", None, target_date, start, end, duration)
            
            dialog.destroy()
            self.load_schedule()
            self.update_calendar()
            messagebox.showinfo("Успех", f"✅ Расписание на {self.selected_date.strftime('%d.%m.%Y')} создано с учётом сезона '{season}'!")