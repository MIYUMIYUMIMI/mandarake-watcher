import os

from mandarake_watcher.notifier import build_email
from mandarake_watcher.scraper import Item


def make_item() -> Item:
    return Item(
        item_code="TEST001",
        title="Pokemon Test Item",
        price="1,500円 (税込 1,650円)",
        shop="Test Shop",
        url="https://example.com/item",
        image_url="https://example.com/image.jpg",
    )


def test_build_email_subject(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "EMAIL_USER",
        "sender@example.com",
    )

    monkeypatch.setenv(
        "EMAIL_TO",
        "receiver@example.com",
    )

    message = build_email(
        "pokemon",
        [make_item()],
    )

    assert (
        message["Subject"]
        == "Mandarake Watcher: 1 new item(s) for 'pokemon'"
    )


def test_build_email_contains_text_content(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "EMAIL_USER",
        "sender@example.com",
    )

    monkeypatch.setenv(
        "EMAIL_TO",
        "receiver@example.com",
    )

    message = build_email(
        "pokemon",
        [make_item()],
    )

    text_part = message.get_body(
        preferencelist=("plain",)
    )

    assert text_part is not None

    content = text_part.get_content()

    assert "Pokemon Test Item" in content
    assert "1,500円" in content
    assert "Test Shop" in content
    assert "https://example.com/item" in content


def test_build_email_contains_html_image(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "EMAIL_USER",
        "sender@example.com",
    )

    monkeypatch.setenv(
        "EMAIL_TO",
        "receiver@example.com",
    )

    message = build_email(
        "pokemon",
        [make_item()],
    )

    html_part = message.get_body(
        preferencelist=("html",)
    )

    assert html_part is not None

    content = html_part.get_content()

    assert "Pokemon Test Item" in content
    assert "https://example.com/image.jpg" in content
    assert "View item" in content