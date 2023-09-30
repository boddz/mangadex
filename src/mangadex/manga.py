#!/usr/bin/env python3

"""
=====
Manga
=====

All manga related classes and methods for this mangadex.org API wrapper; used to gather statistics and information
about manga(s) on the site using title, tags sorting in specific orders and using filtering of tags and ratings.
"""

from __future__ import annotations

from dataclasses import dataclass

from ._handler import RequestHandler
from ._errors import *


@dataclass
class Manga:
    """
    Represents a manga using json data returned in search.
    """
    title: str
    description: str
    type: str
    id: str
    status: str
    year: str
    rating: str
    tags: list
    original_language: str
    available_languages: list
    links: dict


class MangaSearch:
    """
    Search mangadex.org for manga using provided methods in this class. Methods of this class will return either a
    ``Manga`` object or a list of ``Manga`` objects which will contain information about each matched manga such as
    titles and descriptions for example.

    :param proxies: A dict of proxies to use in the requests
    :type proxies: dict, optional

    :param preferred_lang: the language code to use when retrieving data
        See <https://api.mangadex.org/docs/3-enumerations/#language-codes--localization> for more information on this.
    :type preferred_lang: str, optional
    """
    def __init__(self, *, proxies: dict={}, preferred_lang: str="en") -> None:
        self.__request_handler = RequestHandler(proxies=proxies)
        self.__preferred_lang = preferred_lang

    @property
    def request_handler(self) -> RequestHandler:
        """
        The request handler object to be used.
        """
        return self.__request_handler

    @property
    def preferred_lang(self) -> str:
        """
        The preferred language that was specified.
        """
        return self.__preferred_lang

    def __manga_from_json(self, json: dict, lang: str="en") -> Manga:
        """
        Using raw json data for a single manga, convert it into a ``Manga`` object.
        """
        title = json["attributes"]["title"]["en"] if "en" in json["attributes"]["title"] else None  # Fallback title.
        for title_dict in json["attributes"]["altTitles"]:
            if lang in title_dict:
                title = title_dict[lang]
                break
        _manga = Manga(
            title=title,
            description=json["attributes"]["description"][lang] if lang in json["attributes"]["description"] else None,
            type=json["type"],
            id=json["id"],
            status=json["attributes"]["status"],
            year=json["attributes"]["year"],
            rating=json["attributes"]["contentRating"],
            tags=json["attributes"]["tags"],
            original_language=json["attributes"]["originalLanguage"],
            available_languages=json["attributes"]["availableTranslatedLanguages"],
            links=json["attributes"]["links"],
        )
        return _manga

    def __sort_format(self, sort: dict) -> dict:
        """
        Turns the order/ sort dict that was provided into deep object format ``<field>[<key>]=<value>``.
        """
        sort_formatted = {}
        for key, value in sort.items(): sort_formatted[f"order[{key}]"] = value
        return sort_formatted

    def search_by_id(self, manga_id: int) -> Manga:
        """
        Search for a manga using it's specific id hash.
        """
        json = self.request_handler.get(f"manga/{manga_id}").json()
        if "result" in json and json["result"] == "error": raise ResultNotOkayError(json)
        return self.__manga_from_json(json["data"], self.preferred_lang)

    def search_by_title(self, title: str, *, sort: dict={}) -> dict(Manga):
        """
        Search for a manga using it's plain text name.

        :param title: the plain text title to use in the search
        :type title: str

        :param sort: the order in which to sort the list of manga
            See <https://api.mangadex.org/docs/3-enumerations/#manga-order-options> for further information.
        :type sort: dict, optional

        :raises ResultNotOkayError: when the result in the response is non-ok

        :return: a list of ``Manga`` objects which contain information about each manga
        :rtype: Manga

        -----
        Usage
        -----

        ::

            from mangadex import MangaSearch

            ms = MangaSearch()

            # Outputs all of the manga ratings with a matching/ similar name containing the title sorted ascending.
            print(*[manga.rating for manga in ms.search_by_title("berserk", sort={"rating": "asc"})])
        """
        # params = {"title": title} if sort is None else {"title": title, **self.__sort_format(sort)}
        json = self.request_handler.get("manga", params={"title": title, **self.__sort_format(sort)}).json()
        if "result" in json and json["result"] == "error": raise ResultNotOkayError(json)
        return [self.__manga_from_json(manga_json, self.preferred_lang) for manga_json in json["data"]]

    def search_by_tags(self, *, include_tags: list, exclude_tags: list=[], sort: dict={}) -> dict(Manga):
        """
        Search for a manga using a list of both tags to include and those in which to exclude.

        :param include_tags: a list of strings (tags) to include in search
        :type title: list(str)

        :param exclude_tags: a list of strings (tags) to exclude in search
        :type title: list(str)

        :param sort: the order in which to sort the list of manga
            See <https://api.mangadex.org/docs/3-enumerations/#manga-order-options> for further information.
        :type sort: dict, optional

        :raises ResultNotOkayError: when the result in the response is non-ok

        :return: a list of ``Manga`` objects which contain information about each manga
        :rtype: Manga

        -----
        Usage
        -----

        ::

            from mangadex import MangaSearch

            ms = MangaSearch()

            # Outputs all of the manga titles with a matching/ similar name containing the title.
            print(*[manga.title for manga in ms.search_by_tags(include_tags=["Comedy"], exclude_tags=["Gore"])])
        """
        tags_json = self.request_handler.get("manga/tag").json()
        include_tags = [tag["id"] for tag in tags_json["data"] if tag["attributes"]["name"]["en"] in include_tags]
        exclude_tags = [tag["id"] for tag in tags_json["data"] if tag["attributes"]["name"]["en"] in exclude_tags]
        json = self.request_handler.get("manga", params={
            "includedTags[]": include_tags,
            "excludedTags[]": exclude_tags,
            **self.__sort_format(sort)  # **{a: b, c: d} => a: b, c: d - unpacks dict into separate kwargs pairs.
        }).json()
        if "result" in json and json["result"] == "error": raise ResultNotOkayError(json)
        return [self.__manga_from_json(manga_json, self.preferred_lang) for manga_json in json["data"]]
