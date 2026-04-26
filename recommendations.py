"""
Расширенный модуль рекомендаций
"""

from datetime import datetime
from config import DEFAULT_RECOMMENDATIONS


class RecommendationEngine:
    """Класс для формирования рекомендаций"""
    
    def __init__(self, db):
        self.db = db
    
    def get_season_and_weather(self):
        """Определение времени года и рекомендаций на его основе"""
        import datetime
        month = datetime.datetime.now().month
        
        if month in [12, 1, 2]:
            season = "зима"
            weather_tips = {
                "активный": ["Каток", "Лыжи", "Сноуборд", "Прогулка по заснеженному парку"],
                "спокойный": ["Кино", "Музей", "Театр", "Торговый центр", "Кафе"],
                "домашний": ["Чтение книги", "Просмотр фильма", "Готовка", "Рукоделие"]
            }
        elif month in [3, 4, 5]:
            season = "весна"
            weather_tips = {
                "активный": ["Прогулка в парке", "Велопрогулка", "Фотоохота"],
                "спокойный": ["Выставка", "Кафе с видом на улицу", "Прогулка"],
                "домашний": ["Уборка", "Планирование лета", "Садоводство"]
            }
        elif month in [6, 7, 8]:
            season = "лето"
            weather_tips = {
                "активный": ["Пляж", "Поход", "Велопрогулка", "Пикник"],
                "спокойный": ["Летнее кафе", "Книга в парке", "Наблюдение за закатом"],
                "домашний": ["Кондиционер дома", "Готовка холодных блюд"]
            }
        else:  # 9, 10, 11
            season = "осень"
            weather_tips = {
                "активный": ["Прогулка в парке", "Сбор листьев", "Фотосессия"],
                "спокойный": ["Музей", "Театр", "Кофейня", "Кино"],
                "домашний": ["Уютный вечер дома", "Чтение", "Творчество"]
            }
        
        return season, weather_tips

    def get_recommendations(self, mood_score, target_date=None):
        """Получение полных рекомендаций с учётом загрузки и сезона"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        energy = self.get_energy_level(mood_score)
        mood_desc = self.get_mood_description(mood_score)
        time_rec = self.get_time_of_day_recommendation()
        season_info = self.get_season_and_temperature()
        
        schedule = self.get_user_schedule_for_date(target_date)
        load_analysis = self.analyze_daily_load(schedule)
        free_slots = self.calculate_free_time_slots(schedule)
        free_recommendations = self.recommend_free_time_activities(free_slots, season_info, load_analysis['categories'])
        
        pending_tasks = [t for t in schedule if not t.get('is_completed', False)]
        
        full_text = f"{mood_desc}\n"
        full_text += f"⚡ Уровень энергии: {energy}\n"
        full_text += f"🕐 {time_rec}\n"
        full_text += f"🗓️ Сезон: {season_info['season']} | {season_info['temperature']}°C\n\n"
        full_text += "━" * 40 + "\n\n"
        
        full_text += "📊 ЗАГРУЗКА ДНЯ\n"
        full_text += f"   • Запланировано: {load_analysis['total_tasks']} задач\n"
        full_text += f"   • Занято времени: {load_analysis['total_hours']} ч\n"
        full_text += f"   • Свободно: {load_analysis['free_hours']} ч\n"
        full_text += f"   • Загрузка: {load_analysis['load_percent']}%\n\n"
        
        if pending_tasks:
            full_text += "⏰ НАПОМИНАНИЯ\n"
            for task in pending_tasks[:3]:
                full_text += f"   • {task['task_title']} в {task['start_time']}\n"
            full_text += "\n"
        
        if free_recommendations:
            full_text += "💡 ЧЕМ ЗАНЯТЬСЯ В СВОБОДНОЕ ВРЕМЯ\n"
            for rec in free_recommendations[:4]:
                full_text += f"   • {rec['start']}-{rec['end']}: {rec['activity']}\n"
            full_text += "\n"
        
        full_text += "🌿 СОВЕТЫ\n"
        if season_info['weather_type'] == 'холодно':
            full_text += "   • На улице холодно, одевайся теплее\n"
        elif season_info['weather_type'] == 'тепло':
            full_text += "   • Отличная погода для прогулок!\n"
        
        self.db.save_mood(mood_score, mood_desc, energy, full_text)
        
        return {
            "text": full_text,
            "energy": energy,
            "mood_desc": mood_desc,
            "load_analysis": load_analysis,
            "season": season_info['season'],
            "free_recommendations": free_recommendations
        }
    

    
    def get_time_of_day_recommendation(self):
        """Рекомендации по времени суток"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "🌅 Утро — лучшее время для важных дел"
        elif 12 <= hour < 17:
            return "☀️ День — время для активной работы и встреч"
        elif 17 <= hour < 22:
            return "🌆 Вечер — время для отдыха и подведения итогов"
        else:
            return "🌙 Ночь — пора отдыхать, планируйте завтрашний день"
    
    def _get_duration_minutes(self, start_time, end_time):
        """Вычисление длительности в минутах"""
        start_hour = int(start_time[:2])
        start_min = int(start_time[3:])
        end_hour = int(end_time[:2])
        end_min = int(end_time[3:])
        return (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
    
    def get_season_and_temperature(self, month=None):
        """Определение сезона и средней температуры по месяцу"""
        if month is None:
            month = datetime.now().month
        
        if month in [12, 1, 2]:
            return {'season': 'зима', 'temperature': -10, 'weather_type': 'холодно'}
        elif month in [3, 4, 5]:
            return {'season': 'весна', 'temperature': 5, 'weather_type': 'прохладно'}
        elif month in [6, 7, 8]:
            return {'season': 'лето', 'temperature': 22, 'weather_type': 'тепло'}
        else:
            return {'season': 'осень', 'temperature': 8, 'weather_type': 'прохладно'}
        

    def get_user_schedule_for_date(self, target_date):
        """Получение расписания пользователя на конкретную дату"""
        try:
            schedule = self.db.get_schedule_for_date(target_date)
            return [dict(item) for item in schedule] if schedule else []
        except:
            return []
        
    def calculate_free_time_slots(self, schedule, day_start=8, day_end=22):
        """Расчёт свободных промежутков на основе расписания"""
        if not schedule:
            return [{'start': f"{day_start:02d}:00", 'end': f"{day_end:02d}:00", 'duration_minutes': (day_end - day_start) * 60}]
        
        sorted_tasks = sorted(schedule, key=lambda x: x['start_time'])
        free_slots = []
        current_time = day_start * 60
        
        for task in sorted_tasks:
            task_start = int(task['start_time'][:2]) * 60 + int(task['start_time'][3:])
            task_end = int(task['end_time'][:2]) * 60 + int(task['end_time'][3:])
            
            if current_time < task_start:
                free_slots.append({
                    'start': f"{current_time//60:02d}:{current_time%60:02d}",
                    'end': f"{task_start//60:02d}:{task_start%60:02d}",
                    'duration_minutes': task_start - current_time
                })
            current_time = max(current_time, task_end)
        
        day_end_minutes = day_end * 60
        if current_time < day_end_minutes:
            free_slots.append({
                'start': f"{current_time//60:02d}:{current_time%60:02d}",
                'end': f"{day_end:02d}:00",
                'duration_minutes': day_end_minutes - current_time
            })
        
        return free_slots
    
    def analyze_daily_load(self, schedule):
        """Анализ загрузки человека на день"""
        if not schedule:
            return {
                'total_tasks': 0,
                'total_hours': 0,
                'free_hours': 14,
                'categories': {},
                'load_percent': 0
            }
        
        total_minutes = 0
        categories_count = {}
        
        for task in schedule:
            start = int(task['start_time'][:2]) * 60 + int(task['start_time'][3:])
            end = int(task['end_time'][:2]) * 60 + int(task['end_time'][3:])
            total_minutes += end - start
            
            category = task.get('category', 'Другое')
            categories_count[category] = categories_count.get(category, 0) + 1
        
        free_slots = self.calculate_free_time_slots(schedule)
        free_minutes = sum(slot['duration_minutes'] for slot in free_slots)
        
        return {
            'total_tasks': len(schedule),
            'total_hours': round(total_minutes / 60, 1),
            'free_hours': round(free_minutes / 60, 1),
            'categories': categories_count,
            'load_percent': round((total_minutes / (14 * 60)) * 100, 1)
        }
    
    def recommend_free_time_activities(self, free_slots, season_info, categories):
        """Рекомендации по заполнению свободного времени"""
        if not free_slots:
            return []
        
        season = season_info['season']
        has_work = 'Работа' in categories or 'Учёба' in categories
        
        recommendations = []
        for slot in free_slots:
            duration = slot['duration_minutes']
            slot_hour = int(slot['start'][:2])
            
            if duration < 15:
                activity = "🫖 Микро-перерыв: выпей воды, разомнись"
            elif duration < 30:
                activity = "☕ Короткий перерыв: чай и лёгкая разминка"
            elif duration < 60:
                activity = self._get_season_activity(season, 'спокойный')
            elif duration < 120:
                activity = self._get_season_activity(season, 'активный')
            else:
                activity = self._get_season_activity(season, 'полноценный')
            
            if slot_hour < 12:
                time_note = " (утро)"
            elif slot_hour < 17:
                time_note = " (день)"
            else:
                time_note = " (вечер)"
            
            recommendations.append({
                'start': slot['start'],
                'end': slot['end'],
                'duration': duration,
                'activity': activity + time_note
            })
        
        return recommendations

    def _get_season_activity(self, season, activity_type):
        """Получение активности по сезону и типу"""
        activities = {
            'зима': {'спокойный': 'Сходить в кино/музей', 'активный': 'Покататься на коньках/лыжах', 'полноценный': 'Устроить уютный вечер дома'},
            'весна': {'спокойный': 'Сходить в кафе', 'активный': 'Прогуляться в парке', 'полноценный': 'Устроить пикник'},
            'лето': {'спокойный': 'Почитать книгу в парке', 'активный': 'Сходить на пляж', 'полноценный': 'Отправиться в поход'},
            'осень': {'спокойный': 'Сходить в театр', 'активный': 'Прогуляться по парку', 'полноценный': 'Устроить фотосессию'}
        }
        return activities.get(season, activities['осень']).get(activity_type, 'Отдохнуть')
    
    def get_state_profile(self, energy, calm, motivation):
        """Определение профиля состояния на основе трёх показателей"""
        energy_level = "высокая" if energy >= 7 else "средняя" if energy >= 4 else "низкая"
        calm_level = "высокое" if calm >= 7 else "среднее" if calm >= 4 else "низкое"
        motivation_level = "высокая" if motivation >= 7 else "средняя" if motivation >= 4 else "низкая"
        
        # Определяем рекомендательный профиль
        if energy >= 7 and calm >= 7 and motivation >= 7:
            profile = "идеальное"
            profile_desc = "Вы в отличной форме! 🌟"
        elif energy >= 7 and calm <= 3 and motivation >= 7:
            profile = "тревожное"
            profile_desc = "У вас много энергии, но вы тревожны 😟"
        elif energy <= 3 and calm >= 7 and motivation <= 3:
            profile = "усталое"
            profile_desc = "Вы устали и нуждаетесь в отдыхе 😴"
        elif energy >= 7 and calm >= 7 and motivation <= 3:
            profile = "апатичное"
            profile_desc = "Энергия есть, но не хочется ничего делать 😐"
        elif energy <= 3 and calm <= 3 and motivation <= 3:
            profile = "выгоревшее"
            profile_desc = "Вы на пределе, нужен срочный отдых 🔥"
        else:
            profile = "сбалансированное"
            profile_desc = "Среднее состояние, можно работать 😐"
        
        return {
            'profile': profile,
            'profile_desc': profile_desc,
            'energy_level': energy_level,
            'calm_level': calm_level,
            'motivation_level': motivation_level,
            'energy': energy,
            'calm': calm,
            'motivation': motivation
        }

    def get_recommendations_by_state(self, state_profile, free_slots, load_analysis, season_info):
        """Рекомендации на основе профиля состояния"""
        profile = state_profile['profile']
        energy = state_profile['energy']
        calm = state_profile['calm']
        motivation = state_profile['motivation']
        
        recommendations = []
        
        for slot in free_slots:
            duration = slot['duration_minutes']
            
            if profile == "идеальное":
                if duration >= 60:
                    rec = "🎯 Можешь взяться за самую сложную задачу"
                else:
                    rec = "💪 Сделай короткую, но эффективную задачу"
            
            elif profile == "тревожное":
                if duration >= 30:
                    rec = "🧘 Займись успокаивающей активностью: прогулка, дыхание, лёгкий спорт"
                else:
                    rec = "🌿 Сделай дыхательное упражнение 4-7-8"
            
            elif profile == "усталое":
                if duration >= 60:
                    rec = "😴 Отдохни полноценно: сон, ванна, ничего не делай"
                else:
                    rec = "🛌 Просто посиди в тишине, закрой глаза"
            
            elif profile == "апатичное":
                if duration >= 30:
                    rec = "🎬 Посмотри короткое мотивирующее видео или послушай подкаст"
                else:
                    rec = "🍫 Сделай приятную мелочь для себя (чай/кофе/сладость)"
            
            elif profile == "выгоревшее":
                rec = "⚠️ ТЕБЕ НУЖЕН ОТДЫХ! Отложи всё, восстановление важнее"
            
            else:  # сбалансированное
                if duration >= 60:
                    rec = "📋 Выполни запланированные дела"
                else:
                    rec = "☕ Сделай короткий перерыв"
            
            recommendations.append({
                'start': slot['start'],
                'end': slot['end'],
                'duration': duration,
                'activity': rec,
                'profile': profile
            })
        
        return recommendations