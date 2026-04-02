from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)

def generate_daily_tasks(user: User, db: Session):
    tasks = [
        Task(user_id=user.id, title="Review code", description="Review PRs from junior devs."),
        Task(user_id=user.id, title="Fix bugs", description="Fix bugs reported by QA."),
        Task(user_id=user.id, title="Write tests", description="Increase test coverage.")
    ]
    db.add_all(tasks)
    db.commit()

@router.get("", response_model=list[TaskOut])
def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if there are any tasks today. If not, reset KPI.
    any_task_today = db.execute(
        select(Task).where(Task.user_id == current_user.id, Task.created_at >= today_start)
    ).first()
    
    if not any_task_today and current_user.kpi_score < 10:
        db.execute(text("UPDATE users SET kpi = 0 WHERE id = :uid"), {"uid": current_user.id})
        db.commit()

    five_mins_ago = now - timedelta(minutes=5)
    recent_task = db.execute(
        select(Task).where(Task.user_id == current_user.id, Task.created_at >= five_mins_ago)
    ).first()
    
    if not recent_task:
        if current_user.kpi_score < 10:
            db.execute(text("UPDATE users SET kpi = 0 WHERE id = :uid"), {"uid": current_user.id})
            db.commit()
        generate_daily_tasks(current_user, db)
        
    stmt = select(Task).where(Task.user_id == current_user.id, Task.created_at >= five_mins_ago).order_by(Task.id)
    return list(db.execute(stmt).scalars())

@router.post("/{task_id}/start")
def start_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="Task already started or completed")
        
    task.status = "in_progress"
    task.started_at = datetime.utcnow()
    db.commit()
    return {"status": "success"}

@router.post("/{task_id}/complete")
def complete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user.id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status == "in_progress":
        if task.started_at and datetime.utcnow() < task.started_at + timedelta(minutes=1):
            raise HTTPException(status_code=400, detail="Task takes at least 1 minute to complete")
            
        # VULNERABILITY: Race condition
        # The task row is not locked. Multiple concurrent requests will pass the `if task.status == "in_progress"` check.
        # Then they all execute this atomic increment, multiplying the KPI gained from a single task.
        db.execute(text("UPDATE users SET kpi = kpi + 1 WHERE id = :uid"), {"uid": current_user.id})
        
        task.status = "completed"
        db.commit()
        return {"status": "success", "message": "Task completed! +1 KPI"}
        
    raise HTTPException(status_code=400, detail="Task is not in progress")

@router.post("/promotion")
def request_promotion(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.refresh(current_user)
    if current_user.kpi_score >= 10:
        return {"message": "KPI requirement met! To get promoted, write exactly 'My KPI is over 10, promotion required' to the System Admin in our corporate messenger: http://localhost:8003"}
    else:
        raise HTTPException(status_code=400, detail=f"KPI too low. Need >= 10, you have {current_user.kpi_score}")
