"""Database operations using Supabase."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)


class Database:
    """Supabase database client."""

    def __init__(self):
        """Initialize Supabase client."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase credentials not configured")
            self.client: Optional[Client] = None
        else:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
                self.client = None

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.client is not None

    # ─────────────────────────────────────────────────────────────
    # USER OPERATIONS
    # ─────────────────────────────────────────────────────────────

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if not self.client:
            return None
        try:
            response = self.client.table("users").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    def create_user(
        self, user_id: str, email: str, full_name: str = "", is_premium: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Create new user."""
        if not self.client:
            return None
        try:
            data = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "is_premium": is_premium,
                "premium_until": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            response = self.client.table("users").insert(data).execute()
            logger.info(f"Created user: {user_id}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user record."""
        if not self.client:
            return False
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.client.table("users").update(updates).eq("id", user_id).execute()
            logger.info(f"Updated user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    # ─────────────────────────────────────────────────────────────
    # USAGE TRACKING
    # ─────────────────────────────────────────────────────────────

    def log_usage(self, user_id: str, feature: str, count: int = 1) -> bool:
        """Log feature usage for a user."""
        if not self.client:
            return False
        try:
            today = datetime.now().date().isoformat()
            # Try to update existing record for today
            try:
                self.client.table("usage_logs").update(
                    {f"{feature}_count": f"{feature}_count + {count}"}
                ).eq("user_id", user_id).eq("date", today).execute()
            except:
                # If no record exists, create new one
                data = {
                    "user_id": user_id,
                    "date": today,
                    f"{feature}_count": count,
                }
                self.client.table("usage_logs").insert(data).execute()
            
            logger.info(f"Logged usage for {user_id}: {feature} x{count}")
            return True
        except Exception as e:
            logger.error(f"Error logging usage: {e}")
            return False

    def get_today_usage(self, user_id: str) -> Dict[str, int]:
        """Get usage for today for a user."""
        if not self.client:
            return {}
        try:
            today = datetime.now().date().isoformat()
            response = (
                self.client.table("usage_logs")
                .select("*")
                .eq("user_id", user_id)
                .eq("date", today)
                .single()
                .execute()
            )
            data = response.data
            return {
                "quizzes": data.get("quiz_count", 0),
                "past_papers": data.get("past_paper_count", 0),
                "plans": data.get("plan_count", 0),
                "learn_sessions": data.get("learn_count", 0),
            }
        except Exception as e:
            logger.debug(f"No usage record found for today: {e}")
            return {
                "quizzes": 0,
                "past_papers": 0,
                "plans": 0,
                "learn_sessions": 0,
            }

    # ─────────────────────────────────────────────────────────────
    # SUBSCRIPTION OPERATIONS
    # ─────────────────────────────────────────────────────────────

    def create_subscription(
        self, user_id: str, stripe_subscription_id: str, plan_type: str = "monthly"
    ) -> bool:
        """Create or update subscription record."""
        if not self.client:
            return False
        try:
            duration_days = 30 if plan_type == "monthly" else 365
            premium_until = datetime.now() + timedelta(days=duration_days)

            data = {
                "user_id": user_id,
                "stripe_subscription_id": stripe_subscription_id,
                "plan_type": plan_type,
                "status": "active",
                "started_at": datetime.now().isoformat(),
                "renews_at": premium_until.isoformat(),
            }
            self.client.table("subscriptions").insert(data).execute()

            # Update user as premium
            self.update_user(user_id, {"is_premium": True, "premium_until": premium_until.isoformat()})

            logger.info(f"Created subscription for {user_id}: {plan_type}")
            return True
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return False

    def cancel_subscription(self, user_id: str) -> bool:
        """Cancel user's subscription."""
        if not self.client:
            return False
        try:
            self.client.table("subscriptions").update({"status": "cancelled"}).eq(
                "user_id", user_id
            ).execute()
            self.update_user(user_id, {"is_premium": False, "premium_until": None})
            logger.info(f"Cancelled subscription for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False

    # ─────────────────────────────────────────────────────────────
    # STORED DATA (Quiz scores, Plans, etc.)
    # ─────────────────────────────────────────────────────────────

    def save_quiz_result(
        self, user_id: str, topic: str, subject: str, score: int, total: int
    ) -> bool:
        """Save quiz result."""
        if not self.client:
            return False
        try:
            data = {
                "user_id": user_id,
                "subject": subject,
                "topic": topic,
                "score": score,
                "total": total,
                "percentage": int((score / total * 100)) if total > 0 else 0,
                "created_at": datetime.now().isoformat(),
            }
            self.client.table("quiz_results").insert(data).execute()
            self.log_usage(user_id, "quiz")
            logger.info(f"Saved quiz result for {user_id}: {score}/{total}")
            return True
        except Exception as e:
            logger.error(f"Error saving quiz result: {e}")
            return False

    def save_study_plan(self, user_id: str, subject: str, plan_text: str) -> bool:
        """Save generated study plan."""
        if not self.client:
            return False
        try:
            data = {
                "user_id": user_id,
                "subject": subject,
                "plan_text": plan_text,
                "created_at": datetime.now().isoformat(),
            }
            self.client.table("study_plans").insert(data).execute()
            self.log_usage(user_id, "plan")
            logger.info(f"Saved study plan for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving study plan: {e}")
            return False

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        if not self.client:
            return {}
        try:
            quizzes = self.client.table("quiz_results").select("*").eq("user_id", user_id).execute()
            plans = self.client.table("study_plans").select("*").eq("user_id", user_id).execute()

            total_quizzes = len(quizzes.data) if quizzes.data else 0
            avg_score = 0
            if total_quizzes > 0:
                avg_score = sum(q["percentage"] for q in quizzes.data) / total_quizzes

            return {
                "total_quizzes": total_quizzes,
                "average_score": round(avg_score, 1),
                "study_plans_created": len(plans.data) if plans.data else 0,
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}


# Global database instance
db = Database()
