from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mate.academy"

MENU = "TracksMenu_tracksListContainer__AGQYv"
CONTAINER = "flex-container"
LINK = "TracksList_link__bIVx5"
HERO_DESCRIPTION = "typography_headlineMedium__cOCGC"
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
    """Загружает страницу и возвращает BeautifulSoup объект"""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_course_name(card: BeautifulSoup) -> str:
    """Извлекает название курса из карточки"""
    h1_text = card.find("h1").get_text(strip=True)
    words = h1_text.split()

    # Убираем слово "Курс" если оно есть в начале
    if words[0].lower() == "курс":
        name = f"{words[1]} {words[2]}"
    else:
        name = f"{words[0]} {words[1]}"

    # Очищаем название от лишних символов
    return name.split(":")[0].replace("+", " ").strip()


def extract_description(card: BeautifulSoup) -> str:
    """Извлекает краткое описание курса"""
    h2 = card.find("h2", class_=lambda x: x and HERO_DESCRIPTION in x)
    return h2.get_text(strip=True) if h2 else ""


def extract_duration(card: BeautifulSoup) -> str:
    """Извлекает длительность курса"""
    duration_keywords = [
        "місяць", "місяця", "місяців",
        "тижднів", "тиждні", "тиждень",
        "month", "months",
        "week", "weeks",
        "hour", "hours", "година", "годин"
    ]

    content_divs = card.find_all("div", class_=lambda x: x and CONTENT in x)
    for div in content_divs:
        text = div.get_text(strip=True)
        if any(kw in text.lower() for kw in duration_keywords):
            return text


def parse_course_page(href: str) -> dict:
    """Парсит страницу конкретного курса"""
    try:
        card = get_soup(f"{BASE_URL}{href}")
    except requests.RequestException as e:
        print(f"Помилка під час завантаження сторінки: {e}")
        return []

    return {
        "name": extract_course_name(card),
        "short_description": extract_description(card),
        "duration": extract_duration(card)
    }


def parse_course_link(link_element: str) -> Course | None:
    """Парсит ссылку на курс и возвращает объект Course"""
    href = link_element.get("href")
    if not href:
        return None

    course_data = parse_course_page(href)
    return Course(**course_data)


def parse_menu_block(block: any) -> list[Course]:
    """Парсит блок меню с курсами"""
    courses = []

    ul = block.find("ul", class_=lambda x: x and CONTAINER in x)
    if not ul:
        return courses

    for li in ul.find_all("li"):
        link = li.find("a", class_=lambda x: x and LINK in x)
        if link:
            course = parse_course_link(link)
            if course:
                courses.append(course)

    return courses


def get_all_courses() -> list[Course]:
    """Главная функция: возвращает список всех курсов"""
    try:
        soup = get_soup(BASE_URL)
    except requests.RequestException as e:
        print(f"Помилка під час завантаження сторінки: {e}")
        return []

    courses = []
    menu_blocks = soup.find_all("div", class_=lambda x: x and MENU in x)

    for block in menu_blocks:
        courses.extend(parse_menu_block(block))

    return courses


if __name__ == "__main__":
    all_courses = get_all_courses()
