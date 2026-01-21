import os
from moviepy import VideoFileClip, vfx
from core.base_bot import BaseBot
from core.dispatcher import Dispatcher

class EditorBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("EditorBot")
        self.dispatcher = dispatcher
        self.output_dir = "/home/usic/.gemini/antigravity/scratch/autobot/data/processed_videos"
        os.makedirs(self.output_dir, exist_ok=True)

    def process_video(self, input_path: str, segment_duration: int = 120):
        """
        Нарезает видео на сегменты, меняет формат на 9:16 и применяет эффекты.
        """
        self.logger.info(f"Начало обработки видео: {input_path}")
        
        try:
            clip = VideoFileClip(input_path)
            duration = clip.duration
            filename_base = os.path.basename(input_path).split('.')[0]
            
            # 1. Приведение к формату 9:16
            # Если видео горизонтальное, обрезаем края
            target_ratio = 9/16
            w, h = clip.size
            current_ratio = w/h
            
            if current_ratio > target_ratio:
                # Видео слишком широкое (горизонтальное) - обрезаем по бокам
                new_w = h * target_ratio
                clip = clip.cropped(x_center=w/2, width=new_w)
            elif current_ratio < target_ratio:
                # Видео слишком узкое - обрезаем сверху/снизу (редко)
                new_h = w / target_ratio
                clip = clip.cropped(y_center=h/2, height=new_h)
            
            # Масштабируем до стандартного вертикального размера (опционально, например 1080x1920)
            clip = clip.resized(height=1920) if clip.h < 1920 else clip
            
            # 2. Нарезка на сегменты
            segments = []
            for start_t in range(0, int(duration), segment_duration):
                end_t = min(start_t + segment_duration, duration)
                if end_t - start_t < 10: # Пропускаем слишком короткие хвосты
                    continue
                    
                output_filename = f"{filename_base}_part_{start_t}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Вырезаем кусок
                subclip = clip.subclipped(start_t, end_t)
                
                # 3. Эффекты для уникализации
                # Слегка увеличиваем (зум 5%) и добавляем микро-ускорение (1.01)
                subclip = subclip.resized(1.05)
                subclip = subclip.with_effects([vfx.MultiplySpeed(1.01)])
                
                self.logger.info(f"Сохранение сегмента: {output_filename}")
                subclip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)
                segments.append(output_path)
                
            clip.close()
            return segments
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке: {e}")
            return []

    def run(self):
        """Бот проверяет очередь на наличие задач для монтажа."""
        task = self.dispatcher.get_next_task("video_editing")
        if task:
            input_file = task["data"].get("file_path")
            if input_file and os.path.exists(input_file):
                self.dispatcher.update_task_status(task["id"], "processing")
                result_files = self.process_video(input_file)
                
                if result_files:
                    self.dispatcher.update_task_status(task["id"], "completed", {"processed_files": result_files})
                    # Передаем следующему боту (описание/загрузка)
                    for file in result_files:
                        self.dispatcher.add_task("script_captioning", {"file_path": file})
                else:
                    self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для монтажа.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = EditorBot(disp)
    bot.run()
