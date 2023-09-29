"""
======
Errors
======

All exceptions used in the module for catching and handling errors returned by the API/ CDN.
"""


class RateLimitedError(Exception): ...

class ResultNotOkayError(Exception):
    def __init__(self, json: dict) -> None:
        self.json = json

    def __str__(self) -> str:
        error = self.json['errors'][0]
        return f"Result not okay: <status {error['status']}> {error['title']}: {error['detail']}"
