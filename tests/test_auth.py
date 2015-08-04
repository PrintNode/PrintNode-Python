import pytest
import time

from printnodeapi.gateway import Gateway, Unauthorized
from printnodeapi.model import Account
from credentials import *

API_ADDRESS = API_ADDRESS


def test_gateway():
    time.sleep(1)
    gateway = Gateway(url=API_ADDRESS, apikey=API_KEY)
    assert YOUR_NAME == gateway.account.firstname


def test_gateway_handles_unauthentication():
    time.sleep(1)
    gateway = Gateway(
        url=API_ADDRESS,
        email='fake@omlet.co.uk',
        password='helloworld')
    with pytest.raises(Unauthorized):
        gateway.account
