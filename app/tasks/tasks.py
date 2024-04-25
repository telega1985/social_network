import smtplib

from app.config import settings
from app.tasks.celery_app import celery
from app.tasks.email_templates import create_user_verification_template


@celery.task
def send_email_report_dashboard(user: dict, verification_token: str):
    """ Отправка письма пользователю
    """
    email = create_user_verification_template(user, verification_token)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(email)
