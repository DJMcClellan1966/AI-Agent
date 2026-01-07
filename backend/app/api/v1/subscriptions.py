from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, SubscriptionTier
from app.core.security import get_current_active_user
from app.schemas.subscription import SubscriptionResponse, SubscriptionUpdate

router = APIRouter()


@router.get("/", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current subscription information"""
    return {
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "stripe_customer_id": current_user.stripe_customer_id,
        "stripe_subscription_id": current_user.stripe_subscription_id
    }


@router.post("/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upgrade subscription (create Stripe checkout session)"""
    import stripe
    from app.core.config import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            metadata={"user_id": current_user.id}
        )
        current_user.stripe_customer_id = customer.id
        db.commit()
    
    # Create checkout session
    price_id = settings.STRIPE_PRICE_ID_PRO if subscription_data.tier == "pro" else settings.STRIPE_PRICE_ID_PREMIUM
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.CORS_ORIGINS[0]}/subscription/success",
            cancel_url=f"{settings.CORS_ORIGINS[0]}/subscription/cancel"
        )
        
        return {
            "subscription_tier": current_user.subscription_tier,
            "subscription_status": current_user.subscription_status,
            "checkout_url": checkout_session.url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    import stripe
    from app.core.config import settings
    
    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        stripe.Subscription.delete(current_user.stripe_subscription_id)
        current_user.subscription_tier = SubscriptionTier.FREE
        current_user.subscription_status = "cancelled"
        current_user.stripe_subscription_id = None
        db.commit()
        
        return {
            "subscription_tier": current_user.subscription_tier,
            "subscription_status": current_user.subscription_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
