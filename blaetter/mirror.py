from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, asdict
import re
from io import BytesIO

import logging

import requests
import lxml.etree as etree

logger = logging.getLogger('bot')

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
        n: int

    def __init__(self, data: dict):
        assert issubclass(self.DataFormat, Mirror.SerializedMirror)
        self._data = self.DataFormat(**data)

    # used to enforce class attribute "name"
    # when left undefined, the property is invoked and raises
    # an exception
    @property
    def name(self):
        raise NotImplementedError('no "name" attribute defined')

    def DataFormat(self):
        raise NotImplementedError('no DataFormat defined')

    @property
    def data(self) -> dict:
        return asdict(self._data)

    @property
    def filename(self) -> str:
        return self._data.file_format.format(n=self._data.n)

    @property
    def n(self):
        return self._data.n

    @n.setter
    def n(self, value):
        self._data.n = value

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
            logger.debug(f'could not find pattern /{pattern}/')
            return None

        assert match.lastindex == 1, \
            f'expected exactly one group in pattern /{pattern}/, got {match.lastindex}'

        logger.debug(f'found match "{match.group(1)}" for /{pattern}/')
        return match.group(1)

    def find_xpath(self, xpath: str, **kwargs) -> str:
        text = self.get_text(**kwargs)
        dom = etree.HTML(text)
        matches = dom.xpath(xpath)
        if not matches:
            return None

        if len(matches) > 1:
            logger.warning(f'got multiple ({len(matches)}) matches for xpath "{xpath}"')

        logger.debug(f'found match "{matches[0]}" for "{xpath}"')
        return matches[0]

class SimpleLookup(Mirror):
    @dataclass
    class DataFormat(Mirror.SerializedMirror):
        page_url: str
        link_pattern: str
        link_base: str

    def fetch(self):
        pattern = self._data.link_pattern.format(n=self._data.n)
        pdf_url = self.find_regex(pattern, url=self._data.page_url)
        if not pdf_url:
            return None

        pdf = requests.get(self._data.link_base + pdf_url)
        pdf.raise_for_status()
        return pdf
