import os
from openai import OpenAI
from core.base_bot import BaseBot
from core.dispatcher import Dispatcher
from dotenv import load_dotenv

load_dotenv()

class ScriptBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("ScriptBot")
        self.dispatcher = dispatcher
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate_caption(self, video_context: str):
        """
        Генерирует виральное описание и хештеги на основе контекста видео.
        """
        self.logger.info(f"Генерация описания для: {video_context}")
        
        prompt = f"""
        Ты эксперт по продвижению в TikTok, Instagram Reels и YouTube Shorts.
        Твоя задача — написать максимально виральное описание к ролику.
        Контекст видео: {video_context}
        
        Требования:
        1. Описание должно интриговать, чтобы досмотрели до конца.
        2. Добавь 5-7 релевантных и трендовых хештегов.
        3. Используй эмодзи.
        4. Ответ дай на русском языке.
        
        Формат ответа:
        Текст поста...
        
        #хештег1 #хештег2 ...
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ты профессиональный SMM-менеджер."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            result = response.choices[0].message.content
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при вызове OpenAI: {e}")
            return None

    def run(self):
        """Бот проверяет очередь на наличие задач для написания описаний."""
        task = self.dispatcher.get_next_task("script_captioning")
        if task:
            file_path = task["data"].get("file_path")
            niche = task["data"].get("niche", "movie_cuts")
            # Нам нужно понять, о чем видео. Пока возьмем имя файла как контекст.
            context = os.path.basename(file_path)
            
            self.dispatcher.update_task_status(task["id"], "processing")
            caption = self.generate_caption(context)
            
            if caption:
                self.dispatcher.update_task_status(task["id"], "completed", {"caption": caption})
                # Передаем всем аккаунтам в этой нише (TikTok, YT, IG)
                self.dispatcher.add_niche_tasks("upload_video", {
                    "file_path": file_path,
                    "caption": caption
                }, niche=niche)
                self.logger.info(f"Задачи на загрузку созданы для всей ниши: {niche}")
            else:
                self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для генерации описаний.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = ScriptBot(disp)
    bot.run()
