from core.base_bot import BaseBot
from core.dispatcher import Dispatcher
import time

class TrendBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("TrendBot")
        self.dispatcher = dispatcher

    def run(self, niche: str = "movie_cuts"):
        self.logger.info(f"Поиск актуальных трендов для ниши: {niche}...")
        # Имитация поиска тренда
        time.sleep(2)
        trend_data = {
            "topic": f"Best of {niche} 2026",
            "hashtags": ["#ai", "#trending", f"#{niche}"],
            "style": "cinematic",
            "niche": niche
        }
        self.logger.info(f"Найден тренд: {trend_data['topic']}")
        
        # Передаем задачу на согласование пользователю
        self.dispatcher.add_task("script_generation", trend_data, status="awaiting_approval")
        self.logger.info(f"Тренд для ниши {niche} отправлен на согласование.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    import os
    
    # Путь к корню проекта
    project_root = "/home/usic/.gemini/antigravity/scratch/autobot"
    disp = Dispatcher(project_root)
    bot = TrendBot(disp)
    bot.run()
