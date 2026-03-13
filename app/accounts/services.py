from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


def send_account_activation_email(request, user, uid, token):
    activation_url = reverse("accounts:verify", kwargs={"uidb64": uid, "token": token})
    subject = "Activate Your Account"
    message = f"""
Please verify your email:

{activation_url}
""" 

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )