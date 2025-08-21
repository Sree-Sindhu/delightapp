from django.conf import settings
from django.core.mail import send_mail

class EmailService:
    """Email facade. Swappable later for providers like SendGrid/SES/SMTP APIs.
    In dev, Django console backend prints emails to terminal.
    """

    @staticmethod
    def send_order_received(user, order):
        to_email = getattr(user, 'email', None)
        if not to_email:
            return
        subject = f"Your DelightAPI order #{order.id} is received"
        body = (
            f"Hi {user.first_name or user.username},\n\n"
            f"Thanks for your order #{order.id}. We'll notify you when it's out for delivery.\n\n"
            f"- DelightAPI"
        )
        EmailService._send(subject, body, [to_email])

    @staticmethod
    def send_order_delivered(user, order):
        to_email = getattr(user, 'email', None)
        if not to_email:
            return
        subject = f"Your DelightAPI order #{order.id} was delivered"
        body = (
            f"Hi {user.first_name or user.username},\n\n"
            f"Great news! Your order #{order.id} has been delivered.\n\n"
            f"Enjoy your treats!\n- DelightAPI"
        )
        EmailService._send(subject, body, [to_email])

    @staticmethod
    def _send(subject: str, message: str, recipient_list: list[str]):
        """Default path uses Django send_mail. Replace with external provider later.
        Set EMAIL_BACKEND/DEFAULT_FROM_EMAIL in settings to use real SMTP.
        """
        try:
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), recipient_list, fail_silently=True)
        except Exception:
            # Intentionally silent to not break API flows
            pass
