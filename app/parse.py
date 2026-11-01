import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://mate.academy/"


@dataclass
class Course:
    name: str
    short_description: str
    duration: str
    modules_count: int
    topics_count: int


def get_soup(url: str) -> BeautifulSoup:
    time.sleep(0.5)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def parse_single_course(course: Tag) -> Course:
    title_el = course.select_one("[class*='title']")
    name = title_el.text if title_el else ""
    description_el = course.select_one("[class*='description']")
    short_description = description_el.text if description_el else ""
    duration_el = course.select_one("[class*='duration']")
    duration = duration_el.text if duration_el else ""

    modules_count = 0
    topics_count = 0

    href_value = course.get("href", "")
    if href_value:
        course_url = urljoin(BASE_URL, href_value)
        inner_soup = get_soup(course_url)
        h2_element = inner_soup.find(
            "h2", string=re.compile(r"модул|тем", re.IGNORECASE)
        )
        if h2_element:
            numbers = re.findall(r"\d+", h2_element.text)
            if len(numbers) >= 2:
                modules_count = int(numbers[0])
                topics_count = int(numbers[1])
        if modules_count == 0:
            modules = inner_soup.select("[class*='moduleListItem']")
            modules_count = len(inner_soup.select("[class*='topicName']"))
            for module in modules:
                topics_el = module.select_one("[class*='topicsCount']")
                if topics_el:
                    topics_count += int(topics_el.text.split()[0])

    return Course(
        name=name,
        short_description=short_description,
        duration=duration,
        modules_count=modules_count,
        topics_count=topics_count
    )


def get_all_courses() -> list[Course]:
    soup = get_soup(BASE_URL)
    courses = soup.select("[class*='cardWrapper']")
    return [parse_single_course(course) for course in courses]
