"""
Email Agent - Manages email sorting, drafting, and responses
"""
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EmailAgent(BaseAgent):
    """Agent for email management"""
    
    def get_capabilities(self) -> List[str]:
        return [
            "sort_emails",
            "draft_responses",
            "schedule_followups",
            "flag_urgent",
            "archive_old_emails",
            "unsubscribe_from_lists"
        ]
    
    async def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emails and suggest actions"""
        emails = input_data.get("emails", [])
        
        if not emails:
            return {"actions": [], "summary": "No emails to process"}
        
        # Use LLM to categorize and prioritize emails
        system_prompt = """You are an email management assistant. 
        Analyze the provided emails and categorize them by:
        - Urgency (urgent, high, medium, low)
        - Category (work, personal, promotional, social, spam)
        - Action required (reply, read, archive, delete)
        
        Return a JSON array of analyzed emails."""
        
        email_summaries = "\n".join([
            f"From: {e.get('from')}, Subject: {e.get('subject')}, Preview: {e.get('preview', '')[:100]}"
            for e in emails
        ])
        
        try:
            response = self._generate_text(
                f"{system_prompt}\n\nEmails:\n{email_summaries}"
            )
            
            return {
                "actions": self._generate_actions(response, emails),
                "summary": f"Analyzed {len(emails)} emails",
                "analysis": response
            }
        except Exception as e:
            logger.error(f"Email analysis failed: {e}")
            return {"error": str(e)}
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email management task"""
        action = task_data.get("action")
        
        if action == "sort_emails":
            return await self._sort_emails(task_data)
        elif action == "draft_response":
            return await self._draft_response(task_data)
        elif action == "schedule_followup":
            return await self._schedule_followup(task_data)
        elif action == "flag_urgent":
            return await self._flag_urgent(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _sort_emails(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sort emails into categories"""
        emails = task_data.get("emails", [])
        
        # Simulate email sorting (would integrate with actual email API)
        sorted_emails = {
            "urgent": [],
            "important": [],
            "regular": [],
            "promotional": []
        }
        
        for email in emails:
            # Use LLM to categorize
            category = "regular"  # Default
            sorted_emails[category].append(email)
        
        return {
            "success": True,
            "sorted_count": len(emails),
            "categories": {k: len(v) for k, v in sorted_emails.items()}
        }
    
    async def _draft_response(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Draft email response"""
        email = task_data.get("email")
        context = task_data.get("context", "")
        
        prompt = f"""Draft a professional email response to:
        From: {email.get('from')}
        Subject: {email.get('subject')}
        Body: {email.get('body')}
        
        Context: {context}
        
        Write a concise, professional response."""
        
        try:
            draft = self._generate_text(prompt)
            return {
                "success": True,
                "draft": draft,
                "requires_review": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _schedule_followup(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule email follow-up"""
        email_id = task_data.get("email_id")
        days = task_data.get("days", 3)
        
        followup_date = datetime.now() + timedelta(days=days)
        
        # Create follow-up task
        task_id = await self.request_approval({
            "title": f"Follow up on email: {task_data.get('subject', 'N/A')}",
            "description": f"Follow up scheduled for {followup_date.date()}",
            "type": "email_followup",
            "input_data": {"email_id": email_id, "date": followup_date.isoformat()}
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "followup_date": followup_date.isoformat()
        }
    
    async def _flag_urgent(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Flag email as urgent"""
        email_id = task_data.get("email_id")
        
        # Simulate flagging (would integrate with email API)
        return {
            "success": True,
            "email_id": email_id,
            "flagged": True
        }
    
    def _generate_actions(self, analysis: str, emails: List[Dict]) -> List[Dict]:
        """Generate actionable items from analysis"""
        # Parse LLM response and create actions
        actions = []
        
        # Example actions
        for email in emails[:5]:  # Top 5 emails
            actions.append({
                "type": "draft_response",
                "email_id": email.get("id"),
                "priority": "high"
            })
        
        return actions
