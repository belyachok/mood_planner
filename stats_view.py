"""
Модуль статистики с процентами выполнения задач
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, date


class StatisticsView:
    """Класс для отображения статистики выполнения задач"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_widgets()
        self.load_stats()
    
    def create_widgets(self):
        # Выбор периода
        period_frame = ttk.LabelFrame(self.parent, text="Период")
        period_frame.pack(fill="x", padx=10, pady=5)
        
        self.period_var = tk.StringVar(value="week")
        ttk.Radiobutton(period_frame, text="Неделя", variable=self.period_var, 
                        value="week", command=self.load_stats).pack(side="left", padx=10)
        ttk.Radiobutton(period_frame, text="Месяц", variable=self.period_var, 
                        value="month", command=self.load_stats).pack(side="left", padx=10)
        ttk.Radiobutton(period_frame, text="Все время", variable=self.period_var, 
                        value="all", command=self.load_stats).pack(side="left", padx=10)
        
        # Область для статистики
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, wrap="word", font=("Arial", 11), height=20)
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_stats(self):
        """Загрузка и отображение статистики"""
        self.stats_text.delete(1.0, tk.END)
        
        period = self.period_var.get()
        
        # Определяем даты
        end_date = date.today()
        if period == "week":
            start_date = end_date - timedelta(days=7)
            period_name = "последние 7 дней"
        elif period == "month":
            start_date = end_date - timedelta(days=30)
            period_name = "последние 30 дней"
        else:
            start_date = date(2020, 1, 1)
            period_name = "все время"
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Получаем все задачи за период
        all_tasks = self.db.get_schedule_for_range(start_str, end_str)
        
        # Статистика
        total_tasks = 0
        completed_tasks = 0
        pending_tasks = 0
        
        # Статистика по категориям
        category_stats = {}
        
        for task in all_tasks:
            total_tasks += 1
            if task['is_completed']:
                completed_tasks += 1
            else:
                pending_tasks += 1
            
            category = task.get('category', 'Другое')
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'completed': 0}
            category_stats[category]['total'] += 1
            if task['is_completed']:
                category_stats[category]['completed'] += 1
        
        # Формируем вывод
        output = "📊 СТАТИСТИКА ВЫПОЛНЕНИЯ ЗАДАЧ\n"
        output += "━" * 40 + "\n\n"
        output += f"📅 Период: {period_name}\n"
        output += f"📆 С {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}\n\n"
        
        if total_tasks > 0:
            completion_percent = (completed_tasks / total_tasks) * 100
            pending_percent = (pending_tasks / total_tasks) * 100
            
            output += f"📋 Всего задач в период: {total_tasks}\n"
            output += f"✅ Выполнено: {completed_tasks} ({completion_percent:.1f}%)\n"
            output += f"⏳ Не выполнено: {pending_tasks} ({pending_percent:.1f}%)\n\n"
            
            # Визуальная шкала выполнения
            bar_len = int(completion_percent / 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            output += f"   [{bar}] {completion_percent:.0f}%\n\n"
            
            # Статистика по категориям
            output += "📂 ПО КАТЕГОРИЯМ:\n"
            for cat, stats in category_stats.items():
                if stats['total'] > 0:
                    cat_percent = (stats['completed'] / stats['total']) * 100
                    output += f"   • {cat}: {stats['completed']}/{stats['total']} ({cat_percent:.0f}%)\n"
            
            output += "\n💡 ВЫВОДЫ И СОВЕТЫ:\n"
            
            if completion_percent < 30:
                output += "   • Продуктивность низкая. Попробуйте ставить меньше задач на день.\n"
                output += "   • Начинайте с самых маленьких и простых дел.\n"
            elif completion_percent < 60:
                output += "   • Средняя продуктивность. Вы на правильном пути!\n"
                output += "   • Старайтесь не отвлекаться во время работы.\n"
            elif completion_percent < 85:
                output += "   • Хорошая продуктивность! Продолжайте в том же духе.\n"
            else:
                output += "   • Отличная продуктивность! Не забывайте про отдых.\n"
            
            if pending_tasks > completed_tasks:
                output += "   • У вас много невыполненных задач. Пересмотрите планы.\n"
        else:
            output += "📭 Нет данных о задачах за выбранный период\n"
            output += "   Добавьте задачи в расписание и отмечайте их выполнение!\n"
        
        self.stats_text.insert(1.0, output)