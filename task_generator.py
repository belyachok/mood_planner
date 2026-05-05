"""
Модуль генерации задач на день с учётом:
- уже имеющихся задач
- привычек пользователя
- процентного соотношения (работа, отдых, спорт, саморазвитие)
- распределения на 12 часов (с 8:00 до 20:00)
"""

import random
from datetime import datetime, timedelta


class TaskGenerator:
    """Генератор задач на день"""
    
      
    RANDOM_TASKS = {
        "Работа": [
            "Сделать отчёт", "Ответить на письма", "Провести встречу", 
            "Написать план", "Разобрать задачи", "Созвониться с клиентом",
            "Подготовить презентацию", "Проверить документы", "Сделать анализ"
        ],
        "Отдых": [
            "Посмотреть фильм", "Почитать книгу", "Погулять в парке", 
            "Послушать музыку", "Позвонить другу", "Сходить в кафе",
            "Полежать на диване", "Посмотреть сериал", "Поваляться в кровати"
        ],
        "Спорт": [
            "Сделать зарядку", "Пробежка", "Сходить в зал", 
            "Покататься на велосипеде", "Сделать растяжку", "Плавание",
            "Йога", "Отжимания", "Приседания"
        ],
        "Саморазвитие": [
            "Прочитать главу книги", "Посмотреть вебинар", "Выучить 10 новых слов",
            "Пройти онлайн-курс", "Написать пост", "Послушать подкаст",
            "Решить задачу", "Изучить новую тему", "Сделать конспект"
        ]
    }


    def __init__(self, db):
        self.db = db
        
        # Процентное соотношение типов задач (по времени, а не по количеству)
        self.task_ratio = {
            "Работа": 50,      # 40% времени на работуа
            "Отдых": 20,       # 25% на отдых
            "Спорт": 15,       # 15% на спорт
            "Саморазвитие": 15 # 20% на саморазвитие
        }
        
        # Минимальная и максимальная длительность задач (в минутах)
        self.task_duration = {
            "Работа": (60, 180),      # 1-3 часа
            "Отдых": (15, 60),        # 15-60 минут
            "Спорт": (30, 90),        # 30-90 минут
            "Саморазвитие": (30, 120) # 30-120 минут
        }
    
    def get_user_habits(self, user_preferences=None):
        """
        Получение привычек пользователя для персонализации
        Возвращает словарь с весами предпочтений
        """
        # В будущем можно загружать из БД
        # Пока используем настройки по умолчанию
        habits = self.db.get_all_habits() if hasattr(self.db, 'get_all_habits') else []
        
        # Анализируем привычки пользователя
        preference_weights = {
            "Работа": 1.0,
            "Отдых": 1.0,
            "Спорт": 1.0,
            "Саморазвитие": 1.0
        }
        
        for habit in habits:
            category = habit.get('category', '')
            streak = habit.get('current_streak', 0)
            # Чем длиннее серия, тем важнее привычка
            if category in preference_weights:
                preference_weights[category] += streak * 0.1
        
        return preference_weights
    
    def get_existing_tasks_by_date(self, target_date):
        """Получение уже запланированных задач на дату"""
        schedule = self.db.get_schedule_for_date(target_date)
        return [dict(item) for item in schedule] if schedule else []
    
    def get_occupied_time_slots(self, tasks):
        """Получение занятых временных промежутков"""
        occupied = []
        for task in tasks:
            occupied.append({
                'start': task['start_time'],
                'end': task['end_time'],
                'duration': (int(task['end_time'][:2])*60 + int(task['end_time'][3:])) - 
                           (int(task['start_time'][:2])*60 + int(task['start_time'][3:])),
                'category': task.get('category', 'Другое')
            })
        return sorted(occupied, key=lambda x: x['start'])
    
    def get_free_slots(self, occupied_slots, day_start=9, day_end=21):
        """Получение свободных временных промежутков"""
        if not occupied_slots:
            return [{'start': f"{day_start:02d}:00", 'end': f"{day_end:02d}:00", 'duration': (day_end - day_start) * 60}]
        
        free_slots = []
        current_time = day_start * 60
        
        for slot in occupied_slots:
            slot_start = int(slot['start'][:2]) * 60 + int(slot['start'][3:])
            slot_end = int(slot['end'][:2]) * 60 + int(slot['end'][3:])
            
            if current_time < slot_start:
                free_slots.append({
                    'start': f"{current_time//60:02d}:{current_time%60:02d}",
                    'end': f"{slot_start//60:02d}:{slot_start%60:02d}",
                    'duration': slot_start - current_time
                })
            current_time = max(current_time, slot_end)
        
        day_end_minutes = day_end * 60
        if current_time < day_end_minutes:
            free_slots.append({
                'start': f"{current_time//60:02d}:{current_time%60:02d}",
                'end': f"{day_end:02d}:00",
                'duration': day_end_minutes - current_time
            })
        
        return free_slots
    
    def calculate_required_time_by_category(self, total_free_minutes, preference_weights):
        """Расчёт необходимого времени для каждой категории"""
        required = {}
        total_free_minutes = int(total_free_minutes)  # ← преобразуем в int
        
        for category, percent in self.task_ratio.items():
            base_time = total_free_minutes * percent / 100
            weight = preference_weights.get(category, 1.0)
            adjusted_time = base_time * weight
            min_dur, max_dur = self.task_duration[category]
            adjusted_time = max(min_dur, min(adjusted_time, max_dur * 2))
            required[category] = int(adjusted_time)  # ← преобразуем в int
        
        total_required = sum(required.values())
        if total_required > total_free_minutes:
            ratio = total_free_minutes / total_required
            for category in required:
                required[category] = int(required[category] * ratio)
        
        return required
    
    def generate_tasks_for_category(self, category, required_minutes, free_slots, existing_categories):
        """
        Генерация задач для конкретной категории на свободных слотах
        """
        generated_tasks = []
        remaining = int(required_minutes)  
        min_dur, max_dur = self.task_duration[category]
        
        # Получаем шаблоны задач из БД для этой категории
        template_tasks = self.db.get_all_tasks()
        category_tasks = [t for t in template_tasks if t.get('category') == category]
        
        for slot in free_slots:
            if remaining <= 0:
                break
            
            slot_duration = int(slot['duration'])  # ← преобразуем в int
            if slot_duration < min_dur:
                continue
            
            # Длительность задачи
            task_duration = min(slot_duration, remaining, max_dur)
            if task_duration < min_dur:
                task_duration = min(slot_duration, remaining)
            
            # Выбираем задачу из шаблона или создаём стандартную
            task_title = random.choice(self.RANDOM_TASKS.get(category, [self._get_default_task_title(category)]))
            task_energy = 5

            
            generated_tasks.append({
                'start': slot['start'],
                'end': self._add_minutes(slot['start'], task_duration),
                'title': task_title,
                'category': category,
                'energy_level': task_energy,
                'duration': task_duration
            })
            
            remaining -= task_duration
            # Обновляем слот
            slot['start'] = self._add_minutes(slot['start'], task_duration)
            slot['duration'] -= task_duration
        
        return generated_tasks
    
    def _get_default_task_title(self, category):
        """Стандартные названия задач для категорий"""
        defaults = {
            "Работа": "Рабочая задача",
            "Отдых": "Перерыв",
            "Спорт": "Физическая активность",
            "Саморазвитие": "Самообразование"
        }
        return defaults.get(category, "Задача")
    
    def _add_minutes(self, time_str, minutes):
        """Прибавить минуты к времени"""
        hour = int(time_str[:2])
        minute = int(time_str[3:])
        total = hour * 60 + minute + int(minutes)  # ← int(minutes)
        new_hour = total // 60
        new_minute = total % 60
        return f"{new_hour:02d}:{new_minute:02d}"
    
    def generate_daily_schedule(self, target_date, user_preferences=None):
        """
        Генерация полного расписания на день
        """
        # Получаем существующие задачи
        existing_tasks = self.get_existing_tasks_by_date(target_date)
        
        # Получаем занятые слоты
        occupied_slots = self.get_occupied_time_slots(existing_tasks)
        
        # Получаем свободные слоты
        free_slots = self.get_free_slots(occupied_slots)
        total_free_minutes = sum(slot['duration'] for slot in free_slots)
        
        if total_free_minutes < 30:
            return {'generated_tasks': [], 'message': 'Недостаточно свободного времени'}
        
        # Получаем предпочтения пользователя на основе привычек
        preference_weights = self.get_user_habits(user_preferences)
        
        # Анализируем уже запланированные категории
        existing_categories = {}
        for task in existing_tasks:
            cat = task.get('category', 'Другое')
            existing_categories[cat] = existing_categories.get(cat, 0) + 1
        
        # Рассчитываем необходимое время по категориям
        required_time = self.calculate_required_time_by_category(total_free_minutes, preference_weights)
        
        # Генерируем задачи для каждой категории
        all_generated = []
        free_slots_copy = free_slots.copy()
        
        for category in ["Работа", "Спорт", "Саморазвитие", "Отдых"]:
            if category in required_time and required_time[category] > 0:
                tasks = self.generate_tasks_for_category(
                    category, 
                    required_time[category], 
                    free_slots_copy,
                    existing_categories
                )
                all_generated.extend(tasks)
        
        return {
            'generated_tasks': all_generated,
            'existing_tasks': existing_tasks,
            'total_free_minutes': total_free_minutes,
            'required_time': required_time,
            'free_slots': free_slots
        }
    
    def apply_generated_schedule(self, target_date, generated_tasks):
        """Добавить сгенерированные задачи в расписание"""
        added_count = 0
        for task in generated_tasks:
            self.db.add_to_schedule(
                task_id=None,
                task_title=task['title'],
                category=task['category'],
                energy_level=task['energy_level'],
                target_date=target_date,
                start_time=task['start'],
                end_time=task['end'],
                duration=task['duration']
            )
            added_count += 1
        return added_count