from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mate.academy"

MENU = "TracksMenu_tracksListContainer__AGQYv"
CONTAINER = "flex-container"
LINK = "TracksList_link__bIVx5"
HERO_DISCRIPTION = "typography_headlineMedium__cOCGC"
CONTENT = "TableColumnsView_tableCellGray__4hadg"


@dataclass
class Course:
    name: str
    short_description: str
    duration: str
    # optional:
    modules: int | None = None
    topics: int | None = None


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_course(href: str) -> dict[str, str]:
    # print(f"Course link: {BASE_URL}{href}")
    data = {}
    card = get_soup(f"{BASE_URL}{href}")
    words = card.find("h1").get_text(strip=True)
    name = words.split()[0] + " " + words.split()[1]
    if name.split()[0].lower() == "курс" :
        name = words.split()[1] + " " + words.split()[2]

    name = name.split(":")[0].replace("+", " ").strip()
    # print(f"Course name: {name}")
    data["name"] = name

    words = card.find(
        "h2",
        class_=lambda x: x and HERO_DISCRIPTION in x
    ).get_text(strip=True)
    discription = words
    # print(f"Discription: {discription}")
    data["short_description"] = discription

    content = card.find_all(
        "div",
        class_=lambda x: x and CONTENT in x
    )[12].get_text(strip=True)
    # print(f"Content: {content}")
    data["duration"] = content

    return data


def parse_href(link: str) -> dict[str, str]:
    href = link.get("href")
    get_content = parse_course(href)
    return get_content


def parse_block(block: any) -> list[Course]:
    coureses = []
    get_data_course = None
    name = None
    decription = None
    duration = None

    ul = block.find(
        "ul", class_=lambda x: x and CONTAINER in x
    )

    list_li = ul.find_all("li")

    for li in list_li:
        link = li.find("a", class_=lambda x: x and LINK in x)
        if link:
            get_data_course = parse_href(link)
            name = get_data_course["name"]
            decription = get_data_course["short_description"]
            duration = get_data_course["duration"]
            course = Course(
                name=name,
                short_description=decription,
                duration=duration
            )
            coureses.append(course)

    return coureses


def get_all_courses() -> list[Course]:
    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Помилка під час завантаження сторінки: {e}")
        return []

    soup = get_soup(BASE_URL)

    courses = []
    course_blocks = soup.find_all(
        "div",
        class_=lambda x: x and MENU in x
    )
    # print("Found courses in blocks:", len(course_blocks))

    for block in course_blocks:
        try:
            # показываем начало карточки для отладки
            # print(f"\nParsing course card {i+1}:")
            block_data = parse_block(block)
            courses.extend(block_data)

        except AttributeError:
            # если структура немного отличается — пропускаем
            continue

    return courses


if __name__ == "__main__":
    all_courses = get_all_courses()
