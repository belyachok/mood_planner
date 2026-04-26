"""
Модуль статистики и графиков
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, date


class StatisticsView:
    """Класс для отображения статистики"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_widgets()
        self.load_stats()
    
    def create_widgets(self):
        """Создание виджетов статистики"""
        
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
        
        # Статистика выполнения задач
        completion_stats = self.db.get_completion_stats(start_str, end_str)
        
        # Формируем текст
        output = "📊 СТАТИСТИКА ВЫПОЛНЕНИЯ ЗАДАЧ\n"
        output += "━" * 40 + "\n\n"
        output += f"📅 Период: {period_name}\n"
        output += f"📆 С {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}\n\n"
        
        if completion_stats:
            total_all = 0
            completed_all = 0
            for stat in completion_stats:
                total_all += stat['total']
                completed_all += stat['completed']
            
            if total_all > 0:
                output += f"📋 Всего задач: {total_all}\n"
                output += f"✅ Выполнено: {completed_all}\n"
                output += f"📈 Общая продуктивность: {completed_all/total_all*100:.1f}%\n\n"
            
            output += "📅 По дням:\n"
            for stat in completion_stats[-7:]:
                percent = stat['completed']/stat['total']*100 if stat['total'] > 0 else 0
                # Визуальная полоса
                bar_len = int(percent / 10)
                bar = "█" * bar_len + "░" * (10 - bar_len)
                output += f"   {stat['date']}: {bar} {percent:.0f}% ({stat['completed']}/{stat['total']})\n"
        else:
            output += "📭 Нет данных о выполненных задачах\n"
            output += "   Добавьте задачи в расписание и отмечайте их выполнение!\n"
        
        # Советы
        output += "\n💡 СОВЕТЫ\n"
        output += "━" * 40 + "\n"
        
        if completion_stats and total_all > 0:
            if completed_all/total_all < 0.5:
                output += "• Попробуйте планировать меньше задач на день\n"
                output += "• Начинайте с самых маленьких и простых дел\n"
            elif completed_all/total_all > 0.8:
                output += "• Отличная продуктивность! Не забывайте про отдых\n"
            else:
                output += "• Хороший результат! Продолжайте в том же духе\n"
        else:
            output += "• Начните с добавления задач в расписание\n"
            output += "• Планируйте 2-3 задачи на первый день\n"
        
        self.stats_text.insert(1.0, output)
        self.stats_text.config(state="disabled")