"""
Finance Agent - Manages bills, negotiations, and spending
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FinanceAgent(BaseAgent):
    """Agent for financial management"""
    
    def get_capabilities(self) -> List[str]:
        return [
            "track_bills",
            "negotiate_rates",
            "find_savings",
            "monitor_spending",
            "detect_subscriptions",
            "optimize_payments"
        ]
    
    async def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze finances and find opportunities"""
        bills = input_data.get("bills", [])
        subscriptions = input_data.get("subscriptions", [])
        spending = input_data.get("spending", [])
        
        # Analyze for savings opportunities
        opportunities = await self._find_savings_opportunities(bills, subscriptions)
        spending_insights = await self._analyze_spending(spending)
        
        return {
            "opportunities": opportunities,
            "insights": spending_insights,
            "summary": f"Found {len(opportunities)} savings opportunities"
        }
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute financial task"""
        action = task_data.get("action")
        
        if action == "negotiate_bill":
            return await self._negotiate_bill(task_data)
        elif action == "cancel_subscription":
            return await self._cancel_subscription(task_data)
        elif action == "find_better_rate":
            return await self._find_better_rate(task_data)
        elif action == "track_expense":
            return await self._track_expense(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _negotiate_bill(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate a bill with provider"""
        provider = task_data.get("provider")
        current_amount = task_data.get("current_amount")
        service_type = task_data.get("service_type")
        
        # Generate negotiation script using LLM
        prompt = f"""Generate a negotiation script for:
        Provider: {provider}
        Service: {service_type}
        Current amount: ${current_amount}/month
        
        Goals:
        - Request loyalty discount
        - Compare with competitor rates
        - Request price match
        - Be polite but firm
        
        Provide a professional negotiation template."""
        
        try:
            script = self.llm.predict(prompt)
            
            # Request approval for negotiation
            task_id = await self.request_approval({
                "title": f"Negotiate {service_type} bill with {provider}",
                "description": f"Current rate: ${current_amount}/month",
                "type": "negotiate_bill",
                "input_data": {
                    "provider": provider,
                    "script": script,
                    "current_amount": current_amount
                }
            })
            
            return {
                "success": True,
                "task_id": task_id,
                "script": script,
                "requires_approval": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _cancel_subscription(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel unused subscription"""
        subscription = task_data.get("subscription")
        reason = task_data.get("reason", "Not using the service")
        
        # Request approval
        task_id = await self.request_approval({
            "title": f"Cancel subscription: {subscription}",
            "description": reason,
            "type": "cancel_subscription",
            "input_data": {"subscription": subscription, "reason": reason}
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "requires_approval": True
        }
    
    async def _find_better_rate(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find better rates for services"""
        service_type = task_data.get("service_type")
        current_rate = task_data.get("current_rate")
        
        # Simulate finding better rates
        better_rates = [
            {"provider": "Provider A", "rate": current_rate * 0.85, "savings": current_rate * 0.15},
            {"provider": "Provider B", "rate": current_rate * 0.90, "savings": current_rate * 0.10}
        ]
        
        return {
            "success": True,
            "service_type": service_type,
            "current_rate": current_rate,
            "alternatives": better_rates,
            "potential_savings": sum(r["savings"] for r in better_rates) / len(better_rates)
        }
    
    async def _track_expense(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track an expense"""
        amount = task_data.get("amount")
        category = task_data.get("category")
        description = task_data.get("description")
        
        return {
            "success": True,
            "expense_id": f"exp_{datetime.now().timestamp()}",
            "amount": amount,
            "category": category,
            "tracked_at": datetime.now().isoformat()
        }
    
    async def _find_savings_opportunities(
        self,
        bills: List[Dict],
        subscriptions: List[Dict]
    ) -> List[Dict]:
        """Find savings opportunities"""
        opportunities = []
        
        # Check for unused subscriptions
        for sub in subscriptions:
            if sub.get("last_used_days_ago", 0) > 30:
                opportunities.append({
                    "type": "unused_subscription",
                    "item": sub.get("name"),
                    "savings": sub.get("monthly_cost"),
                    "action": "Consider canceling"
                })
        
        # Check for high bills
        for bill in bills:
            if bill.get("amount", 0) > 100:
                opportunities.append({
                    "type": "negotiate_bill",
                    "item": bill.get("provider"),
                    "potential_savings": bill.get("amount") * 0.15,
                    "action": "Negotiate for better rate"
                })
        
        return opportunities
    
    async def _analyze_spending(self, spending: List[Dict]) -> Dict[str, Any]:
        """Analyze spending patterns"""
        if not spending:
            return {"message": "No spending data available"}
        
        total = sum(s.get("amount", 0) for s in spending)
        categories = {}
        
        for spend in spending:
            cat = spend.get("category", "other")
            categories[cat] = categories.get(cat, 0) + spend.get("amount", 0)
        
        return {
            "total_spending": total,
            "by_category": categories,
            "top_category": max(categories, key=categories.get) if categories else None
        }
