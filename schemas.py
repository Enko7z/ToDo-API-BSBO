from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from pydantic import computed_field
# Базовая схема для Task.
# Все поля, которые есть в нашей "базе данных" tasks_db
class TaskBase(BaseModel):
    title: str = Field(
        ..., 
        min_length=3,
        max_length=100,
        description="Название задачи")
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание задачи")
    is_important: bool = Field(
        ...,
        description="Важность задачи")
    deadline_at: Optional[datetime] = Field(
        None,
        description = "Плановый срок выполнения задачи"
    )

class TaskCreate(TaskBase):
 pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Новое название задачи")
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание")
    is_important: Optional[bool] = Field(
        None,
        description="Новая важность")
    deadline_at: Optional[datetime] = Field(
        None,
        description="Новый дедлайн")
    completed: Optional[bool] = Field(
        None,
        description="Статус выполнения")

class TaskResponse(TaskBase):
    id: int = Field(
        ...,
    description="Уникальный идентификатор задачи",
    examples=[1])
    quadrant: str = Field(
    ...,
    description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)",
    examples=["Q1"])
    completed: bool = Field(
    default=False,
    description="Статус выполнения задачи")
    created_at: datetime = Field(
    ...,
    description="Дата и время создания задачи")
    completed_at: Optional[datetime] = Field(
        None,
        description="Дата и время завершения задачи")
    
    @computed_field
    @property
    def days_until_deadline(self) -> Optional[int]:
        """Вычисляемое поле: количество дней до дедлайна"""
        if self.deadline_at is None:
            return None
        now = datetime.now(timezone.utc)
        deadline = self.deadline_at
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        delta = deadline - now
        return delta.days
    
    @computed_field
    @property
    def is_urgent(self) -> bool:
        """Вычисляемое поле: срочность (True если до дедлайна <= 3 дня)"""
        if not self.deadline_at:
            return False
        days = self.days_until_deadline
        return days is not None and days <= 3

    class Config:
        from_attributes = True

class TimingStatsResponse(BaseModel):
    completed_on_time: int = Field(
        ...,
        description="Количество задач, завершенных в срок"
    )
    completed_late: int = Field(
        ...,
        description="Количество задач, завершенных с нарушением сроков"
    )
    on_plan_pending: int = Field(
        ...,
        description="Количество задач в работе, выполняемых в соответствии с планом"
    )
    overtime_pending: int = Field(
        ...,
        description="Количество просроченных незавершенных задач"
    )
