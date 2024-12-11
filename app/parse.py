import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def get_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("small.author").text,
        tags=[tag.text for tag in quote.select_one(".tags").findAll(
            "a", class_="tag"
        )],
    )


def get_current_page(url: str) -> BeautifulSoup:
    text = requests.get(url).content
    return BeautifulSoup(text, "html.parser")


def parse_quotes_from_page(current_page: BeautifulSoup) -> list[Quote]:
    quotes = current_page.select(".quote")
    return [get_quote(quote) for quote in quotes]


def parse_quotes() -> list[Quote]:
    current_page = get_current_page(BASE_URL)
    all_quotes = parse_quotes_from_page(current_page)
    current_page_num = 1
    while current_page.select_one("li.next a"):
        current_page_num += 1
        next_url = f"{BASE_URL}page/{current_page_num}/"
        current_page = get_current_page(next_url)
        quotes = parse_quotes_from_page(current_page)
        all_quotes.extend((quote for quote in quotes))
    return all_quotes


def write_quotes_to_csv(quotes: list, output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = parse_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
