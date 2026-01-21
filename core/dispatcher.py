import json
import os
from datetime import datetime

class Dispatcher:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.queue_file = os.path.join(workspace_dir, "data/pipeline_queue.json")
        self._init_queue()

    def _init_queue(self):
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, 'w') as f:
                json.dump([], f)

    def add_task(self, task_type: str, data: dict, status: str = "pending", account_id: int = None):
        """Добавляет новую задачу в конвейер с привязкой к аккаунту."""
        with open(self.queue_file, 'r+') as f:
            queue = json.load(f)
            new_task = {
                "id": len(queue) + 1,
                "type": task_type,
                "status": status,
                "account_id": account_id,
                "data": data,
                "created_at": datetime.now().isoformat()
            }
            queue.append(new_task)
            f.seek(0)
            json.dump(queue, f, indent=4)
        print(f"[Dispatcher] Добавлена задача: {task_type} для аккаунта: {account_id}")

    def approve_task(self, task_id: int):
        """Одобряет задачу, переводя её в статус 'pending' для следующего бота."""
        self.update_task_status(task_id, "pending")
        print(f"[Dispatcher] Задача {task_id} одобрена пользователем.")

    def get_next_task(self, bot_type: str):
        """Получает следующую доступную задачу для конкретного бота."""
        with open(self.queue_file, 'r') as f:
            queue = json.load(f)
        
        for task in queue:
            if task["type"] == bot_type and task["status"] == "pending":
                return task
        return None

    def add_niche_tasks(self, task_type: str, data: dict, niche: str, status: str = "pending"):
        """Добавляет задачи для всех аккаунтов в указанной нише (мультиплатформенность)."""
        accounts_file = os.path.join(self.workspace_dir, "data/accounts.json")
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)
                target_accounts = [a for a in accounts if a["niche"] == niche and a["status"] == "active"]
                
                for acc in target_accounts:
                    self.add_task(task_type, data, status=status, account_id=acc["id"])
                    print(f"[Dispatcher] Запланирована публикация для {acc['platform']} (Ниша: {niche})")
        else:
            print(f"[Dispatcher] Ошибка: файл аккаунтов не найден.")

    def update_task_status(self, task_id: int, status: str, result_data: dict = None):
        """Обновляет статус задачи и добавляет результат."""
        with open(self.queue_file, 'r+') as f:
            queue = json.load(f)
            for task in queue:
                if task["id"] == task_id:
                    task["status"] = status
                    if result_data:
                        task["result"] = result_data
                    task["updated_at"] = datetime.now().isoformat()
                    break
            f.seek(0)
            json.dump(queue, f, indent=4)
            f.truncate()
