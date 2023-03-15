from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .models import StripeSubscriptionData

import json
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
UserModel = get_user_model()
# Create your views here.

def home(request):
    return render(request, 'home.html')

def checkout(request):
    PRICE_ID = 'price_1MlgA5L1SwZOdDPI1EhcXcSS'
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': PRICE_ID,
                },
            ],
            mode='subscription',
            success_url='http://localhost:8000'+reverse('success')+'?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000'+reverse('cancel')
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return HttpResponse("Server error")

def create_portal_session(request, *args, **kwargs):
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.

    checkout_session_id = request.GET.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = 'http://localhost:8000'

    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)

def success(request):
    context = {'session_id':request.GET.get('session_id')}
    return render(request=request, template_name='success.html', context=context)


def cancel(request):
    return render(request, 'cancel.html')

@csrf_exempt
def webhook_received(request, *args, **kwargs):
    webhook_secret = 'whsec_6eecdbe80df5af8204b0d12a38bd1e4d0334a701edceacd6408b9b123f6dd14a'
    request_data = json.loads(request.body.decode())

    # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
    stripe_signature = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload=request.body.decode(), sig_header=stripe_signature, secret=webhook_secret)
        data = event['data']
    except Exception as e:
        print(str(e))
        return JsonResponse({'status': 'faild'}, status=500)
    
    # Get the type of webhook event sent - used to check the status of PaymentIntents.
    event_type = event['type']


    email = request_data.get('data').get('object').get('email')
    user: str|None = None
    try:
        user = UserModel.objects.get(email=email)
        newStripeSubscriptionData = StripeSubscriptionData(
            user=user,
            subscription_data=str(request_data)
        )
        newStripeSubscriptionData.save()
    except UserModel.DoesNotExist as e:
        print(f'error on email addres {email}\n{e}')
        return JsonResponse({'status': 'faild'}, content_type="application/json", status=400)
    
    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print('Subscription canceled: %s', event.id)


    return JsonResponse({'status': 'success'})
