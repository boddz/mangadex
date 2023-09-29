"""
===============
Request Handler
===============

A simple request handler implemented using the requests module. This is the handler that should be used when sending
any requests to <https://mangadex.org>.
"""


from __future__ import annotations

from platform import uname
from time import sleep

from requests import Session, Response

from ._errors import RateLimitedError


class RequestHandler:
    """
    :param proxies: proxies connection to use for session
    :type proxies: dict, optional
    """
    def __init__(self, *, proxies: dict={}) -> None:
        self.__proxies = proxies
        self.__api_base_url = "https://api.mangadex.org"

    @property
    def api_base_url(self) -> str:
        """
        The base URL for the API <https://api.mangadex.org>.
        """
        return self.__api_base_url

    @property
    def user_agent(self) -> dict:
        """
        A truthful user agent to be sent in every request to mangadex.org based on package/ device information (nothing
        that breaches privacy more so than any browser would).
        """
        _os = uname()
        return {"User-Agent": f"MangaDex Scraper ({_os.system}; {_os.release}) {_os.machine}/{_os.node}"}

    @property
    def session(self) -> Session:
        """
        The session object that will be used in all requests to mangadex.org
        """
        _session = Session()
        _session.headers.update(self.user_agent)
        return _session

    def get(self, endpoint: str, *, params: dict={}, override_url: str=None) -> Response:
        """
        Sends a get request to <https://api.mangadex.org> (by default) with a specified endpoint and params.

        :param endpoint: The endpoint of the API/ CDN to hit in the request e.g. `manga/random`
        :type endpoint: str

        :param params: The data to be sent when hitting the endpoint as parameters
        :type params: dict, optional

        :param override_url: A base URL that can be specified to replace the default <https://api.mangadex.org>
        :type override_url: str, optional

        :raises RateLimitedError: If the first attempt status is 429 (too many requests)

        :return: The response object from the request
        :rtype: Response 
        """
        base_url = self.api_base_url if override_url is None else override_url
        try:
            resp = self.session.get(f"{base_url}/{endpoint}", proxies=self.__proxies, params=params)
            if resp.status_code == 429: raise RateLimitedError("429 too many requests...")
            return resp
        except RateLimitedError:
            self.__basic_rate_limiter(endpoint)
            return self.session.get(f"{base_url}/{endpoint}", proxies=self.__proxies, params=params)

    def __basic_rate_limiter(self, endpoint: str) -> None:
        """
        A basic rate limiter (internal) to be used when the :meth:``get`` raises a ``RateLimitedError``. Sleeps
        until decided cooldown has passed.

        For further information on rate limitations, please see: <https://api.mangadex.org/docs/2-limitations/>

        :param endpoint: The endpoint used to decide appropriate cooldown time
        :type endpoint: str
        """
        endpoint_split = [seg for seg in endpoint.split("/") if seg != ""]
        endpoint_split = endpoint_split[0] if len(endpoint_split) else None
        # Useful for POST/ PUT/ DELETE methods, as cooldown differs. For now, 60 is pretty much always used in GET
        available_cooldowns = {
            "at-home": 60,
            "__default": 60
        }
        which_cooldown = available_cooldowns[endpoint_split if endpoint_split in available_cooldowns else "__default"]
        clear_line = "\r\x1b[2K"
        while which_cooldown > -1:
            print(f"\r{clear_line}Hit rate limit for the `{endpoint}` endpoint, starting cooldown of "                \
                  f"{which_cooldown} seconds " if which_cooldown > 0 else clear_line, end="")
            sleep(1)
            which_cooldown -= 1
