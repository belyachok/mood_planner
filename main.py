"""
Точка входа в приложение Mood Planner
"""

from config import DB_NAME
from database import Database
from recommendations import RecommendationEngine
from gui import MoodPlannerApp


def main():
    """Запуск приложения"""
    db = Database(DB_NAME)
    app = MoodPlannerApp(db)


if __name__ == "__main__":
    main()