"""
Расширенный модуль работы с базой данных
"""

import sqlite3
import os
from datetime import datetime, date, timedelta


class Database:
    """Класс для работы с БД"""
    
    def __init__(self, db_name):
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Создание всех таблиц"""
        
        # Таблица задач (шаблонов)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                energy_level INTEGER NOT NULL,
                estimated_duration INTEGER DEFAULT 30,
                created_date TEXT NOT NULL
            )
        ''')
        
        # Таблица расписания (запланированные задачи)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                task_title TEXT NOT NULL,
                category TEXT NOT NULL,
                energy_level INTEGER,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration INTEGER,
                is_completed INTEGER DEFAULT 0,
                mood_before INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        
        # Таблица ежедневных целей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                goal_text TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 1
            )
        ''')
        
        # Таблица привычек
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                frequency TEXT NOT NULL, -- daily, weekly
                target_count INTEGER DEFAULT 1,
                current_streak INTEGER DEFAULT 0,
                created_date TEXT NOT NULL
            )
        ''')
        
        # Таблица выполнения привычек
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_completion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        ''')
        
        self.conn.commit()
    
    # ========== ЗАДАЧИ ==========
    
    def add_task(self, title, category, energy_level, duration=30):
        """Добавление задачи-шаблона"""
        self.cursor.execute('''
            INSERT INTO tasks (title, category, energy_level, estimated_duration, created_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, category, energy_level, duration, datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_tasks(self):
        """Все задачи-шаблоны"""
        self.cursor.execute("SELECT * FROM tasks ORDER BY energy_level DESC")
        result = self.cursor.fetchall()
        # Преобразуем sqlite3.Row в словарь для удобства
        return [dict(row) for row in result]
    
    def delete_task(self, task_id):
        """Удаление задачи"""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
    
    # ========== РАСПИСАНИЕ ==========
    
    def add_to_schedule(self, task_id, task_title, category, energy_level, 
                        target_date, start_time, end_time, duration):
        """Добавление задачи в расписание"""
        self.cursor.execute('''
            INSERT INTO schedule (task_id, task_title, category, energy_level, 
                                 date, start_time, end_time, duration, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, task_title, category, energy_level, target_date, 
              start_time, end_time, duration, 0))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_schedule_for_date(self, target_date):
        """Получение расписания на конкретную дату"""
        self.cursor.execute('''
            SELECT * FROM schedule 
            WHERE date = ? 
            ORDER BY start_time
        ''', (target_date,))
        return self.cursor.fetchall()
    
    def get_schedule_for_range(self, start_date, end_date):
        """Получение расписания за период"""
        self.cursor.execute('''
            SELECT * FROM schedule 
            WHERE date BETWEEN ? AND ?
            ORDER BY date, start_time
        ''', (start_date, end_date))
        return self.cursor.fetchall()
    
    def complete_schedule_item(self, item_id, mood_before=None):
        """Отметить задачу выполненной"""
        if mood_before:
            self.cursor.execute('''
                UPDATE schedule 
                SET is_completed = 1, mood_before = ?
                WHERE id = ?
            ''', (mood_before, item_id))
        else:
            self.cursor.execute('''
                UPDATE schedule 
                SET is_completed = 1
                WHERE id = ?
            ''', (item_id,))
        self.conn.commit()
    
    def delete_schedule_item(self, item_id):
        """Удалить задачу из расписания"""
        self.cursor.execute("DELETE FROM schedule WHERE id = ?", (item_id,))
        self.conn.commit()
    
    def get_completion_stats(self, start_date, end_date):
        """Статистика выполнения задач за период"""
        self.cursor.execute('''
            SELECT date, 
                   COUNT(*) as total,
                   SUM(is_completed) as completed
            FROM schedule 
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        ''', (start_date, end_date))
        return self.cursor.fetchall()
    
    
    def get_tasks_by_category_and_date(self, target_date, category=None):
        """Получение задач на дату по категориям"""
        if category:
            self.cursor.execute('''
                SELECT * FROM schedule 
                WHERE date = ? AND category = ?
                ORDER BY start_time
            ''', (target_date, category))
        else:
            self.cursor.execute('''
                SELECT * FROM schedule 
                WHERE date = ?
                ORDER BY start_time
            ''', (target_date,))
        result = self.cursor.fetchall()
        return [dict(row) for row in result]

    def get_free_time_slots(self, target_date, day_start=8, day_end=22):
        """Получение свободных временных промежутков"""
        tasks = self.get_tasks_by_category_and_date(target_date)
        
        # Создаём список занятых интервалов
        busy_slots = []
        for task in tasks:
            busy_slots.append({
                'start': task['start_time'],
                'end': task['end_time']
            })
        
        # Сортируем по времени начала
        busy_slots.sort(key=lambda x: x['start'])
        
        # Находим свободные промежутки
        free_slots = []
        current_time = f"{day_start:02d}:00"
        
        for slot in busy_slots:
            if current_time < slot['start']:
                free_slots.append({
                    'start': current_time,
                    'end': slot['start']
                })
            current_time = slot['end'] if slot['end'] > current_time else current_time
        
        # Добавляем остаток дня
        end_time = f"{day_end:02d}:00"
        if current_time < end_time:
            free_slots.append({
                'start': current_time,
                'end': end_time
            })
        
        return free_slots
    
    # ========== ЕЖЕДНЕВНЫЕ ЦЕЛИ ==========
    
    def add_daily_goal(self, target_date, goal_text, priority=1):
        """Добавить ежедневную цель"""
        self.cursor.execute('''
            INSERT INTO daily_goals (date, goal_text, priority, is_completed)
            VALUES (?, ?, ?, 0)
        ''', (target_date, goal_text, priority))
        self.conn.commit()
    
    def get_daily_goals(self, target_date):
        """Получить цели на день"""
        self.cursor.execute('''
            SELECT * FROM daily_goals 
            WHERE date = ? 
            ORDER BY priority DESC, id
        ''', (target_date,))
        return self.cursor.fetchall()
    
    def complete_daily_goal(self, goal_id):
        """Отметить цель выполненной"""
        self.cursor.execute('''
            UPDATE daily_goals SET is_completed = 1 WHERE id = ?
        ''', (goal_id,))
        self.conn.commit()
    
    # ========== ПРИВЫЧКИ ==========
    
    def add_habit(self, name, category, frequency, target_count=1):
        """Добавить привычку"""
        self.cursor.execute('''
            INSERT INTO habits (name, category, frequency, target_count, current_streak, created_date)
            VALUES (?, ?, ?, ?, 0, ?)
        ''', (name, category, frequency, target_count, datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_habits(self):
        """Все привычки"""
        self.cursor.execute("SELECT * FROM habits")
        return self.cursor.fetchall()
    
    def complete_habit(self, habit_id, target_date):
        """Отметить выполнение привычки"""
        # Проверяем, не отмечена ли уже
        self.cursor.execute('''
            SELECT * FROM habit_completion 
            WHERE habit_id = ? AND date = ?
        ''', (habit_id, target_date))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.cursor.execute('''
                INSERT INTO habit_completion (habit_id, date, completed)
                VALUES (?, ?, 1)
            ''', (habit_id, target_date))
            
            # Обновляем серию
            self.cursor.execute('''
                UPDATE habits 
                SET current_streak = current_streak + 1 
                WHERE id = ?
            ''', (habit_id,))
            self.conn.commit()
            return True
        return False
    
    def get_habit_streak(self, habit_id):
        """Получить текущую серию привычки"""
        self.cursor.execute('SELECT current_streak FROM habits WHERE id = ?', (habit_id,))
        result = self.cursor.fetchone()
        return result['current_streak'] if result else 0
    
    # ========== ЗАКРЫТИЕ ==========
    
    def close(self):
        self.conn.close()