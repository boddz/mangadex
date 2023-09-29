====================
MangaDex API Wrapper
====================

An API wrapper for `mangadex.org <https://mangadex.org>`_'s public API. Credit goes to
`mangadex.org <https://mangadex.org>`_ for providing a very well documented public API. Please use this code within
reason and do not send an unnecessary amount of requests to MangaDex; I have implemented simple measures under the hood
make sure this is avoided if unintentional.

For official API documentation, you can find that `here <https://api.mangadex.org/docs/>`_.


-----
Usage
-----

For now, there is an example that shows you how to download a manga in the main.py file in the same directory as this
file.

.. code-block:: bash

    # Ubuntu (22.04.3 LTS) is what I use, should be similar on all Linux based platforms.
    # I always recommend setting a virtual environment to avoid dependecy contamination.

    sudo apt install python3-venv
    python -m venv venv && source venv/bin/activate

    pip install -r requirements.txt
    python main.py
