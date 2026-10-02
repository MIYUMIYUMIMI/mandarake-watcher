from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from mandarake_watcher.scraper import Item


load_dotenv()


def build_email(
    keyword: str,
    items: list[Item],
) -> EmailMessage:
    email_user = os.getenv("EMAIL_USER")
    email_to = os.getenv("EMAIL_TO")

    if not email_user:
        raise ValueError(
            "EMAIL_USER is not configured."
        )

    if not email_to:
        raise ValueError(
            "EMAIL_TO is not configured."
        )

    message = EmailMessage()

    message["From"] = email_user
    message["To"] = email_to
    message["Subject"] = (
        f"Mandarake Watcher: "
        f"{len(items)} new item(s) for '{keyword}'"
    )

    lines = [
        f"New Mandarake items found for: {keyword}",
        "",
    ]

    for item in items:
        lines.extend(
            [
                item.title,
                f"Price: {item.price}",
                f"Shop: {item.shop}",
                item.url,
                "",
                "-" * 60,
                "",
            ]
        )

    message.set_content(
        "\n".join(lines)
    )

    return message


def send_email(
    keyword: str,
    items: list[Item],
) -> None:
    if not items:
        return

    host = os.getenv(
        "EMAIL_HOST",
        "smtp.gmail.com",
    )

    port = int(
        os.getenv(
            "EMAIL_PORT",
            "587",
        )
    )

    email_user = os.getenv(
        "EMAIL_USER"
    )

    email_password = os.getenv(
        "EMAIL_PASSWORD"
    )

    if not email_user:
        raise ValueError(
            "EMAIL_USER is not configured."
        )

    if not email_password:
        raise ValueError(
            "EMAIL_PASSWORD is not configured."
        )

    message = build_email(
        keyword,
        items,
    )

    with smtplib.SMTP(
        host,
        port,
    ) as server:
        server.starttls()

        server.login(
            email_user,
            email_password,
        )

        server.send_message(
            message
        )

    print(
        f"Email notification sent "
        f"for {len(items)} new item(s)."
    )