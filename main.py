#!/usr/bin/env python3

from src import mangadex


if __name__ == "__main__":
    WHAT_IS_THE_MANGAS_NAME = "Berserk"

    # Search mangadex.org using a title, return a list of related manga(s) as ``mangadex.Manga`` objects.
    manga_search = mangadex.MangaSearch().search_by_title(WHAT_IS_THE_MANGAS_NAME)

    manga_matched = None
    for manga in manga_search:  # Search through returned list for a casefolded title match.
        if manga.title.casefold() == WHAT_IS_THE_MANGAS_NAME.casefold():
            manga_matched = manga  # A match is found, so change the ``manga_matched`` variable to it.
            break

    # This will then found the manga that matched the search if one was found.
    if manga_matched is not None:
        mangadex.MangaChapters(manga_matched.id).download_all()
    
    # Just for testing >500 pages offset implementation.
    # manga_by_id = mangadex.MangaSearch().search_by_id("227e3f72-863f-46f9-bafe-c43104ca29ee")
    # mangadex.MangaChapters(manga_by_id.id).download_chapter_by_number("510")
