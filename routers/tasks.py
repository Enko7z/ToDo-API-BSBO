from fastapi import APIRouter, FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]


@router.get("")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),  # считает количество записей в хранилище
        "tasks": tasks_db  # выводит всё, что есть в хранилище
    }


"""
4) создайте endpoint для поиска задач по ключевому слову в
названии или описании
GET /tasks/search
Пример запроса: /tasks/search?q=проект
async def search_tasks(q: str) -> dict:
Параметры: q: Ключевое слово для поиска (минимум 2 символа)
Возвращает:
- Список задач, содержащих ключевое слово в title или description
- Ошибку, если слово менее 2-х символов
- Ошибку 404, если статус не найден.
Ожидаемый формат ответа: { "query": "проект", "count": 2, "tasks":
[...] }
При выполнении задания обратите внимание на порядок
декораторов в коде. FastAPI определяет маршруты по порядку
объявления. И если оставить так, как описано в задании, то при
вызове /tasks/stats после /tasks/{task_id}, FastAPI будет думать, что
вызывается endpoint /tasks/{task_id} и преобразует "stats" в int.
Эндпоинт выдаст ошибку. Тоже произойдет и с GET /tasks/search, если
описать его в конце.
Нужно поменять порядок маршрутов в коде — все конкретные
пути (/tasks/stats, /tasks/search, /tasks/status/...) должны идти до
динамических (/tasks/{task_id}).
"""
@router.get("/search")
async def search_tasks(q: str) -> dict:
    # Проверяем длину ключевого слова
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Ключевое слово должно содержать минимум 2 символа"
        )
    
    # Фильтруем задачи по ключевому слову в названии или описании
    filtered_tasks = [
        task
        for task in tasks_db
        if (task["title"] and q.lower() in task["title"].lower()) or 
           (task["description"] and q.lower() in task["description"].lower())
    ]
    
    return {
        "query": q,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

"""
3) создайте endpoint для фильтрации задач по статусу
выполнения
GET /tasks/status/{status}
async def get_tasks_by_status(status: str) -> dict:
Параметры: status: Статус задачи ("completed" - выполненные,
"pending" - невыполненные).
Возвращает:
- Список задач с указанным статуса
- Ошибку 404, если статус не найден.
Ожидаемый формат ответа: { "status": "completed", "count": 1,
"tasks": [...] }
"""

@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    # Проверяем валидность статуса
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Неверный статус. Используйте: 'completed' для выполненных задач или 'pending' для невыполненных"
        )
    
    # Определяем булево значение для фильтрации
    is_completed = (status == "completed")
    
    # Фильтруем задачи по статусу
    filtered_tasks = [
        task
        for task in tasks_db
        if task["completed"] == is_completed
    ]
    
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException( #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4" #текст, который будет выведен пользователю
        )
    filtered_tasks = [
        task # ЧТО добавляем в список
        for task in tasks_db # ОТКУДА берем элементы
        if task["quadrant"] == quadrant # УСЛОВИЕ фильтрации
    ]
    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }


"""
2) создайте endpoint для получения статистики по задачам:
GET /tasks/stats
async def get_tasks_stats() -> dict:
Возвращает:
- Общее количество задач
- Количество задач в каждом квадранте (Q1, Q2, Q3, Q4)
- Количество выполненных и невыполненных задач.
Ожидаемый формат ответа: { "total_tasks": 5, "by_quadrant": { "Q1": 1,
"Q2": 1, "Q3": 1, "Q4": 1 }, "by_status": { "completed": 1, "pending": 3 } }
"""
@router.get("/stats")
async def get_tasks_stats() -> dict:
    # Общее количество задач
    total_tasks = len(tasks_db)
    
    # Количество задач по квадрантам
    by_quadrant = {
        "Q1": len([task for task in tasks_db if task["quadrant"] == "Q1"]),
        "Q2": len([task for task in tasks_db if task["quadrant"] == "Q2"]),
        "Q3": len([task for task in tasks_db if task["quadrant"] == "Q3"]),
        "Q4": len([task for task in tasks_db if task["quadrant"] == "Q4"])
    }
    
    # Количество задач по статусу выполнения
    completed_count = len([task for task in tasks_db if task["completed"]])
    pending_count = len([task for task in tasks_db if not task["completed"]])
    
    by_status = {
        "completed": completed_count,
        "pending": pending_count
    }
    
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }

"""
1) создайте endpoint для получения задачи по ID.
GET /tasks/{task_id}
async def get_task_by_id(task_id: int) -> dict:
Параметры: task_id: ID задачи (целое число).
Возвращает:
- Полную информацию о задаче, если она найдена
- Ошибку 404, если задача не найдена
"""
@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Задача с ID {task_id} не найдена"
        )
    return {
        "task": task,
        "message": f"Задача с ID {task_id} найдена"
    }