import requests
from dataclasses import dataclass
from telegram import Bot

from mirror import Mirror, SimpleLookup
from utils import register, fetchers

@register('ex')
class ExphyMirror(Mirror):
    @dataclass
    class DataFormat(Mirror.SerializedMirror):
        login_url: str
        page_url: str
        xpath_fmt: str
        login_token_pattern: str
        username: str
        password: str

    def _login(self, session: requests.Session):
        login_token = self.find_regex(
            self._data.login_token_pattern,
            url=self._data.login_url,
            session=session
        )
        login_form = {
            'username': self._data.username,
            'password': self._data.password,
            'logintoken': login_token
        }

        response = session.post(self._data.login_url, data=login_form)
        response.raise_for_status()

    def fetch(self) -> (bytes, None):
        with requests.Session() as session:
            self._login(session)

            xpath = self._data.xpath_fmt.format(n=self._data.n)
            pdf_url = self.find_xpath(
                xpath,
                url=self._data.page_url,
                session=session
            )
            if not pdf_url:
                return None

            pdf = session.get(pdf_url)
            pdf.raise_for_status()

            return pdf


@register('theo')
class TheoMirror(SimpleLookup):
    pass

@register('ana')
class AnaMirror(SimpleLookup):
    pass

@register('la')
class TheoMirror(SimpleLookup):
    pass

@register('homa')
class HoMaMirror(SimpleLookup):
    pass

