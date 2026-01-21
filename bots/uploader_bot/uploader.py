import os
import json
from core.base_bot import BaseBot
from core.dispatcher import Dispatcher

class UploaderBot(BaseBot):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__("UploaderBot")
        self.dispatcher = dispatcher
        self.accounts_file = "/home/usic/.gemini/antigravity/scratch/autobot/data/accounts.json"

    def get_account_info(self, account_id):
        with open(self.accounts_file, 'r') as f:
            accounts = json.load(f)
            for acc in accounts:
                if acc["id"] == account_id:
                    return acc
        return None

    async def upload_tiktok(self, page, file_path, caption):
        """Логика загрузки видео в TikTok."""
        await page.goto("https://www.tiktok.com/upload")
        self.logger.info("Ожидание страницы загрузки...")
        
        # Ожидание селектора файла или кнопки загрузки
        await page.wait_for_selector('input[type="file"]')
        file_input = await page.query_selector('input[type="file"]')
        await file_input.set_input_files(file_path)
        
        self.logger.info(f"Файл {file_path} выбран. Заполнение описания...")
        
        # Заполнение описания
        # В TikTok описание часто в div с contenteditable
        await page.wait_for_selector('div[contenteditable="true"]')
        await page.fill('div[contenteditable="true"]', caption)
        
        self.logger.info("Нажатие кнопки Опубликовать...")
        # Селектор кнопки опубликовать может меняться, обычно это кнопка с текстом "Post" или "Опубликовать"
        await page.click('button:has-text("Post"), button:has-text("Опубликовать")')
        
        # Ждем подтверждения загрузки
        await page.wait_for_timeout(10000) 
        return True

    async def upload_youtube(self, page, file_path, caption):
        """Загрузка видео в YouTube Shorts."""
        self.logger.info("Начало загрузки в YouTube Studio...")
        await page.goto("https://studio.youtube.com")
        
        # Ожидание кнопки загрузки
        await page.wait_for_selector("#upload-icon")
        await page.click("#upload-icon")
        
        await page.wait_for_selector('input[type="file"]')
        file_input = await page.query_selector('input[type="file"]')
        await file_input.set_input_files(file_path)
        
        self.logger.info("Файл загружен, заполнение метаданных...")
        
        # Заполнение заголовка и описания
        # Обычно первый textbox - это заголовок
        await page.wait_for_selector('#textbox[contenteditable="true"]')
        textboxes = await page.query_selector_all('#textbox[contenteditable="true"]')
        if len(textboxes) > 0:
            await textboxes[0].fill(caption[:100]) # Заголовок
        
        # Выбор "Не для детей" (обязательно для загрузки)
        await page.click('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MADE_FOR_KIDS"]')
        
        # Кнопки Далее
        for _ in range(3):
            await page.click("#next-button")
            await page.wait_for_timeout(2000)
            
        # Публикация
        await page.click("#done-button")
        self.logger.info("YouTube: Видео отправлено на публикацию!")
        await page.wait_for_timeout(5000)
        return True

    async def upload_instagram(self, page, file_path, caption):
        """Загрузка видео в Instagram Reels."""
        self.logger.info("Начало загрузки в Instagram...")
        await page.goto("https://www.instagram.com/")
        
        # Нажатие на кнопку Создать
        await page.wait_for_selector('svg[aria-label="New post"]')
        await page.click('svg[aria-label="New post"]')
        
        await page.wait_for_selector('input[type="file"]')
        file_input = await page.query_selector('input[type="file"]')
        await file_input.set_input_files(file_path)
        
        # Ожидание обработки и кнопки Далее
        await page.wait_for_selector('div:has-text("Next")')
        await page.click('div:has-text("Next")')
        await page.wait_for_timeout(1000)
        await page.click('div:has-text("Next")') # Второй раз для фильтров
        
        # Описание
        await page.wait_for_selector('div[aria-label="Write a caption..."]')
        await page.fill('div[aria-label="Write a caption..."]', caption)
        
        # Поделиться
        await page.click('div:has-text("Share")')
        self.logger.info("Instagram: Видео опубликовано!")
        await page.wait_for_timeout(5000)
        return True

    async def start_upload_process(self, file_path, caption, account_id):
        from playwright.async_api import async_playwright
        account = self.get_account_info(account_id)
        if not account:
            return False

        profile_path = os.path.join("/home/usic/.gemini/antigravity/scratch/autobot/data/profiles", account["name"])
        
        async with async_playwright() as p:
            proxy = {"server": account["proxy"]} if account.get("proxy") else None
            
            # ВАЖНО: для соцсетей лучше использовать браузер с видимым окном для отладки или качественный headless
            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=True,
                proxy=proxy,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            page = await context.new_page()
            success = False
            
            try:
                if account["platform"] == "tiktok":
                    success = await self.upload_tiktok(page, file_path, caption)
                elif account["platform"] == "youtube":
                    success = await self.upload_youtube(page, file_path, caption)
                elif account["platform"] == "instagram":
                    success = await self.upload_instagram(page, file_path, caption)
            except Exception as e:
                self.logger.error(f"Ошибка при автоматизации {account['platform']}: {e}")
                # Скриншот для отладки
                await page.screenshot(path=f"data/debug_{account['platform']}_error.png")
            finally:
                await context.close()
            
            return success

    def run(self):
        import asyncio
        task = self.dispatcher.get_next_task("upload_video")
        if task:
            account_id = task.get("account_id")
            if not account_id:
                self.logger.warning("Задача на загрузку без ID аккаунта!")
                return

            self.dispatcher.update_task_status(task["id"], "processing")
            
            # Запускаем асинхронный процесс загрузки
            try:
                success = asyncio.run(self.start_upload_process(
                    task["data"]["file_path"], 
                    task["data"]["caption"], 
                    account_id
                ))
                
                if success:
                    self.logger.info(f"Видео успешно опубликовано на {account_id}!")
                    self.dispatcher.update_task_status(task["id"], "completed")
                else:
                    self.dispatcher.update_task_status(task["id"], "failed")
            except Exception as e:
                self.logger.error(f"Критическая ошибка UploaderBot: {e}")
                self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для загрузки.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = UploaderBot(disp)
    bot.run()
