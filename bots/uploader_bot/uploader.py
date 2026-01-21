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

    async def start_upload_process(self, file_path, caption, account_id):
        from playwright.async_api import async_playwright
        account = self.get_account_info(account_id)
        if not account:
            return False

        profile_path = os.path.join("/home/usic/.gemini/antigravity/scratch/autobot/data/profiles", account["name"])
        
        async with async_playwright() as p:
            proxy = {"server": account["proxy"]} if account.get("proxy") else None
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=True, # В проде запускаем в фоне
                proxy=proxy,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            page = await context.new_page()
            success = False
            
            try:
                if account["platform"] == "tiktok":
                    success = await self.upload_tiktok(page, file_path, caption)
                # Здесь можно добавить upload_instagram, upload_youtube и т.д.
            except Exception as e:
                self.logger.error(f"Ошибка при автоматизации: {e}")
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
            success = asyncio.run(self.start_upload_process(
                task["data"]["file_path"], 
                task["data"]["caption"], 
                account_id
            ))
            
            if success:
                self.logger.info("Видео успешно опубликовано!")
                self.dispatcher.update_task_status(task["id"], "completed")
            else:
                self.dispatcher.update_task_status(task["id"], "failed")
        else:
            self.logger.info("Нет задач для загрузки.")

if __name__ == "__main__":
    from core.dispatcher import Dispatcher
    disp = Dispatcher("/home/usic/.gemini/antigravity/scratch/autobot")
    bot = UploaderBot(disp)
    bot.run()
