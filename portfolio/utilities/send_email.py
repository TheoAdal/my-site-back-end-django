from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user):
    verification_link = f"http://localhost:3000/verify/{user.verification_token}/"
    send_mail(
        subject="Verify your email",
        message=f"Hi {user.name},\n\nClick to verify:\n{verification_link}\n\nThis link expires in 1 hour.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    
def send_reset_password_email(user):
    reset_link = f"http://localhost:3000/reset-password/{user.reset_password_token}/"
    send_mail(
        subject="Password Reset Request",
        message=f"Hi {user.name},\n\nYou are receiving this because you (or someone else) have requested the reset of the password for your account.\n\nPlease click on the following link, or paste this into your browser to complete the process:\n{reset_link}\n\nIf you did not request this, please ignore this email and your password will remain unchanged.\n",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )