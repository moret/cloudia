import pytest
from model import hello_world
from bolacha import Bolacha

def test_hello_world_model_prints_hello_world():
    assert 'Hello World' in hello_world.say()

def test_hello_world_url_returns_hello_world():
    b = Bolacha()
    assert 'Hello World' in b.get('http://0.0.0.0:8888/')[1]
