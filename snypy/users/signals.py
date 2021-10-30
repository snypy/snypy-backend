from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created

User = get_user_model()


@receiver(post_save, sender=User)
def add_user_to_default_groups(sender, instance, created,**kwargs):
    if created:
        groups = Group.objects.filter(name__in=settings.REGISTRATION_DEFAULT_GROUPS)
        instance.groups.add(*groups)



@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': settings.RESET_PASSWORD_VERIFICATION_URL.format(token=reset_password_token.key)
    }

    msg = EmailMessage(
        # title:
        "Password Reset for {title} account".format(title="SnyPy"),
        # message:
        render_to_string('email/user_reset_password.txt', context),
        # from:
        "noreply@snypy.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.send()
