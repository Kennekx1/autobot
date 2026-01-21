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

def test_editor():
    print("--- Тест монтажа видео ---")
    file_path = input("Введите полный путь к видео файлу: ")
    if not os.path.exists(file_path):
        print("Файл не найден!")
        return
        
    disp = Dispatcher(project_root)
    bot = EditorBot(disp)
    results = bot.process_video(file_path)
    if results:
        print(f"Готово! Обработано файлов: {len(results)}")
        for r in results:
            print(f" - {r}")
    else:
        print("Ошибка при монтаже.")

if __name__ == "__main__":
    from bots.editor_bot.editor import EditorBot
    while True:
        print("\n--- DEV MENU ---")
        print("1. Тест скачивания видео")
        print("2. Тест монтажа видео (EditorBot)")
        print("3. Показать очередь задач")
        print("4. Выход")
        choice = input("Выберите действие: ")
        
        if choice == "1":
            test_download()
        elif choice == "2":
            test_editor()
        elif choice == "3":
            show_queue()
        elif choice == "4":
            break
        else:
            print("Неверный выбор.")
