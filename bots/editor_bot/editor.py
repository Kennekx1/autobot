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

    def process_video_task(self, input_path: str, mode: str = "clean_cut", music_path: str = None):
        """
        Основной метод обработки в зависимости от режима.
        mode: 'clean_cut' (простая нарезка) или 'epic_edit' (под музыку)
        """
        self.logger.info(f"Запуск монтажа в режиме: {mode}")
        
        # 1. Сначала нарезаем видео на сегменты
        segments = self.slice_video(input_path)
        processed_segments = []

        for segment in segments:
            if mode == "epic_edit" and music_path:
                # Если режим эдита, накладываем музыку на каждый сегмент
                final_path = self.overlay_music(segment, music_path)
                processed_segments.append(final_path)
            else:
                processed_segments.append(segment)
                
        return processed_segments

    def slice_video(self, input_path: str, segment_duration: int = 120):
        """Метод только для нарезки и изменения формата."""
        try:
            clip = VideoFileClip(input_path)
            duration = clip.duration
            filename_base = os.path.basename(input_path).split('.')[0]
            
            # Приведение к 9:16
            w, h = clip.size
            target_ratio = 9/16
            if w/h > target_ratio:
                new_w = h * target_ratio
                clip = clip.cropped(x_center=w/2, width=new_w)
            
            clip = clip.resized(height=1920) if clip.h < 1920 else clip
            
            segments = []
            for start_t in range(0, int(duration), segment_duration):
                end_t = min(start_t + segment_duration, duration)
                if end_t - start_t < 10: continue
                    
                output_path = os.path.join(self.output_dir, f"{filename_base}_part_{start_t}.mp4")
                subclip = clip.subclipped(start_t, end_t).resized(1.05)
                subclip = subclip.with_effects([vfx.MultiplySpeed(1.01)])
                
                subclip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)
                segments.append(output_path)
                
            clip.close()
            return segments
        except Exception as e:
            self.logger.error(f"Ошибка при нарезке: {e}")
            return []

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
        task = self.dispatcher.get_next_task("video_editing")
        if task:
            data = task["data"]
            input_file = data.get("file_path")
            mode = data.get("mode", "clean_cut") # По умолчанию просто нарезка
            music_file = data.get("music_path")

            if input_file and os.path.exists(input_file):
                self.dispatcher.update_task_status(task["id"], "processing")
                result_files = self.process_video_task(input_file, mode, music_file)
                
                if result_files:
                    self.dispatcher.update_task_status(task["id"], "completed", {"processed_files": result_files})
                    niche = data.get("niche", "movie_cuts")
                    for file in result_files:
                        self.dispatcher.add_task("script_captioning", {
                            "file_path": file,
                            "niche": niche
                        })
                else:
                    self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для монтажа.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = EditorBot(disp)
    bot.run()
