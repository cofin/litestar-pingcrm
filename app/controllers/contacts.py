from __future__ import annotations

from litestar import Controller


class ContactController(Controller):
    include_in_schema = False
