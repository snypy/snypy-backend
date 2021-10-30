from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

User = get_user_model()


@receiver(post_save, sender=User)
def add_user_to_default_groups(sender, instance, created,**kwargs):
    if created:
        groups = Group.objects.filter(name__in=settings.REGISTRATION_DEFAULT_GROUPS)
        instance.groups.add(*groups)
