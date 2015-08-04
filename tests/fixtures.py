import pytest
import requests
import mock
import string
import random
import re
import time

from credentials import *
from printnodeapi.gateway import Gateway
from printnodeapi.model import Computer, Printer, PrintJob, State, Account
from printnodeapi.auth import Auth

API_ADDRESS = API_ADDRESS
API_KEY = API_KEY

ENTRY_SIZE = 5


@pytest.fixture
def get_random_string(size=6, chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@pytest.fixture(autouse=True)
def patch_auth_for_throttling(request):
    patcher = mock.patch('printnodeapi.gateway.Auth')
    AuthMock = patcher.start()
    request.addfinalizer(patcher.stop)

    def create_auth(*args, **kwargs):
        auth = Auth(*args, **kwargs)
        return auth

    AuthMock.side_effect = create_auth


@pytest.fixture
def create_gateway(child_id=None):
    if child_id:
        gateway = Gateway(
            url=API_ADDRESS,
            apikey=API_KEY,
            child_id=child_id)
    else:
        gateway = Gateway(url=API_ADDRESS, apikey=API_KEY)
    return gateway
