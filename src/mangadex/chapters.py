#!/usr/bin/env python3

"""
========
Chapters
========

Provides an interface class to interact with a manga's chapters and fetch information about a specific/ all chapters,
and on top of that provides an easy bundle of methods for downloading chapters based on certain criteria.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from ._handler import RequestHandler
from ._errors import *
from .manga import MangaSearch


@dataclass
class Chapter:
    """
    Represents a chapter on mangadex.org.
    """
    id: str
    title: str
    volume: str | None
    number: str
    pages: int


class MangaChapters:
    """
    An interface for fetching chapters related to a manga.

    :param manga_id: The manga ID hash to use.
    :type manga_id: str

    :param proxies: A dict of proxies to use in requests.
    :type proxies: dict, optional

    :param preferred_lang: the language code to use when retrieving data
        See <https://api.mangadex.org/docs/3-enumerations/#language-codes--localization> for more information on this.
    :type lang: str, optional
    """
    def __init__(self, manga_id: str, *, proxies: dict={}, preferred_lang: str="en") -> None:
        self.__manga_id = manga_id
        self.__request_handler = RequestHandler(proxies=proxies)
        self.__preferred_lang = preferred_lang
        self.__manga_obj = MangaSearch(proxies=proxies, preferred_lang=preferred_lang).search_by_id(self.__manga_id)

    @property
    def manga_id(self) -> str:
        """
        The manga ID hash.
        """
        return self.__manga_id

    @property
    def request_handler(self) -> RequestHandler:
        """
        The request handler object to be used when sending requests to the API/ CDN(s).
        """
        return self.__request_handler

    @property
    def preferred_lang(self) -> str:
        """
        The preferred language that was specified.
        """
        return self.__preferred_lang

    @property
    def manga_title(self) -> str:
        """
        The title for the manga.
        """
        return self.__manga_obj.title

    @property
    def __chapters_json(self) -> dict:
        """
        The raw json data for chapters. TODO: chapters > 500 using offset here.
        """
        json = self.request_handler.get(f"manga/{self.manga_id}/feed",
                                        params={"translatedLanguage[]": self.preferred_lang, "limit": 500}).json()
        return json

    @property
    def all(self) -> (int, list(Chapter)):  # TODO: manga pages > 500 using offset.
        """
        A list of all chapters as ``Chapter`` objects.
        """
        chapters = []
        for chapter in self.__chapters_json["data"]:
            chapters.append(
                Chapter(
                    id=chapter["id"],
                    title=chapter["attributes"]["title"],
                    volume=chapter["attributes"]["volume"],
                    number=chapter["attributes"]["chapter"],
                    pages=chapter["attributes"]["pages"]
                )
            )
        return (len(chapters), chapters)

    def _download(self, chapter: Chapter, *, datasaver: bool=False, path: str=None) -> None:
        """
        Download a specific chapter into a specified directory.

        :param chapter: The ``Chapter`` object to use for download
        :type chapter: Chapter

        :param datasaver: Whether to use lower quality compressed page images or original uncompressed
        :type datasaver: bool, optional

        :param path: The base directory in which to save the chapters to, it will be created if it does not exist yet
        :type path: str, optional
        """

        chapter_path = f"{chapter.number}: {chapter.title}" if chapter.title is not None else chapter.number
        path = f"{path}/{chapter_path}" if path else f"./{self.manga_title}/{chapter_path}"

        json = self.request_handler.get(f"at-home/server/{chapter.id}").json()

        if "result" in json and json["result"] == "error": raise ResultNotOkayError(json)
        if os.path.exists(path) is False: os.makedirs(path)

        pages = json["chapter"]["data"] if datasaver is False else json["chapter"]["dataSaver"]
        quality = "data" if datasaver is False else "data-saver"

        for index, page_url in enumerate(pages):
            ext_type = [seg for seg in page_url.split(".") if seg != ""][-1]
            with open(f"{path}/{index + 1}.{ext_type}", "wb") as page_image_file:
                page_dest = f"{quality}/{json['chapter']['hash']}/{page_url}"
                page_image_file.write(self.request_handler.get(page_dest, override_url=json['baseUrl']).content)

    def download_all(self, *, datasaver: bool=False, path: str=None) -> None:
        """
        Download all chapters of a manga using ``self.manga_id`` as the manga ID hash.

        :param datasaver: Whether to use lower quality compressed page images or original uncompressed
        :type datasaver: bool, optional

        :param path: The base directory in which to save the chapters to, it will be created if it does not exist yet
        :type path: str, optional


        -----
        Usage
        -----
        
        Downloads all of the chapters in Berserk:

        ::

            WHAT_IS_THE_MANGAS_NAME = "Berserk"

            # Search mangadex.org using a title, return a list of related manga(s) as ``mangadex.Manga`` objects.
            manga_search = mangadex.MangaSearch().search_by_title(WHAT_IS_THE_MANGAS_NAME)

            manga_matched = None
            for manga in manga_search:  # Search through returned list for a casefolded title match.
                if manga.title.casefold() == WHAT_IS_THE_MANGAS_NAME.casefold():
                    manga_matched = manga  # A match is found, so change the manga_matched variable to it.
                    break

            # This will then found the manga that matched the search if one was found.
            if manga_matched is not None: mangadex.MangaChapters(manga_matched.id).download_all()
        """
        total_chapters, all_chapters = self.all
        for index, chapter in enumerate(all_chapters):
            clear_line = "\r\x1b[2K"
            print(f"\r{clear_line}{self.manga_title}: Currently downloading chapter ({chapter.number}) "              \
                  f"\"{chapter.title}\" ~~> downloaded {index} out of {total_chapters} available chapters ", end="")
            self._download(chapter, datasaver=datasaver, path=path)
        print(f"\n{self.manga_title}: Successfully downloaded all chapters")


if __name__ == "__main__":
    mc = MangaChapters("40c12869-5686-4e21-9048-39882a026858")
    mc.download_all()
