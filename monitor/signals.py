from django.dispatch import receiver
from django.core.mail import send_mail
from allauth.account.signals import user_signed_up


@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):

    if not user.email:
        return

    send_mail(
        subject="Welcome to Pingger! 🔔",

        message=f"""
Hi {user.first_name or user.username},

Welcome to Pingger!

Your account has been successfully created.

You can now add your websites and let Pingger
monitor them for you.

We'll notify you when something goes wrong
and when your website comes back online.

Thanks,
Pingger Team
""",

        from_email=None,

        recipient_list=[
            user.email
        ],

        fail_silently=False,
    )