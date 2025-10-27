# main/signals.py
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import RitoAccount, generate_rito_id


@receiver(post_save, sender=User)
def create_user_rito_account(sender, instance, created, **kwargs):
    """Create RitoAccount when a new User is created"""
    if created:
        try:
            # Check if RitoAccount already exists using get_or_create
            rito_account, created = RitoAccount.objects.get_or_create(
                user=instance,
                defaults={
                    'rito_id': generate_rito_id(),
                    'name': instance.username
                }
            )
            if created:
                print(f"Created RitoAccount for {instance.username}")
        except Exception as e:
            print(f"Error creating RitoAccount for {instance.username}: {e}")