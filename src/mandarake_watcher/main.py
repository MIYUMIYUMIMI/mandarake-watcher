from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import yaml

from mandarake_watcher.notifier import send_email
from mandarake_watcher.scraper import search_mandarake
from mandarake_watcher.storage import save_items


CONFIG_PATH = Path("config.yaml")


def load_config() -> tuple[list[str], int]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.yaml was not found."
        )

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file)

    keywords = config.get(
        "keywords",
        [],
    )

    interval = config.get(
        "check_interval_seconds",
        300,
    )

    if not keywords:
        raise ValueError(
            "No keywords configured."
        )

    return keywords, int(interval)


def check_keyword(keyword: str) -> None:
    print()
    print("=" * 70)
    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"Checking: {keyword}"
    )
    print("=" * 70)

    try:
        items = search_mandarake(
            keyword
        )

        print(
            f"Found {len(items)} current items."
        )

        new_items = save_items(
            keyword,
            items,
        )

        if not new_items:
            print(
                f"No new items found for '{keyword}'."
            )
            return

        print(
            f"\nNEW ITEMS for '{keyword}': "
            f"{len(new_items)}\n"
        )

        for item in new_items:
            print(
                f"[NEW] {item.title}"
            )
            print(
                f"Shop: {item.shop}"
            )
            print(
                f"Price: {item.price}"
            )
            print(
                item.url
            )
            print(
                "-" * 60
            )

        send_email(
            keyword,
            new_items,
        )

    except Exception as error:
        print(
            f"Error while checking "
            f"'{keyword}': {error}"
        )


def run_monitor() -> None:
    keywords, interval = load_config()

    print(
        "Mandarake Watcher started."
    )

    print(
        "Keywords:",
        ", ".join(keywords),
    )

    print(
        f"Check interval: {interval} seconds"
    )

    print(
        "Press Ctrl+C to stop."
    )

    while True:
        for keyword in keywords:
            check_keyword(keyword)

        print()
        print(
            f"Waiting {interval} seconds..."
        )

        time.sleep(interval)


if __name__ == "__main__":
    try:
        run_monitor()

    except KeyboardInterrupt:
        print()
        print(
            "Mandarake Watcher stopped."
        )