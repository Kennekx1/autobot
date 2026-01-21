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

    def overlay_music(self, video_path: str, music_path: str, video_volume: float = 0.3, music_volume: float = 1.0):
        """
        Накладывает фоновую музыку на видео.
        video_volume: громкость оригинального звука (0.3 = 30%)
        music_volume: громкость накладываемой музыки
        """
        self.logger.info(f"Наложение музыки {music_path} на {video_path}")
        try:
            from moviepy import AudioFileClip
            video_clip = VideoFileClip(video_path)
            music_clip = AudioFileClip(music_path)
            
            # Зацикливаем музыку или обрезаем под длину видео
            if music_clip.duration < video_clip.duration:
                # Если музыка короче видео, зацикливаем (через повторение сегмента)
                repeats = int(video_clip.duration / music_clip.duration) + 1
                from moviepy import concatenate_audioclips
                music_clip = concatenate_audioclips([music_clip] * repeats)
            
            music_clip = music_clip.subclipped(0, video_clip.duration)
            
            # Регулируем громкость
            new_video_audio = video_clip.audio.with_volume_scaled(video_volume)
            new_music_audio = music_clip.with_volume_scaled(music_volume)
            
            # Смешиваем аудио
            from moviepy import CompositeAudioClip
            final_audio = CompositeAudioClip([new_video_audio, new_music_audio])
            
            final_clip = video_clip.with_audio(final_audio)
            
            output_path = video_path.replace(".mp4", "_epic.mp4")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)
            
            video_clip.close()
            music_clip.close()
            return output_path
        except Exception as e:
            self.logger.error(f"Ошибка при смешивании музыки: {e}")
            return video_path
            
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
