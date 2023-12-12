from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class ShippingAddress(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address_lines = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=15)
    status = models.BooleanField(default=False)

    def _str_(self):
        return self.full_name

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_id = models.CharField(max_length=12, unique=True)
    balance = models.PositiveIntegerField(default=0)

    # def save(self, *args, **kwargs):
    #     if not self.wallet_id:
    #         # Generate a random wallet ID using uuid
    #         self.wallet_id = str(uuid.uuid4())[:12]

    #     super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.user.username}'s Wallet"

# function (create_wallet_for_new_user) should be called when a User instance is saved.   
@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    """
    Signal handler to create a Wallet instance for each new user.
    """
    if created:
        Wallet.objects.create(user=instance, wallet_id=str(uuid.uuid4())[:12])

# Connect the post_save signal to signal handler function
post_save.connect(create_wallet_for_new_user, sender=User)