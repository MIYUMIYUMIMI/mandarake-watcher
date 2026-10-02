from __future__ import annotations

import html
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

    text_lines = [
        f"New Mandarake items found for: {keyword}",
        "",
    ]

    for item in items:
        text_lines.extend(
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
        "\n".join(text_lines)
    )

    cards: list[str] = []

    for item in items:
        safe_title = html.escape(
            item.title
        )

        safe_price = html.escape(
            item.price
        )

        safe_shop = html.escape(
            item.shop
        )

        safe_url = html.escape(
            item.url,
            quote=True,
        )

        safe_image_url = html.escape(
            item.image_url,
            quote=True,
        )

        image_html = ""

        if safe_image_url:
            image_html = f"""
            <div style="margin-bottom: 12px;">
                <img
                    src="{safe_image_url}"
                    alt="{safe_title}"
                    style="
                        width: 180px;
                        max-width: 100%;
                        height: auto;
                        border-radius: 8px;
                    "
                >
            </div>
            """

        card_html = f"""
        <div
            style="
                border: 1px solid #dddddd;
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 20px;
                font-family: Arial, sans-serif;
            "
        >
            {image_html}

            <h3
                style="
                    margin-top: 0;
                    margin-bottom: 12px;
                "
            >
                {safe_title}
            </h3>

            <p>
                <strong>Price:</strong>
                {safe_price}
            </p>

            <p>
                <strong>Shop:</strong>
                {safe_shop}
            </p>

            <p>
                <a
                    href="{safe_url}"
                    style="
                        display: inline-block;
                        padding: 10px 16px;
                        background: #222222;
                        color: #ffffff;
                        text-decoration: none;
                        border-radius: 6px;
                    "
                >
                    View item
                </a>
            </p>
        </div>
        """

        cards.append(card_html)

    html_body = f"""
    <html>
        <body
            style="
                max-width: 700px;
                margin: 0 auto;
                padding: 20px;
                font-family: Arial, sans-serif;
            "
        >
            <h2>
                New Mandarake items
            </h2>

            <p>
                Keyword:
                <strong>{html.escape(keyword)}</strong>
            </p>

            <p>
                Found {len(items)} new item(s).
            </p>

            {''.join(cards)}
        </body>
    </html>
    """

    message.add_alternative(
        html_body,
        subtype="html",
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