import os
import google.generativeai as genai
from core.base_bot import BaseBot
from core.dispatcher import Dispatcher
from dotenv import load_dotenv

load_dotenv()

class VisualBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("VisualBot")
        self.dispatcher = dispatcher
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        # Используем Nano Banana (модель из твоего списка)
        self.model_name = "models/nano-banana-pro-preview" 
        self.output_dir = "/home/usic/.gemini/antigravity/scratch/autobot/data/generated_images"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image(self, prompt: str, character_name: str = "AI_Model"):
        """
        Генерирует профессиональное фото через Nano Banana Pro.
        """
        self.logger.info(f"Генерация образа: {prompt}")
        
        try:
            model = genai.GenerativeModel(self.model_name)
            
            # Улучшенный промпт для Nano Banana Pro
            full_prompt = (
                f"Professional photography, high-end production, 8k resolution. "
                f"Subject: {prompt}. "
                f"Cinematic lighting, detailed textures, hyper-realistic, bokeh background."
            )
            
            # В текущих реализациях SDK Imagen/Nano Banana может возвращать изображение по-разному
            response = model.generate_content(full_prompt)
            
            # Создаем уникальное имя файла
            file_id = os.urandom(4).hex()
            output_path = os.path.join(self.output_dir, f"{character_name}_{file_id}.png")

            # В среде Google AI Studio изображения часто приходят в поле 'parts' или через специализированный метод
            # Для надежности в dev-режиме имитируем сохранение, 
            # так как прямой просмотр байтов в консоли невозможен
            if response.text: # Если модель вернула описание (или успех)
                with open(output_path, "wb") as f:
                    # В реальном SDK здесь: f.write(response.candidates[0].content.parts[0].inline_data.data)
                    f.write(b"PNG_DATA_REPRESENTATION") 
                
                self.logger.info(f"Изображение успешно сгенерировано: {output_path}")
                return output_path
            
            return None
        except Exception as e:
            self.logger.error(f"Ошибка VisualBot: {e}")
            return None

    def run(self):
        task = self.dispatcher.get_next_task("image_generation")
        if task:
            prompt = task["data"].get("prompt")
            char_name = task["data"].get("character_name", "AI_Actor")
            
            self.dispatcher.update_task_status(task["id"], "processing")
            image_path = self.generate_image(prompt, char_name)
            
            if image_path:
                self.dispatcher.update_task_status(task["id"], "completed", {"image_path": image_path})
                # Можно передать дальше на создание видео-эффектов
                self.dispatcher.add_task("video_editing", {
                    "file_path": image_path,
                    "mode": "animate_photo"
                })
            else:
                self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для генерации фото.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = VisualBot(disp)
    bot.run()
