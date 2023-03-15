from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Create your models here.

User = get_user_model()

class StripeSubscriptionData(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING
    )
    subscription_data = models.TextField()