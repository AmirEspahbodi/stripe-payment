from django.urls import path, include
from .views import home, checkout,create_portal_session ,success, cancel, webhook_received

urlpatterns = [
    path('', home, name='home'),
    path('checkout', checkout, name='checkout'),
    path('portal_session', create_portal_session, name='portal_session'),
    path('success', success, name='success'),
    path('webhook', webhook_received, name='webhook'),
    path('cancel', cancel, name='cancel')
]
