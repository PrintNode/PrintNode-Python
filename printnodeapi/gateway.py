import json

import requests

from .auth import Auth, Unauthorized
from .model import ModelFactory
from .accounts import Accounts
from .computers import Computers
from .util import camel_to_underscore


class Gateway:

    URL = 'https://api.printnode.com'

    def __init__(self, **kwargs):
        url = kwargs.pop('url', self.URL)
        self._auth = Auth(url=url, **kwargs)
        self._factory = ModelFactory()
        self._accounts = Accounts(self._auth, self._factory)
        self._computers = Computers(self._auth, self._factory)

    @property
    def account(self):
        server_account = self._auth.get('whoami')
        return self._factory.create_account(server_account)

    @property
    def computers(self):
        return self._computers.get_computers

    @property
    def printers(self):
        return self._computers.get_printers

    @property
    def printjobs(self):
        return self._computers.get_printjobs

    @property
    def scales(self):
        return self._computers.get_scales

    @property
    def tag(self):
        return self._accounts.get_tag

    @property
    def api_key(self):
        return self._accounts.get_api_key

    @property
    def clientkey(self):
        return self._accounts.get_clientkey

    @property
    def clients(self):
        return self._accounts.get_clients

    @property
    def states(self):
        return self._computers.get_states

    def PrintJob(self, *args, **kwargs):
        printjob_id = self._computers.submit_printjob(*args, **kwargs)
        printjob = self.printjobs(printjob=printjob_id)
        return printjob

    def TestDataGenerate(self):
        self._auth.get('test/data/generate')

    def TestDataDelete(self):
        self._auth.delete('test/data/generate')

    def ModifyTag(self, tagname, tagvalue):
        tag = self._accounts.modify_tag(tagname, tagvalue)
        return tag

    def DeleteTag(self, tagname):
        tag = self._accounts.delete_tag(tagname)
        return tag

    def CreateAccount(self, **kwargs):
        acc_post = self._accounts.create_account(**kwargs)
        return acc_post

    def ModifyAccount(self, **kwargs):
        acc_id = self._accounts.modify_account(**kwargs)
        return self._factory.create_account(acc_id)

    def DeleteAccount(self, **kwargs):
        boolean = self._accounts.delete_account(**kwargs)
        return boolean

    def DeleteApiKey(self, api_key):
        key = self._accounts.delete_api_key(api_key)
        return key

    def CreateApiKey(self, api_key):
        key = self._accounts.create_api_key(api_key)
        return key

    def ModifyClientDownloads(self, client_id, enabled):
        clients = self._accounts.modify_client_downloads(client_id, enabled)
        return clients
