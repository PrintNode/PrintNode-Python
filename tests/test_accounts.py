import pytest
import requests
import mock
import string
import random
import re
import time

from printnodeapi.gateway import Gateway
from printnodeapi.model import Computer, Printer, PrintJob, State, Account
from printnodeapi.auth import Auth

from fixtures import *

ENTRY_SIZE = 5

def setup_module(module):
    gateway = create_gateway()
    gateway.TestDataGenerate()

def teardown_module(module):
    gateway = create_gateway()
    gateway.TestDataDelete()

@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_create_delete_account(gateway):
    time.sleep(1)
    creator_ref = "a_ref"+get_random_string()
    acc = gateway.CreateAccount(
        firstname="Jake",
        lastname="Torrance",
        email="anemail@emails.emails"+get_random_string(),
        password="password",
        creator_ref=creator_ref,
        tags={"likes": "chicken"})
    assert creator_ref == acc["Account"]["creatorRef"]
    acc_gateway = create_gateway(child_id=acc["Account"]["id"])
    acc_gateway.DeleteAccount()
    with pytest.raises(Exception) as no_account_exception:
        acc_gateway.account
    assert no_account_exception


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_create_api_key(gateway):
    time.sleep(1)
    creator_ref = "a_ref"+get_random_string()
    acc = gateway.CreateAccount(
        firstname="Jake",
        lastname="Torrance",
        email="anemail@emails.emails"+get_random_string(),
        password="password",
        creator_ref=creator_ref,
        tags={"likes": "chicken"})
    acc_gateway = create_gateway(child_id=acc["Account"]["id"])
    acc_gateway.CreateApiKey(api_key=creator_ref)
    assert acc_gateway.account.api_keys[creator_ref]
    acc_gateway.DeleteAccount()


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_api_key(gateway):
    time.sleep(1)
    creator_ref = "a_ref"+get_random_string()
    acc = gateway.CreateAccount(
        firstname="Jake",
        lastname="Torrance",
        email="anemail@emails.emails"+get_random_string(),
        password="password",
        creator_ref=creator_ref,
        tags={"likes": "chicken"})
    acc_gateway = create_gateway(child_id=acc["Account"]["id"])
    acc_gateway.CreateApiKey(api_key=creator_ref)
    apikey = acc_gateway.account.api_keys[creator_ref]
    assert acc_gateway.api_key(api_key=creator_ref) == apikey
    acc_gateway.DeleteAccount()


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_delete_api_key(gateway):
    time.sleep(1)
    creator_ref = "a_ref"+get_random_string()
    acc = gateway.CreateAccount(
        firstname="Jake",
        lastname="Torrance",
        email="anemail@emails.emails"+get_random_string(),
        password="password",
        creator_ref=creator_ref,
        tags={"likes": "chicken"})
    acc_gateway = create_gateway(child_id=acc["Account"]["id"])
    acc_gateway.CreateApiKey(api_key=creator_ref)
    acc_gateway.DeleteApiKey(api_key=creator_ref)
    assert acc_gateway.account.api_keys == []
    acc_gateway.DeleteAccount()


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_create_delete_tag(gateway):
    time.sleep(1)
    gateway.ModifyTag("likes", "chicken")
    assert {"likes": "chicken"} == gateway.account.tags
    gateway.DeleteTag("likes")
    assert [] == gateway.account.tags


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_modify_account(gateway):
    time.sleep(1)
    creator_ref = "a_ref"+get_random_string()
    acc = gateway.CreateAccount(
        firstname="Jake",
        lastname="Torrance",
        email="anemail@emails.emails"+get_random_string(),
        password="password",
        creator_ref=creator_ref,
        tags={"likes": "chicken"})
    acc_gateway = create_gateway(child_id=acc["Account"]["id"])
    acc_gateway.ModifyAccount(firstname="NotJake")
    assert "NotJake" == acc_gateway.account.firstname
    acc_gateway.DeleteAccount()


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_clientkey(gateway):
    time.sleep(1)
    creator_ref = "a_ref"+get_random_string()
    acc = gateway.CreateAccount(
        firstname="Jake",
        lastname="Torrance",
        email="anemail@emails.emails"+get_random_string(),
        password="password",
        creator_ref=creator_ref,
        tags={"likes": "chicken"})
    acc_gateway = create_gateway(child_id=acc["Account"]["id"])
    response = acc_gateway.clientkey(
        uuid="0a756864-602e-428f-a90b-842dee47f57e",
        edition="printnode",
        version="4.7.2")
    regex = re.compile('^ck.*')
    assert regex.match(response) is not None
    acc_gateway.DeleteAccount()


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_clients(gateway):
    time.sleep(1)
    all_clis = gateway.clients()
    assert all_clis[0].edition == "tyrell"
    some_clis = gateway.clients(client_ids="10-15")
    ver10 = False
    ver15 = False
    for v in some_clis:
        if v.id == 10:
            ver10 = True
        elif v.id == 15:
            ver15 = True
    assert ver10 and ver15
    recent_cli = gateway.clients(os="windows")
    assert recent_cli.os == "windows"


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_modify_downloads(gateway):
    time.sleep(1)
    gateway.ModifyClientDownloads(17, False)
    cli_17 = gateway.clients(client_ids="17")
    assert not cli_17[0].enabled
