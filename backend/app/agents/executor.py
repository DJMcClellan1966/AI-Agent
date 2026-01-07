"""
Task Executor - Celery worker for executing agent tasks
"""
from celery import Celery
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.task import Task, TaskStatus
from app.models.agent import Agent, AgentType
from app.agents.email_agent import EmailAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.coordinator_agent import CoordinatorAgent

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "agentic_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


def get_agent_instance(agent: Agent):
    """Get the appropriate agent instance"""
    agent_mapping = {
        AgentType.EMAIL: EmailAgent,
        AgentType.SCHEDULER: SchedulerAgent,
        AgentType.FINANCE: FinanceAgent,
        AgentType.COORDINATOR: CoordinatorAgent
    }
    
    agent_class = agent_mapping.get(agent.agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent.agent_type}")
    
    return agent_class(
        agent_id=agent.id,
        user_id=agent.user_id,
        config=agent.config or {}
    )


@celery_app.task(name="execute_task_async", bind=True, max_retries=3)
def execute_task_async(self, task_id: int):
    """Execute a task asynchronously"""
    db = SessionLocal()
    
    try:
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return {"error": "Task not found"}
        
        # Get agent
        agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
        if not agent:
            logger.error(f"Agent {task.agent_id} not found")
            task.status = TaskStatus.FAILED
            task.error_message = "Agent not found"
            db.commit()
            return {"error": "Agent not found"}
        
        # Update task status
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        db.commit()
        
        # Get agent instance
        agent_instance = get_agent_instance(agent)
        
        # Execute task
        logger.info(f"Executing task {task_id} with agent {agent.id}")
        result = agent_instance.execute(task.input_data)
        
        # Update task with result
        if result.get("error"):
            task.status = TaskStatus.FAILED
            task.error_message = result["error"]
            agent.tasks_failed += 1
        else:
            task.status = TaskStatus.COMPLETED
            task.output_data = result
            task.completed_at = datetime.utcnow()
            agent.tasks_completed += 1
        
        # Update agent metrics
        agent.tasks_pending = max(0, agent.tasks_pending - 1)
        total_tasks = agent.tasks_completed + agent.tasks_failed
        if total_tasks > 0:
            agent.success_rate = int((agent.tasks_completed / total_tasks) * 100)
        agent.last_active = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Task {task_id} completed successfully")
        return {"success": True, "task_id": task_id, "result": result}
        
    except Exception as e:
        logger.error(f"Error executing task {task_id}: {e}", exc_info=True)
        
        # Update task
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            
            # Retry if under max retries
            if task.retry_count < task.max_retries:
                logger.info(f"Retrying task {task_id} (attempt {task.retry_count + 1})")
                db.commit()
                raise self.retry(exc=e, countdown=60 * (task.retry_count + 1))
            
            db.commit()
        
        return {"error": str(e)}
        
    finally:
        db.close()


@celery_app.task(name="analyze_and_predict")
def analyze_and_predict():
    """Periodic task to analyze user patterns and predict needs"""
    db = SessionLocal()
    
    try:
        # Get all active coordinator agents
        agents = db.query(Agent).filter(
            Agent.agent_type == AgentType.COORDINATOR,
            Agent.status == "active"
        ).all()
        
        for agent in agents:
            try:
                coordinator = CoordinatorAgent(
                    agent_id=agent.id,
                    user_id=agent.user_id,
                    config=agent.config or {}
                )
                
                # Predict needs based on context
                context = {
                    "task_history": [],  # Would fetch from database
                    "time_of_day": datetime.now().strftime("%H"),
                    "day_of_week": datetime.now().strftime("%A").lower()
                }
                
                predictions = coordinator.predict_needs(context)
                
                # Create predicted tasks
                for prediction in predictions:
                    if prediction.get("confidence", 0) > 0.8:
                        logger.info(f"Creating predicted task for user {agent.user_id}: {prediction}")
                        # Would create task here
                        
            except Exception as e:
                logger.error(f"Error predicting for agent {agent.id}: {e}")
        
    finally:
        db.close()


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "analyze-and-predict": {
        "task": "analyze_and_predict",
        "schedule": 3600.0,  # Every hour
    },
}
