from pydantic import BaseModel
from typing import Optional


class SubscriptionUpdate(BaseModel):
    tier: str  # "pro" or "premium"


class SubscriptionResponse(BaseModel):
    subscription_tier: str
    subscription_status: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    checkout_url: Optional[str] = None
