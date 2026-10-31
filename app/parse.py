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
    response = requests.get(url).content
    return BeautifulSoup(response, "html.parser")


def parse_single_course(course: Tag) -> Course:
    modules_count = 0
    topics_count = 0

    course_link = course.find_parent("a")
    href_value = course_link["href"]
    course_url = urljoin(BASE_URL, href_value)
    if "courses" in href_value:
        inner_soup = get_soup(course_url)
        modules = inner_soup.select(".ft6NTW_moduleListItem")
        modules_count = len(modules)
        for module in modules:
            topics_count += int(module.select_one(".ft6NTW_topicsCount")
                                .text.split()[0])
    elif "skills" in href_value:
        inner_soup = get_soup(course_url)
        modules_count = int(inner_soup.select_one("h2.mt-4").text.split()[0])
        h2_element = inner_soup.select_one("h2.mt-4")
        numbers = re.findall(r"\d+", h2_element.text)
        topics_count = int(numbers[1])

    return Course(
        name=course.select_one(".FUm52q_title").text,
        short_description=course.select_one(".FUm52q_description").text,
        duration=course.select_one(".FUm52q_duration").text,
        modules_count=modules_count,
        topics_count=topics_count
    )


def get_all_courses() -> list[Course]:
    soup = get_soup(BASE_URL)
    courses = soup.select(".FUm52q_content")
    return [parse_single_course(course) for course in courses]


print(get_all_courses())
