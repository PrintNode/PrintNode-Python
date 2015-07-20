from printnodeapi.model import Model, Client, Account
import json


class Accounts:

    def __init__(self, auth, factory):
        self._auth = auth
        self._factory = factory

    def get_clients(self, client_ids=None, os=None):
        if os:
            url = "/download/client/"+os
            clients = self._factory.create_latest_download(
                self._auth.get(url))
        else:
            client_ids = str(client_ids) if client_ids else ""
            url = "/download/clients/"+client_ids
            clients = self._factory.create_clients(self._auth.get(url))

        return clients

    def modify_client_downloads(self, client_ids, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Incorrect type of enabled, should be bool.')

        response = self._auth.patch(
            "/download/clients/"+str(client_ids),
            {"enabled": enabled})

        return response

    def get_tag(self, tagname):
        tags = self._auth.get('account/tag/'+tagname)

        return tags

    def modify_tag(self, tagname, tagvalue):
        tags = self._auth.post('account/tag/'+tagname, tagvalue)

        return tags

    def delete_tag(self, tagname):
        tags = self._auth.delete('account/tag/'+tagname)

        return tags

    def modify_account(
            self,
            firstname=None,
            lastname=None,
            password=None,
            email=None,
            creator_ref=None
            ):
        mod_data = {}
        if firstname is not None:
            mod_data.update({"firstname": firstname})
        if lastname is not None:
            mod_data.update({"lastname": lastname})
        if password is not None:
            mod_data.update({"password": password})
        if email is not None:
            mod_data.update({"email": email})
        if creator_ref is not None:
            mod_data.update({"creatorRef": creator_ref})
        if not mod_data:
            raise ValueError("No fields selected to be modified, exiting")
        account_id = self._auth.patch('/account', mod_data)
        return account_id

    def create_account(
            self,
            firstname,
            lastname,
            email,
            password,
            creator_ref=None,
            api_keys=None,
            tags=None):

        acc_data = {
                "Account": {
                    "firstname": firstname,
                    "lastname": lastname,
                    "email": email,
                    "password": password}
                }

        if creator_ref is not None:
            acc_data["Account"].update({"creatorRef": creator_ref})

        if api_keys is not None:
            acc_data.update({"ApiKeys": api_keys})

        if tags is not None:
            acc_data.update({"Tags": tags})

        acc_id = self._auth.post('/account', acc_data)

        return acc_id

    def delete_account(
            self,
            ):

        response = self._auth.delete("/account")

        return response

    def delete_api_key(
            self,
            api_key,
            ):

        response = self._auth.delete('account/apikey/'+api_key)

        return response

    def get_api_key(
            self,
            api_key
            ):

        response = self._auth.get("/account/apikey/"+api_key)
        return response

    def create_api_key(
            self,
            api_key,
            ):
        response = self._auth.post("/account/apikey/"+api_key)
        return response

    def get_clientkey(
            self,
            uuid,
            version,
            edition):
        url = "/client/key/"+uuid+"?edition="+edition+"&version="+version
        response = self._auth.get(url, {'Content-Type': 'application/json'})
        return response

    def _get_computer_ids(self, computer):
        if isinstance(computer, int):
            return [computer]
        elif isinstance(computer, Computer):
            return [computer.id]
        elif computer is None or isinstance(computer, str):
            computers = [
                self._factory.create_computer(comp)
                for comp in self._auth.get('/computers')]
            if isinstance(computer, str):
                computers = [
                    comp
                    for comp in computers
                    if comp.name == computer]
            return [c.id for c in computers]
        else:
            raise TypeError('computer: "{}"'.format(type(computer)))

    def _get_computer_id(self, computer):
        return self._get_model_id(computer, Computer)

    def _get_printer_id(self, printer):
        return self._get_model_id(printer, Printer)

    def _get_printjob_id(self, printjob):
        return self._get_model_id(printjob, PrintJob)

    def _get_model_id(self, model, model_type):
        if isinstance(model, int):
            return model
        elif isinstance(model, model_type):
            return model.id
        else:
            raise TypeError(str(type(model)))

    def _get_printer_ids(self, printer):
        if isinstance(printer, int):
            return [printer]
        elif isinstance(printer, Printer):
            return [Printer.id]
        elif printer is None or isinstance(printer, str):
            printers = {
                self._factory.create_printer(printer_dict)
                for printer_dict in self._auth.get('/printer')}
            if isinstance(printer, str):
                printers = {
                    p for p in printers if p.name == printer}
            return printers
        else:
            raise TypeError('printer: "{}"'.format(type(printer)))

    def _is_multi_query(self, obj):
        if obj is None:
            return True
        elif isinstance(obj, int):
            return False
        elif isinstance(obj, str):
            return True
        elif isinstance(obj, Model):
            return False
        else:
            raise TypeError('type "{}" unsupported'.format(type(obj)))

    def _get_printer_by_name(self, printer_name, computer_id=None):
        assert isinstance(printer_name, str)
        assert not computer_id or isinstance(computer_id, int)
        printers = self.get_printers(computer=computer_id)
        return [
            printer
            for printer in printers
            if printer.name == printer_name]


class LookupFailedError(RuntimeError):

    def __init__(self, obj_name, field, value):
        msg = 'Failed to find a matching {} with {} of {}'.format(
            obj_name,
            field,
            value)
        super(RuntimeError, self).__init__(msg)

        self.obj_name = obj_name
        self.field = field
        self.value = value
