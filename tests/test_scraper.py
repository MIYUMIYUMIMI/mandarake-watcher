from mandarake_watcher.scraper import parse_items


SAMPLE_HTML = """
<html>
    <body>
        <div
            class="block"
            data-adult="0"
            data-itemidx="1349446110"
        >
            <div class="basic">
                <p class="shop">
                    中野店
                </p>
            </div>

            <div class="pic">
                <img src="https://img.example.com/test.jpg">
            </div>

            <div class="title">
                <p>
                    <a href="/order/detailPage/item?itemCode=1349446110">
                        ポケットモンスター フシギダネ
                    </a>
                </p>
            </div>

            <div class="price">
                <p>
                    1,500円
                    (税込 1,650円)
                </p>
            </div>
        </div>
    </body>
</html>
"""


def test_parse_items_returns_one_item() -> None:
    items = parse_items(SAMPLE_HTML)

    assert len(items) == 1


def test_parse_items_extracts_fields() -> None:
    items = parse_items(SAMPLE_HTML)

    item = items[0]

    assert item.item_code == "1349446110"
    assert item.title == "ポケットモンスター フシギダネ"
    assert item.shop == "中野店"
    assert item.price == "1,500円 (税込 1,650円)"
    assert item.image_url == "https://img.example.com/test.jpg"

    assert (
        item.url
        == "https://order.mandarake.co.jp/"
        "order/detailPage/item?"
        "itemCode=1349446110"
    )


def test_parse_items_skips_invalid_cards() -> None:
    html = """
    <div class="block">
        <div class="title">
            <a>Missing item code</a>
        </div>
    </div>
    """

    items = parse_items(html)

    assert items == []