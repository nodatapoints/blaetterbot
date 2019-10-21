from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, asdict
import re
from io import BytesIO

import logging

import requests
import lxml.etree as etree

from .database import get_n, increment_n

__all__ = 'Mirror', 'SimpleLookup', 'SimpleGet'

log = logging.getLogger('fetch')

class Mirror(metaclass=ABCMeta):
    """Abstact base class for all Mirrors
    A Mirror is provided a defined set of initializing parameters in `dict`.
    Every Mirror Class must implement
    - a DataFormat subclass used to parse the parameters, that inherits from
      Mirror.SerializedMirror. To be implemented as class attribute

      This dataclass extends the required parameters of SerializedMirror with
      configuration parameters specific to the new Mirror. This is used to
      ensure consistency when loading and saving from configuration files.

    - an unique name

      A class attribute used to u
    - a fetch method
    """
    @dataclass
    class SerializedMirror:
        name: str
        file_format: str

    def __init__(self, data: dict):
        assert issubclass(self.DataFormat, Mirror.SerializedMirror)
        self._data = self.DataFormat(**data)
        self.n = get_n(self.lecture_id)

    def DataFormat(self):
        raise NotImplementedError('no DataFormat defined')

    @property
    def lecture_id(self):
        raise NotImplementedError('class attribute lecture_id missing')

    def increment(self):
        increment_n(self.lecture_id)

    @property
    def data(self) -> dict:
        return asdict(self._data)

    @property
    def filename(self) -> str:
        return self._data.file_format.format(n=self.n)

    @abstractmethod
    def fetch(self) -> (bytes, None):
        pass

    def process_pdf(self, pdf: requests.Response) -> bytes:
        assert pdf.headers['Content-Type'] == 'application/pdf', \
            f'Expected content type "application/pdf", got "{pdf.headers["Content-Type"]}"'

        fp = BytesIO()
        fp.write(pdf.content)
        fp.seek(0)

        return fp

    def get(self, url: str, session: requests.Session=None, *, as_text=False,
            as_content=False) -> requests.Response:
        response = (session or requests).get(url)
        response.raise_for_status()

        if as_text:
            return response.text
        if as_content:
            return response.content
        return response

    def get_text(self, *, url: str=None, html: str=None,
                   session: requests.Session=None) -> str:
        if not (url or html):
            raise ValueError('No url or html provided')

        return html or self.get(url, session, as_text=True)

    def find_regex(self, pattern: str, **kwargs) -> str:
        text = self.get_text(**kwargs)
        match = re.search(pattern, text)
        if not match:
            log.debug(f'could not find pattern /{pattern}/')
            return None

        assert match.lastindex == 1, \
            f'expected exactly one group in pattern /{pattern}/, got {match.lastindex}'

        log.debug(f'found match "{match.group(1)}" for /{pattern}/')
        return match.group(1)

    def find_xpath(self, xpath: str, **kwargs) -> str:
        text = self.get_text(**kwargs)
        dom = etree.HTML(text)
        matches = dom.xpath(xpath)
        if not matches:
            return None

        if len(matches) > 1:
            log.warning(f'got multiple ({len(matches)}) matches for xpath "{xpath}"')

        log.debug(f'found match "{matches[0]}" for "{xpath}"')
        return matches[0]

class SimpleLookup(Mirror):
    @dataclass
    class DataFormat(Mirror.SerializedMirror):
        page_url: str
        link_pattern: str
        link_base: str

    def fetch(self):
        pattern = self._data.link_pattern.format(n=self.n)
        pdf_url = self.find_regex(pattern, url=self._data.page_url)
        if not pdf_url:
            return None

        pdf = requests.get(self._data.link_base + pdf_url)
        pdf.raise_for_status()
        return pdf

class SimpleGet(Mirror):
    @dataclass
    class DataFormat(Mirror.SerializedMirror):
        link: str

    def fetch(self):
        url = self._data.link.format(n=self.n)
        pdf = requests.get(url)
        if pdf.ok:
            return pdf
