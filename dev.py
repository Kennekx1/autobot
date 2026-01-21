import sys
import os

# Добавляем путь к проекту в sys.path
project_root = "/home/usic/.gemini/antigravity/scratch/autobot"
sys.path.append(project_root)

from core.media_utils import MediaUtils
from core.dispatcher import Dispatcher

def test_download():
    print("--- Тест скачивания видео ---")
    url = input("Введите ссылку на видео (TikTok/YouTube): ")
    output_dir = os.path.join(project_root, "data/temp_downloads")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = MediaUtils.download_video(url, output_dir)
    if filename:
        print(f"Видео успешно скачано: {filename}")
    else:
        print("Не удалось скачать видео.")

def show_queue():
    print("--- Текущая очередь задач ---")
    disp = Dispatcher(project_root)
    queue_file = os.path.join(project_root, "data/pipeline_queue.json")
    if os.path.exists(queue_file):
        with open(queue_file, 'r') as f:
            import json
            queue = json.load(f)
            for task in queue:
                print(f"[{task['id']}] Type: {task['type']} | Status: {task['status']}")
    else:
        print("Очередь пуста.")

if __name__ == "__main__":
    while True:
        print("\n--- DEV MENU ---")
        print("1. Тест скачивания видео")
        print("2. Показать очередь задач")
        print("3. Выход")
        choice = input("Выберите действие: ")
        
        if choice == "1":
            test_download()
        elif choice == "2":
            show_queue()
        elif choice == "3":
            break
        else:
            print("Неверный выбор.")
