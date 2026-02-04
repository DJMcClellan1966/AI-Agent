"""
Base Agent Class
All specialized agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.local_llm import get_local_llm

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: int, user_id: int, config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.user_id = user_id
        self.config = config or {}
        self.use_local = settings.USE_LOCAL_LLM
        self.llm = self._initialize_llm()
        logger.info(f"Initialized {self.__class__.__name__} for user {user_id} (Local: {self.use_local})")
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        # Use local LLM if enabled
        if self.use_local or self.config.get("use_local_llm", False):
            local_llm = get_local_llm()
            if local_llm.is_available():
                logger.info(f"Using local LLM: {local_llm.get_info()}")
                return local_llm
            else:
                logger.warning("Local LLM not available, falling back to API")
        
        # Fall back to API-based LLMs
        provider = self.config.get("llm_provider", "openai")
        
        if provider == "openai" and settings.OPENAI_API_KEY:
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )
        elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                temperature=0.7,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            logger.error("No LLM provider available!")
            return None
    
    def _generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using either local or API LLM"""
        if isinstance(self.llm, type(get_local_llm())):
            # Using local LLM
            return self.llm.generate(prompt, max_tokens=max_tokens)
        else:
            # Using LangChain API LLM
            try:
                response = self.llm.predict(prompt)
                return response
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return ""
    
    @abstractmethod
    async def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze input and determine what actions to take
        Returns: Dict with analysis results and recommended actions
        """
        pass
    
    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task
        Returns: Dict with execution results
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of agent capabilities
        """
        pass
    
    async def predict_needs(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict user needs based on context and history
        Returns: List of predicted tasks
        """
        # Default implementation - can be overridden
        return []
    
    async def validate_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate if an action is safe and within permissions
        """
        # Check permissions
        permissions = self.config.get("permissions", {})
        action_type = action.get("type")
        
        if action_type not in permissions.get("allowed_actions", []):
            logger.warning(f"Action {action_type} not in allowed permissions")
            return False
        
        return True
    
    async def request_approval(self, task_data: Dict[str, Any]) -> int:
        """
        Create a task that requires approval
        Returns: task_id
        """
        from app.db.database import SessionLocal
        from app.models.task import Task, TaskStatus
        
        db = SessionLocal()
        try:
            task = Task(
                user_id=self.user_id,
                agent_id=self.agent_id,
                title=task_data.get("title"),
                description=task_data.get("description"),
                task_type=task_data.get("type"),
                input_data=task_data.get("input_data", {}),
                status=TaskStatus.AWAITING_APPROVAL,
                requires_approval=True
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            logger.info(f"Created task {task.id} awaiting approval")
            return task.id
        finally:
            db.close()
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log agent activity"""
        logger.info(f"Agent {self.agent_id} - {activity_type}: {details}")
