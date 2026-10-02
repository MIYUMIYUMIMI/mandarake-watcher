from pathlib import Path

import mandarake_watcher.storage as storage
from mandarake_watcher.scraper import Item


def make_item(
    item_code: str,
    title: str,
) -> Item:
    return Item(
        item_code=item_code,
        title=title,
        price="1,000円",
        shop="Test Shop",
        url=(
            "https://order.mandarake.co.jp/"
            "order/detailPage/item?"
            f"itemCode={item_code}"
        ),
        image_url="https://example.com/image.jpg",
    )


def test_first_run_creates_baseline(
    tmp_path: Path,
) -> None:
    storage.DB_PATH = (
        tmp_path / "test.db"
    )

    items = [
        make_item(
            "TEST001",
            "First Item",
        ),
    ]

    new_items = storage.save_items(
        "pokemon",
        items,
    )

    assert new_items == []


def test_second_run_detects_new_item(
    tmp_path: Path,
) -> None:
    storage.DB_PATH = (
        tmp_path / "test.db"
    )

    first_items = [
        make_item(
            "TEST001",
            "First Item",
        ),
    ]

    storage.save_items(
        "pokemon",
        first_items,
    )

    second_items = [
        make_item(
            "TEST001",
            "First Item",
        ),
        make_item(
            "TEST002",
            "Second Item",
        ),
    ]

    new_items = storage.save_items(
        "pokemon",
        second_items,
    )

    assert len(new_items) == 1
    assert new_items[0].item_code == "TEST002"


def test_existing_item_is_not_reported_twice(
    tmp_path: Path,
) -> None:
    storage.DB_PATH = (
        tmp_path / "test.db"
    )

    items = [
        make_item(
            "TEST001",
            "First Item",
        ),
    ]

    storage.save_items(
        "pokemon",
        items,
    )

    new_items = storage.save_items(
        "pokemon",
        items,
    )

    assert new_items == []