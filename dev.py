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

def test_script_bot():
    print("--- Тест генерации описания (OpenAI) ---")
    context = input("О чем видео? (например: нарезка из фильма Интерстеллар): ")
    
    disp = Dispatcher(project_root)
    bot = ScriptBot(disp)
    caption = bot.generate_caption(context)
    if caption:
        print(f"\nСгенерированный пост:\n{'-'*20}\n{caption}\n{'-'*20}")
    else:
        print("Ошибка при генерации. Проверь API_KEY в .env")

def test_uploader():
    print("--- Тест загрузки видео (UploaderBot) ---")
    file_path = input("Введите путь к видео для загрузки: ")
    caption = input("Введите описание: ")
    account_id = int(input("Введите ID аккаунта из data/accounts.json: "))
    
    disp = Dispatcher(project_root)
    bot = UploaderBot(disp)
    
    # Создаем фиктивную задачу для теста
    disp.add_task("upload_video", {"file_path": file_path, "caption": caption}, account_id=account_id)
    bot.run()

def test_visual_bot():
    print("--- Тест генерации фото (Nano Banana Pro) ---")
    prompt = input("Опишите персонажа или сцену: ")
    char_name = input("Имя персонажа (для файла): ") or "AI_Model"
    
    disp = Dispatcher(project_root)
    bot = VisualBot(disp)
    result = bot.generate_image(prompt, char_name)
    if result:
        print(f"Готово! Изображение здесь: {result}")
    else:
        print("Ошибка генерации. Проверьте GEMINI_API_KEY.")

def test_tts():
    print("--- Тест озвучки текста (TTS) ---")
    text = input("Введите текст для озвучки: ")
    
    disp = Dispatcher(project_root)
    bot = AudioBot(disp)
    result = bot.generate_tts(text)
    if result:
        print(f"Готово! Аудио файл: {result}")
    else:
        print("Ошибка TTS.")

def run_full_pipeline():
    print("--- ЗАПУСК ПОЛНОГО КОНВЕЙЕРА (Тестовый прогон) ---")
    # 1. Аналитик находит тренд
    disp = Dispatcher(project_root)
    tb = TrendBot(disp)
    tb.run()
    
    # 2. Получаем задачу из очереди и одобряем её
    queue_file = os.path.join(project_root, "data/pipeline_queue.json")
    with open(queue_file, 'r') as f:
        import json
        queue = json.load(f)
        last_task = queue[-1]
    
    print(f"Обнаружена задача: {last_task['type']} (ID: {last_task['id']})")
    confirm = input("Одобрить запуск цепочки? (y/n): ")
    if confirm.lower() == 'y':
        disp.approve_task(last_task['id'])
        
        # 3. Запускаем остальных ботов по очереди
        sb = ScriptBot(disp)
        sb.run()
        print("Сценарий готов.")
        
        # Для теста загрузки нужно иметь реальный файл
        # Здесь мы просто показываем, что цепочка работает
        print("Цепочка прошла успешно до этапа загрузки.")
    else:
        print("Запуск отменен.")

def test_audio_bot():
    print("--- Тест создания 8D звука ---")
    file_path = input("Введите путь к аудио файлу (mp3/wav): ")
    if not os.path.exists(file_path):
        print("Файл не найден!")
        return
        
    disp = Dispatcher(project_root)
    bot = AudioBot(disp)
    result = bot.create_8d_effect(file_path)
    if result:
        print(f"Готово! 8D версия здесь: {result}")
    else:
        print("Ошибка при обработке аудио.")

if __name__ == "__main__":
    from bots.editor_bot.editor import EditorBot
    from bots.script_bot.script_writer import ScriptBot
    from bots.uploader_bot.uploader import UploaderBot
    from bots.audio_bot.audio_processor import AudioBot
    from bots.visual_bot.generator import VisualBot
    from bots.script_bot.trend_analyst import TrendBot

    while True:
        print("\n--- 🏭 CONTENT FACTORY: DEV CONTROL ---")
        print("1. Скачать видео (yt-dlp)")
        print("2. Монтаж: Нарезка / Эффекты (EditorBot)")
        print("3. Текст: Описания и теги (ScriptBot / OpenAI)")
        print("4. Фото: Nano Banana Pro (VisualBot / Gemini)")
        print("5. Звук: 8D Эффект (AudioBot)")
        print("6. Звук: Озвучка текста (TTS)")
        print("7. Загрузка: Playwright (UploaderBot)")
        print("---------------------------------------")
        print("8. ТЕСТ: Запустить полную цепочку")
        print("9. Показать очередь задач")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ")
        
        if choice == "1": test_download()
        elif choice == "2": test_editor()
        elif choice == "3": test_script_bot()
        elif choice == "4": test_visual_bot()
        elif choice == "5": test_audio_bot()
        elif choice == "6": test_tts()
        elif choice == "7": test_uploader()
        elif choice == "8": run_full_pipeline()
        elif choice == "9": show_queue()
        elif choice == "0": break
        else: print("Неверный выбор.")
