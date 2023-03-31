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
from requests import Response, get as gets
from random import choice
from urllib.request import Request, urlopen
from subprocess import run

import tempfile as tmpf
import argparse


def gather_sauce(soup: BeautifulSoup) -> list[str]:
    """
    Meet the Scout.
    """
    links: list[str] = []
    for a in soup.find_all("a"):
        link = a.get("href")
        if link is not None and "https" in link:
            if "page=post" in link:
                links.append(link)
    return links


def get_main_image(soup: BeautifulSoup) -> str:
    """
    returns: str
    """
    imgs: list[str] = []
    for img in soup.find_all("img", src=True):
        link = img.get("src")
        if link is not None:
            if "https" in link:
                imgs.append(link)
    return imgs[2]


def make_sauce(args: dict[str, Any]) -> str:
    """
    Let the man cook

    returns: str
    """
    link: str = "https://gelbooru.com/index.php?page=post&s=list&tags="

    nsfw: str = args["nsfw"]
    if nsfw == "on":
        link += "rating%3aexplicit"
    else:
        # default
        link += "rating%3ageneral"

    if args["tag"] is not None:
        tags: str = args["tag"]
        for tag in tags.split(","):
            link += f"+{tag}"

    return link


def parse_flags() -> dict[str, Any]:
    """
    returns: {str: Any}
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--nsfw",
        help="fallen to the dark side, You have.",
        choices=["on", "off"],
    )

    parser.add_argument(
        "--tag",
        help="same as tag but looks into more details\n Example: --tag X,Y,Z",
        type=str,
    )

    return vars(parser.parse_args())


def main() -> None:
    args: dict[str, Any] = parse_flags()

    url: str = make_sauce(args)
    response: Response = gets(url)
    soup = BeautifulSoup(response.content, "html.parser")

    images: list[str] = gather_sauce(soup)
    sauce: str = choice(images)
    response = gets(sauce)
    soup = BeautifulSoup(response.content, "html.parser")

    with tmpf.NamedTemporaryFile() as f:
        request_site = Request(
            get_main_image(soup), headers={"User-Agent": "Mozilla/5.0"}
        )
        webpage = urlopen(request_site).read()
        f.write(webpage)
        run(["neofetch", "--source", f.name])


if __name__ == "__main__":
    main()
