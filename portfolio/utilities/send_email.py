from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user):
    verification_link = f"http://localhost:3000/api/verify/{user.verification_token}/"
    send_mail(
        subject="Verify your email",
        message=f"Hi {user.name},\n\nClick to verify:\n{verification_link}\n\nThis link expires in 1 hour.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )