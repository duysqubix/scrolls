"""
custom paginators
"""
from world.utils.utils import clear_terminal
from evennia.utils import justify
from evennia import EvForm
from evennia.utils.evmore import EvMore


class BookEvMore(EvMore):
    def init_str(self, text):
        # """The input is a string"""

        # we must break very long lines into multiple ones. Note that this
        # will also remove spurious whitespace.
        justify_kwargs = self._justify_kwargs or {}
        width = 23
        justify_kwargs["width"] = width
        justify_kwargs["align"] = "l"
        justify_kwargs["indent"] = 0

        lines = []
        for line in text.split("\n"):
            if len(line) > width:
                lines.extend(justify(line, **justify_kwargs).split("\n"))
            else:
                lines.append(line)

        page_height = 15

        self._data = [
            "\n".join(lines[i:i + page_height])
            for i in range(0, len(lines), page_height)
        ]
        self._npages = len(self._data)

    def display(self, show_footer=True):
        """
            Pretty-print the page.
            """
        _DISPLAY = """{text}
            (|wmore|n [{pageno}/{pagemax}] retur|wn|n|||wb|nack|||wt|nop|||we|nnd|||wq|nuit)"""
        pos = 0
        text = "[no content]"
        if self._npages > 0:
            pos = self._npos
            try:
                pages = (self.paginator(pos), self.paginator(pos + 1))
            except IndexError:
                pages = (self.paginator(pos), None)

            text = self.page_formatter(pages)
        if show_footer:
            page = _DISPLAY.format(text=text,
                                   pageno=pos + 1,
                                   pagemax=self._npages)
        else:
            page = text
        # check to make sure our session is still valid
        sessions = self._caller.sessions.get()
        if not sessions:
            self.page_quit()
            return
        # this must be an 'is', not == check
        if not any(ses for ses in sessions if self._session is ses):
            self._session = sessions[0]
        # clear screen if client supports telnet
        clear_terminal(self._caller)
        self._caller.msg(text=page, session=self._session, **self._kwargs)

    def page_next(self):
        """
        Scroll the text to the next page. Quit if already at the end
        of the page.
        """
        if self._npos >= self._npages - 2:
            # exit if we are already at the end
            self.page_quit()
        else:

            self._npos += 2
            if self.exit_on_lastpage and self._npos >= (self._npages - 2):
                self.display(show_footer=False)
                self.page_quit(quiet=True)
            else:
                self.display()

    def page_formatter(self, page):
        lpage = page[0] if page[0] else ""
        rpage = page[1] if page[1] else ""

        form = EvForm("resources.forms.book")
        form.map(cells={1: lpage, 2: rpage})
        return str(form)