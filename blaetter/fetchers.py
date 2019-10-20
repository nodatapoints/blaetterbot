import requests
from dataclasses import dataclass
import logging

from .mirror import Mirror, SimpleLookup

logger = logging.getLogger('bot')

_fetchers = {}

def register(name):
    def wrapper(cls):
        assert issubclass(cls, Mirror)
        cls.lecture_id = name
        _fetchers[name] = cls
        return cls

    return wrapper

def fetchers(config_data):
    for cls_name, data in config_data['mirrors'].items():
        logger.debug(f'loading {cls_name}')
        cls = _fetchers[cls_name]
        instance = cls(data)
        yield instance
        data.update(instance.data)


@register('ex')
class ExphyMirror(Mirror):
    class LoginError(Exception):
        """Login failed"""

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
        if not login_token:
            logger.error('could not find logintoken')
            raise self.LoginError('no logintoken')

        logging.debug(f'logintoken={login_token}')

        login_form = {
            'username': self._data.username,
            'password': self._data.password,
            'logintoken': login_token
        }

        response = session.post(self._data.login_url, data=login_form)
        response.raise_for_status()
        logging.debug('logged in successfully')

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

