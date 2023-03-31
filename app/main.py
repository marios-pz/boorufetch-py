"""
The GPLv3 License (GPLv3)

Copyright (c) 2023 Author Freedom Penguin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from typing import Any
from bs4 import BeautifulSoup
from requests import get as gets
from random import choice
from urllib.request import Request, urlopen
from subprocess import run

import tempfile as tmpf
import argparse


def gather_links(soup: BeautifulSoup) -> list[str]:
    links: list[str] = []
    for a in soup.find_all("a"):
        link = a.get("href")
        if link is not None and "https" in link:
            if "page=post" in link:
                links.append(link)
    return links


def get_main_image(soup: BeautifulSoup) -> str:
    imgs: list[str] = []
    for img in soup.find_all("img", src=True):
        link = img.get("src")
        if link is not None:
            if "https" in link:
                imgs.append(link)
    # TODO: Sometimes it gathers a thumbnail instead of the main image,
    # it needs better filtering
    return imgs[2]


# TODO: multiple use of --tag does not work
def tag_handler(args: dict[str, Any]) -> str:
    link: str = "https://gelbooru.com/index.php?page=post&s=list&tags="

    nsfw: str = args["nsfw"]
    if nsfw == "on":
        link += "rating%3aexplicit"
    else:
        # default
        link += "rating%3ageneral"
    tag: str | None = args["tag"]
    if tag is not None:
        link += f"+{tag}"

    if args["tags"] is not None:
        tags: str = args["tags"]
        for tag in tags.split(","):
            link += f"+{tag}"
    return link


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--nsfw",
        help="fallen to the dark side, You have.",
        choices=["on", "off"],
    )
    parser.add_argument(
        "--tag", help="runs with specific tag\n Example: --tags X", type=str
    )
    parser.add_argument(
        "--tags",
        help="same as tag but looks into more details\n Example: --tags X,Y,Z",
        type=str,
    )

    parser.add_argument(
        "--backend",
        help="backend engine for neofetch",
        type=str,
    )

    args = vars(parser.parse_args())
    url: str = tag_handler(args)
    backend = args["backend"]

    response = gets(url)
    soup = BeautifulSoup(response.content, "html.parser")

    images: list[str] = gather_links(soup)
    sauce: str = choice(images)
    response = gets(sauce)
    soup = BeautifulSoup(response.content, "html.parser")

    image_link = get_main_image(soup)

    with tmpf.NamedTemporaryFile() as f:
        request_site = Request(
            image_link, headers={"User-Agent": "Mozilla/5.0"}
        )
        webpage = urlopen(request_site).read()
        f.write(webpage)
        if backend is None:
            run(["neofetch", "--source", f.name])
        else:
            run(["neofetch", "--backend", backend, "--source", f.name])


if __name__ == "__main__":
    main()
