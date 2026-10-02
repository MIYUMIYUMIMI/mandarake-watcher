from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


SEARCH_URL = "https://order.mandarake.co.jp/order/listPage/list"


@dataclass
class Item:
    item_code: str
    title: str
    price: str
    shop: str
    url: str
    image_url: str


def build_search_url(keyword: str) -> str:
    params = {
        "keyword": keyword,
    }

    return f"{SEARCH_URL}?{urlencode(params)}"


def fetch_search_page(keyword: str) -> str:
    url = build_search_url(keyword)

    profile_dir = ".mandarake_profile"

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="msedge",
            headless=False,
            locale="ja-JP",
            viewport={
                "width": 1400,
                "height": 900,
            },
        )

        page = context.pages[0]

        print("Opening Mandarake home page...")

        page.goto(
            "https://www.mandarake.co.jp/",
            wait_until="domcontentloaded",
            timeout=60_000,
        )

        page.wait_for_timeout(2000)

        print("Opening:", url)

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60_000,
        )

        try:
            page.wait_for_selector(
                "div.block[data-itemidx]",
                timeout=15_000,
            )
        except Exception:
            print(
                "Product cards were not detected "
                "within 15 seconds."
            )

        print("Final URL:", page.url)
        print("Title:", page.title())

        card_count = page.locator(
            "div.block[data-itemidx]"
        ).count()

        print(
            "Product cards:",
            card_count,
        )

        html = page.content()

        print(
            "HTML length:",
            len(html),
        )

        context.close()

        return html


def parse_items(html: str) -> list[Item]:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    items: list[Item] = []

    cards = soup.select(
        "div.block[data-itemidx]"
    )

    for card in cards:
        item_code = card.get(
            "data-itemidx",
            "",
        ).strip()

        title_link = card.select_one(
            "div.title a"
        )

        shop_element = card.select_one(
            "p.shop"
        )

        price_element = card.select_one(
            "div.price p"
        )

        image_element = card.select_one(
            "div.pic img"
        )

        if not item_code or title_link is None:
            continue

        title = " ".join(
            title_link.get_text(
                " ",
                strip=True,
            ).split()
        )

        shop = (
            " ".join(
                shop_element.get_text(
                    " ",
                    strip=True,
                ).split()
            )
            if shop_element
            else ""
        )

        price = (
            " ".join(
                price_element.get_text(
                    " ",
                    strip=True,
                ).split()
            )
            if price_element
            else ""
        )

        url = (
            "https://order.mandarake.co.jp/"
            "order/detailPage/item?"
            f"itemCode={item_code}"
        )

        image_url = (
            image_element.get(
                "src",
                "",
            )
            if image_element
            else ""
        )

        items.append(
            Item(
                item_code=item_code,
                title=title,
                price=price,
                shop=shop,
                url=url,
                image_url=image_url,
            )
        )

    return items


def search_mandarake(
    keyword: str,
) -> list[Item]:
    html = fetch_search_page(keyword)

    return parse_items(html)


if __name__ == "__main__":
    keyword = input(
        "Keyword to monitor: "
    ).strip()

    items = search_mandarake(
        keyword
    )

    print(
        f"\nFound {len(items)} items "
        f"for '{keyword}'\n"
    )

    for item in items[:20]:
        print(
            f"[{item.item_code}] "
            f"{item.title}"
        )

        print(
            f"Shop: {item.shop}"
        )

        print(
            f"Price: {item.price}"
        )

        print(
            f"Image: {item.image_url}"
        )

        print(
            item.url
        )

        print(
            "-" * 60
        )