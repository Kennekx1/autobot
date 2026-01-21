import asyncio
from playwright.async_api import async_playwright
import os
import json

async def manual_login(account_id):
    accounts_file = "/home/usic/.gemini/antigravity/scratch/autobot/data/accounts.json"
    with open(accounts_file, 'r') as f:
        accounts = json.load(f)
        account = next((a for a in accounts if a["id"] == account_id), None)

    if not account:
        print(f"Аккаунт {account_id} не найден!")
        return

    profile_path = os.path.join("/home/usic/.gemini/antigravity/scratch/autobot/data/profiles", account["name"])
    os.makedirs(profile_path, exist_ok=True)

    async with async_playwright() as p:
        # Настройка прокси
        proxy = None
        if "proxy" in account and account["proxy"]:
            # Пример: http://user:pass@host:port
            proxy = {"server": account["proxy"]}

        print(f"Запуск браузера для {account['name']}...")
        print("Пожалуйста, залогиньтесь вручную. После входа закройте браузер или нажмите Ctrl+C здесь.")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            proxy=proxy,
            args=["--disable-blink-features=AutomationControlled"] # Скрываем, что это бот
        )
        
        page = await context.new_page()
        
        if account["platform"] == "tiktok":
            await page.goto("https://www.tiktok.com/login")
        elif account["platform"] == "instagram":
            await page.goto("https://www.instagram.com/accounts/login/")
        elif account["platform"] == "youtube":
            await page.goto("https://accounts.google.com/")

        # Держим браузер открытым, пока пользователь не закроет его
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Сохранение сессии...")
        finally:
            await context.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python login_helper.py <account_id>")
    else:
        asyncio.run(manual_login(int(sys.argv[1])))
