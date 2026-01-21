from core.base_bot import BaseBot
from core.dispatcher import Dispatcher
import time

class TrendBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("TrendBot")
        self.dispatcher = dispatcher

    def run(self):
        self.logger.info("Поиск актуальных трендов...")
        # Имитация поиска тренда
        time.sleep(2)
        trend_data = {
            "topic": "AI Influencers in 2026",
            "hashtags": ["#ai", "#future", "#contentfactory"],
            "style": "cinematic"
        }
        self.logger.info(f"Найден тренд: {trend_data['topic']}")
        
        # Передаем задачу на согласование пользователю
        self.dispatcher.add_task("script_generation", trend_data, status="awaiting_approval")
        self.logger.info("Тренд отправлен на согласование пользователю.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    import os
    
    # Путь к корню проекта
    project_root = "/home/usic/.gemini/antigravity/scratch/autobot"
    disp = Dispatcher(project_root)
    bot = TrendBot(disp)
    bot.run()
