import yt_dlp
import os

class MediaUtils:
    @staticmethod
    def download_video(url: str, output_path: str):
        """Скачивает видео по ссылке в указанную директорию."""
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return filename
        except Exception as e:
            print(f"Ошибка при скачивании: {e}")
            return None

    @staticmethod
    def get_video_info(url: str):
        """Получает информацию о видео без скачивания."""
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
