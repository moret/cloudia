import pytest
from bolacha import Bolacha

def test_home_page_allows_signin():
    b = Bolacha()
    headers, html = b.get('http://0.0.0.0:8888/')

    assert '200' in headers['status']
    assert 'Connect' in html
    assert 'access' in html
    assert 'secret' in html

def test_signin_redirects_and_sets_cookie():
    signin = {
        'access': 'abcdef',
        'secret': 'sdfghj'
    }

    b = Bolacha()
    headers, html = b.post('http://0.0.0.0:8888/signin', signin)

    assert '302' in headers['status']
    assert '/' in headers['location']
    assert 'access=' in headers['set-cookie']
    assert 'secret=' in headers['set-cookie']
