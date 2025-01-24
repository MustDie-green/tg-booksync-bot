import smtplib
import ssl
from email.message import EmailMessage
from config import (
    YANDEX_LOGIN,
    YANDEX_PASSWORD
)

def send_book_via_yandex(
    to_email: str,
    subject: str,
    text_body: str,
    file_bytes: bytes,
    file_name: str,
    sender_email: str = YANDEX_LOGIN,
    sender_password: str = YANDEX_PASSWORD,
):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content(text_body)

    msg.add_attachment(
        file_bytes,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)