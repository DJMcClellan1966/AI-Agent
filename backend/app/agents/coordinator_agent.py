"""
Coordinator Agent - Manages inter-agent communication and prioritization
"""
from typing import Dict, Any, List
import logging

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """Agent that coordinates other agents"""
    
    def get_capabilities(self) -> List[str]:
        return [
            "prioritize_tasks",
            "resolve_conflicts",
            "delegate_tasks",
            "monitor_progress",
            "learn_preferences",
            "optimize_workflow"
        ]
    
    async def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all agent activities and optimize"""
        pending_tasks = input_data.get("pending_tasks", [])
        agent_statuses = input_data.get("agent_statuses", {})
        user_preferences = input_data.get("user_preferences", {})
        
        # Prioritize tasks
        prioritized = await self._prioritize_tasks(pending_tasks, user_preferences)
        
        # Check for conflicts
        conflicts = await self._detect_conflicts(pending_tasks)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            agent_statuses,
            user_preferences
        )
        
        return {
            "prioritized_tasks": prioritized,
            "conflicts": conflicts,
            "recommendations": recommendations,
            "summary": f"Coordinated {len(pending_tasks)} tasks across agents"
        }
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordination task"""
        action = task_data.get("action")
        
        if action == "prioritize":
            return await self._prioritize_tasks(
                task_data.get("tasks", []),
                task_data.get("preferences", {})
            )
        elif action == "resolve_conflict":
            return await self._resolve_conflict(task_data)
        elif action == "delegate":
            return await self._delegate_task(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _prioritize_tasks(
        self,
        tasks: List[Dict],
        preferences: Dict[str, Any]
    ) -> List[Dict]:
        """Prioritize tasks based on urgency, importance, and user preferences"""
        if not tasks:
            return []
        
        # Use LLM to intelligently prioritize
        task_list = "\n".join([
            f"- {t.get('title')} (Type: {t.get('task_type')}, Priority: {t.get('priority')})"
            for t in tasks
        ])
        
        prompt = f"""Prioritize these tasks based on:
        - Urgency and deadlines
        - User preferences: {preferences}
        - Dependencies between tasks
        - Potential impact
        
        Tasks:
        {task_list}
        
        Return the task IDs in priority order (most important first)."""
        
        try:
            result = self.llm.predict(prompt)
            
            # Parse result and reorder tasks
            # Simplified: return tasks as-is
            return sorted(tasks, key=lambda t: t.get("priority", "medium"), reverse=True)
        except Exception as e:
            logger.error(f"Prioritization failed: {e}")
            return tasks
    
    async def _detect_conflicts(self, tasks: List[Dict]) -> List[Dict]:
        """Detect conflicts between tasks"""
        conflicts = []
        
        # Check for time conflicts
        for i, task1 in enumerate(tasks):
            for task2 in tasks[i+1:]:
                if self._tasks_conflict(task1, task2):
                    conflicts.append({
                        "task1": task1.get("id"),
                        "task2": task2.get("id"),
                        "reason": "Time conflict"
                    })
        
        return conflicts
    
    async def _resolve_conflict(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts between tasks"""
        conflict = task_data.get("conflict")
        task1 = conflict.get("task1")
        task2 = conflict.get("task2")
        
        # Use LLM to suggest resolution
        prompt = f"""Two tasks conflict:
        Task 1: {task1}
        Task 2: {task2}
        
        Suggest the best resolution:
        1. Prioritize one task
        2. Reschedule one task
        3. Delegate to different agent
        4. Cancel one task
        
        Provide reasoning."""
        
        try:
            resolution = self.llm.predict(prompt)
            return {
                "success": True,
                "resolution": resolution,
                "requires_approval": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _delegate_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to appropriate agent"""
        task = task_data.get("task")
        task_type = task.get("type")
        
        # Map task types to agents
        agent_mapping = {
            "email": "EmailAgent",
            "schedule": "SchedulerAgent",
            "finance": "FinanceAgent",
            "planning": "PlanningAgent"
        }
        
        target_agent = agent_mapping.get(task_type, "UnknownAgent")
        
        return {
            "success": True,
            "task_id": task.get("id"),
            "delegated_to": target_agent
        }
    
    async def _generate_recommendations(
        self,
        agent_statuses: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> List[str]:
        """Generate workflow recommendations"""
        recommendations = []
        
        # Check agent performance
        for agent_name, status in agent_statuses.items():
            if status.get("success_rate", 100) < 80:
                recommendations.append(
                    f"Review {agent_name} configuration - success rate below 80%"
                )
        
        return recommendations
    
    def _tasks_conflict(self, task1: Dict, task2: Dict) -> bool:
        """Check if two tasks conflict"""
        # Simplified conflict detection
        # In reality, would check schedules, resources, etc.
        return False
    
    async def predict_needs(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict user needs based on patterns"""
        history = context.get("task_history", [])
        time_of_day = context.get("time_of_day", "morning")
        day_of_week = context.get("day_of_week", "monday")
        
        predictions = []
        
        # Analyze patterns
        if time_of_day == "morning" and day_of_week == "monday":
            predictions.append({
                "type": "email",
                "action": "sort_emails",
                "reason": "Monday morning email check",
                "confidence": 0.9
            })
        
        if day_of_week == "friday":
            predictions.append({
                "type": "planning",
                "action": "plan_next_week",
                "reason": "Weekly planning",
                "confidence": 0.85
            })
        
        return predictions
