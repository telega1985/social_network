from email.message import EmailMessage

from app.config import settings


def create_user_verification_template(user: dict, verification_token: str):
    """ Создание письма для подтверждения почты
    """
    email = EmailMessage()

    email["Subject"] = "Подтверждение почты"
    email["From"] = settings.SMTP_USER
    email["To"] = user["email"]

    email.set_content(
        f"""
        <h1>Подтвердите почту</h1>
        <p>Перейдите по ссылке ниже, чтобы подтвердить ваш адрес электронной почты:</p>
        <a href="http://127.0.0.1:8000/auth/verify-email?token={verification_token}">Подтвердить почту</a>
        """,
        subtype="html"
    )

    return email
