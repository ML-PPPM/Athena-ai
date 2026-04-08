"""Stripe webhook handler for automatic subscription management."""
import json
import logging
import stripe
from flask import Flask, request, jsonify
from config import settings
from database import db
from payments import handle_payment_success

logger = logging.getLogger(__name__)

# Initialize Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for subscription events."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        else:
            # For development, trust the payload
            event = json.loads(payload)

    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return jsonify({'error': 'Webhook signature verification failed'}), 400
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({'error': 'Webhook processing error'}), 400

    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')

        if subscription_id:
            # Find user by subscription ID
            try:
                subscription_data = db.client.table('subscriptions').select('*').eq('stripe_subscription_id', subscription_id).single().execute()
                if subscription_data.data:
                    user_id = subscription_data.data['user_id']
                    handle_payment_success(subscription_id, user_id)
                    logger.info(f"Processed payment success for subscription {subscription_id}")
            except Exception as e:
                logger.error(f"Error processing payment success: {e}")

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']

        # Cancel subscription
        try:
            db.client.table('subscriptions').update({'status': 'cancelled'}).eq('stripe_subscription_id', subscription_id).execute()
            subscription_data = db.client.table('subscriptions').select('*').eq('stripe_subscription_id', subscription_id).single().execute()
            if subscription_data.data:
                user_id = subscription_data.data['user_id']
                db.update_user(user_id, {'is_premium': False, 'premium_until': None})
                logger.info(f"Cancelled subscription {subscription_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        logger.warning(f"Payment failed for subscription {subscription_id}")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=4242)