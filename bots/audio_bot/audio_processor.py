import os
import math
from pydub import AudioSegment
from core.base_bot import BaseBot
from core.dispatcher import Dispatcher

class AudioBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("AudioBot")
        self.dispatcher = dispatcher
        self.output_dir = "/home/usic/.gemini/antigravity/scratch/autobot/data/processed_audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_tts(self, text: str, voice: str = "alloy"):
        """
        Озвучивает текст через OpenAI TTS.
        """
        self.logger.info(f"Озвучка текста: {text[:50]}...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            output_path = os.path.join(self.output_dir, f"tts_{os.urandom(4).hex()}.mp3")
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            response.stream_to_file(output_path)
            self.logger.info(f"Голос сохранен: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Ошибка TTS: {e}")
            return None

    def create_8d_effect(self, input_path: str, speed: float = 0.5):
        """
        Создает эффект 8D звука (вращение вокруг головы).
        speed: скорость вращения (чем выше, тем быстрее звук 'бегает')
        """
        self.logger.info(f"Начало обработки аудио: {input_path}")
        
        try:
            audio = AudioSegment.from_file(input_path)
            duration_ms = len(audio)
            
            # Разделяем на маленькие кусочки для плавного панорамирования
            chunk_size = 50  # 50 мс
            processed_audio = AudioSegment.empty()
            
            for i in range(0, duration_ms, chunk_size):
                chunk = audio[i:i+chunk_size]
                
                # Вычисляем уровень панорамы (от -1.0 до 1.0)
                # Используем синус для плавности: sin(время * скорость)
                # speed здесь влияет на частоту колебаний
                pan = math.sin(i / 1000 * speed * math.pi)
                
                # Применяем панораму
                chunk_panned = chunk.pan(pan)
                processed_audio += chunk_panned
            
            filename = os.path.basename(input_path).split('.')[0] + "_8d.mp3"
            output_path = os.path.join(self.output_dir, filename)
            
            # Сохраняем результат
            processed_audio.export(output_path, format="mp3")
            self.logger.info(f"8D аудио сохранено: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании 8D эффекта: {e}")
            return None

    def run(self):
        """Проверяет очередь на наличие задач для звука."""
        task = self.dispatcher.get_next_task("audio_processing")
        if task:
            input_file = task["data"].get("file_path")
            if input_file and os.path.exists(input_file):
                self.dispatcher.update_task_status(task["id"], "processing")
                result_file = self.create_8d_effect(input_file)
                
                if result_file:
                    self.dispatcher.update_task_status(task["id"], "completed", {"processed_audio": result_file})
                else:
                    self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для аудио.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = AudioBot(disp)
    bot.run()
