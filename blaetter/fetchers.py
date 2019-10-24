import requests
from dataclasses import dataclass
import logging

from .mirror import *

log = logging.getLogger('fetch')

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
        log.debug(f'loading {cls_name}')
        cls = _fetchers[cls_name]
        instance = cls(data)
        yield instance
        data.update(instance.data)

class MoodleMirror(Mirror):
    class LoginError(Exception):
        """Login failed"""

    session = None
    def __init__(self, data):
        super().__init__(data)

        # log in once for all MoodleMirrors
        if MoodleMirror.session is None:
            MoodleMirror.session = requests.Session()
            self._login()

    @dataclass
    class DataFormat(Mirror.SerializedMirror):
        login_url: str
        page_url: str
        xpath_fmt: str
        login_token_pattern: str
        username: str
        password: str

    def _login(self):
        login_token = self.find_regex(
            self._data.login_token_pattern,
            url=self._data.login_url,
            session=self.session
        )
        if not login_token:
            log.error('could not find logintoken')
            raise self.LoginError('no logintoken')

        log.debug(f'logintoken={login_token}')

        login_form = {
            'username': self._data.username,
            'password': self._data.password,
            'logintoken': login_token
        }

        response = self.session.post(self._data.login_url, data=login_form)
        response.raise_for_status()
        log.debug('logged in successfully')

    def fetch(self) -> (bytes, None):
        xpath = self._data.xpath_fmt.format(n=self.n)
        pdf_url = self.find_xpath(
            xpath,
            url=self._data.page_url,
            session=self.session
        )
        if not pdf_url:
            return None

        pdf = self.session.get(pdf_url)
        pdf.raise_for_status()

        return pdf

@register('ana3')
class AnaMirror(Mirror):
    @dataclass
    class DataFormat(Mirror.SerializedMirror):
        login_url: str
        email: str
        password: str
        link_pattern: str

    def fetch(self) -> (bytes, None):
        with requests.Session() as session:
            response = session.post(url=self._data.login_url, data={
                'email': self._data.email,
                'password': self._data.password
            })

            response.raise_for_status()
            log.debug('ana3: logged in successfully')

            url = self._data.link_pattern.format(n=self.n)
            pdf = session.get(url)
            if pdf.ok:
                log.info(f'found {url}')
                return pdf

            else:
                log.debug(f'ana3: could not find {url}')

@register('ex3')
class ExphyMirror(MoodleMirror):
    pass

@register('astro')
class AstroMirror(MoodleMirror):
    pass

@register('elektro')
class ElektroMirror(MoodleMirror):
    pass

@register('theo3')
class TheoMirror(SimpleLookup):
    pass

@register('ex1')
class Exphy1Mirror(SimpleLookup):
    pass

@register('la')
class TheoMirror(SimpleLookup):
    pass

@register('homa3')
class HoMaMirror(SimpleLookup):
    pass

@register('alg1')
class AlgebraMirror(SimpleLookup):
    pass

@register('stat')
class StatistikMirror(SimpleGet):
    pass

