from fastapi import APIRouter
from database import tasks_db
from typing import Dict, Any

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    responses={404: {"description": "Stats not found"}},
)

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