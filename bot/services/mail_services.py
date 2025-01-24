import smtplib
import ssl
import random
import datetime
from email.message import EmailMessage
from config import (
    YANDEX_LOGIN,
    YANDEX_PASSWORD
)
import logging

def generate_message(
        file_name: str,
        telegram_username: str,
        to_email: str,
        file_bytes: bytes,
        sender_email: str
):
    subject_templates = [
        "Новая книга: {file_name}",
        "Свежий файл: {file_name}",
        "Подарок: {file_name}",
        "Ваша книжка: {file_name}",
        "Держите вашу книгу: {file_name}",
    ]
    subject = random.choice(subject_templates).format(file_name=file_name)
    greetings = [
        f"Привет, {telegram_username}!",
        f"Здравствуйте, {telegram_username}!",
        f"Салют, {telegram_username}!",
        f"Хей, {telegram_username}!",
        f"Добрый день, {telegram_username}!"
    ]
    transitions = [
        f"Отправляю вашу книгу «{file_name}»:",
        f"Вы запросили книжку «{file_name}». Ловите!",
        f"Вот тот самый файл «{file_name}», о котором шла речь.",
        f"Как и просили, высылаю «{file_name}»:",
        f"Спешу поделиться файлом «{file_name}»!"
    ]
    extras = [
        "Приятного чтения!",
        "Надеюсь, вам понравится эта книга!",
        "Наслаждайтесь чтением!",
        "Буду рад, если книга окажется полезной!",
        "Если что-то будет не так с файлом, дайте знать!"
    ]
    sign_offs = [
        "С наилучшими пожеланиями,\nFlex Book Sync Bot",
        "Всегда к вашим услугам,\nBook Sender",
        "С уважением,\nВаш Книжный Бот",
        "Счастливого чтения,\nBook Bot",
        "До связи,\nTelegram Book Service"
    ]
    time_sent_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    greeting_line = random.choice(greetings)
    transition_line = random.choice(transitions)
    extra_line = random.choice(extras)
    sign_off_line = random.choice(sign_offs)
    text_body = (
        f"{greeting_line}\n\n"
        f"{transition_line}\n"
        f"{extra_line}\n\n"
        f"Отправлено: {time_sent_str}\n\n"
        f"{sign_off_line}\n"
    )

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content(text_body)
    logging.info(f'Отправляем письмо {subject, text_body}')

    msg.add_attachment(
        file_bytes,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    return msg

def send_book_via_yandex(
    file_name: str,
    telegram_username: str,
    to_email: str,
    file_bytes: bytes,
    sender_email: str = YANDEX_LOGIN,
    sender_password: str = YANDEX_PASSWORD,
):
    context = ssl.create_default_context()

    msg = generate_message(
        file_name=file_name,
        telegram_username=telegram_username,
        to_email=to_email,
        file_bytes=file_bytes,
        sender_email=sender_email,
    )

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)